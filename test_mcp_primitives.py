#!/usr/bin/env python3
"""
Verification Suite for FigCraft MCP Primitives Middleware
---------------------------------------------------------
Covers both unit tests (normalizer guardrails, resource/prompt rendering,
list merging) and end-to-end stdio JSON-RPC 2.0 tests against bridge.py.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import mcp_primitives

BRIDGE_PATH = SCRIPT_DIR / "bridge.py"


def test_input_normalization_guardrails() -> None:
    # 1. create_node normalization
    raw_create = {
        "name": "create_node",
        "arguments": {
            "type": "frame",
            "props": {
                "stroke": "#334155",
                "strokeWidth": 2,
                "mainAlign": "space-between",
                "crossAlign": "start",
                "fontWeight": 700,
            },
        },
    }
    norm = mcp_primitives.normalize_tool_call_params(raw_create)
    props = norm["arguments"]["props"]
    assert "strokeWidth" not in props
    assert props["strokeWeight"] == 2
    assert props["mainAlign"] == "spaceBetween"
    assert props["crossAlign"] == "min"
    assert "fontWeight" not in props
    assert props["fontStyle"] == "Bold"
    # Verify original input was not mutated
    assert raw_create["arguments"]["props"]["strokeWidth"] == 2

    # 2. batch normalization
    raw_batch = {
        "name": "batch",
        "arguments": {
            "commands": [
                {
                    "command": "node.create",
                    "as": "card",
                    "params": {
                        "type": "frame",
                        "strokeWidth": 1,
                        "mainAlign": "end",
                        "crossAlign": "end",
                    },
                },
                {
                    "command": "node.create",
                    "params": {
                        "type": "text",
                        "text": "Hello",
                        "props": {"fontWeight": "600"},
                    },
                },
            ]
        },
    }
    norm_batch = mcp_primitives.normalize_tool_call_params(raw_batch)
    step0 = norm_batch["arguments"]["commands"][0]["params"]
    step1 = norm_batch["arguments"]["commands"][1]["params"]["props"]
    assert step0["strokeWeight"] == 1
    assert step0["mainAlign"] == "max"
    assert step0["crossAlign"] == "max"
    assert step1["fontStyle"] == "SemiBold"
    print("  [PASS] Input normalization guardrails (create_node, batch)")


def test_uri_classification() -> None:
    assert mcp_primitives.is_live_canvas_uri("figcraft://document") is True
    assert mcp_primitives.is_live_canvas_uri("figcraft://comments") is True
    assert mcp_primitives.is_live_canvas_uri("figcraft://node/42") is True
    assert mcp_primitives.is_live_canvas_uri("figcraft://node/42/semantic") is True
    assert mcp_primitives.is_live_canvas_uri("figcraft://canvas/semantic") is True

    assert mcp_primitives.is_live_canvas_uri("figcraft://tokens") is False
    assert mcp_primitives.is_live_canvas_uri("figcraft://guidelines") is False
    assert mcp_primitives.is_live_canvas_uri("figcraft://commands") is False
    assert mcp_primitives.is_custom_resource_uri("figcraft://node/42/semantic") is True
    assert mcp_primitives.is_custom_resource_uri("figcraft://node/42") is False
    print("  [PASS] URI classification (live-canvas vs static local)")


def test_custom_prompt_rendering_and_validation() -> None:
    res = mcp_primitives.handle_custom_prompt_get(
        "figcraft_dashboard_card",
        {"metric_name": "MRR", "metric_value": "$42,000", "trend": "+9.2%", "theme": "dark"},
    )
    text = res["messages"][0]["content"]["text"]
    assert "MRR" in text
    assert "$42,000" in text
    assert "fill 'none'" in text
    assert "strokeWeight 1" in text

    # Missing required arg must raise ValueError
    try:
        mcp_primitives.handle_custom_prompt_get("figcraft_dashboard_card", {"metric_name": "MRR"})
        raise AssertionError("Expected ValueError for missing metric_value")
    except ValueError as exc:
        assert "metric_value" in str(exc)

    # Design-to-code prompt
    d2c = mcp_primitives.handle_custom_prompt_get(
        "figcraft_design_to_code", {"node_id": "125", "framework": "flutter"}
    )
    assert "figcraft_generate_code" in d2c["messages"][0]["content"]["text"]
    assert "flutter" in d2c["messages"][0]["content"]["text"]

    # Mocked figcraft_generate_code tool verification (code & json & validation)
    def mock_upstream(method: str, params: dict[str, Any]) -> dict[str, Any]:
        assert method == "tools/call" and params["name"] == "get_node"
        sample = {
            "id": 99,
            "name": "Primary Button",
            "type": "FRAME",
            "cornerRadius": 8,
            "layout": {"mode": "horizontal", "padding": [12, 20, 12, 20], "mainAlign": "center", "crossAlign": "center"},
            "fills": [{"type": "solid", "color": "#4F46E5"}],
            "children": [
                {"id": 100, "name": "Label", "type": "TEXT", "characters": "Deploy Now", "fontSize": 14, "fontStyle": "SemiBold", "fills": [{"type": "solid", "color": "#FFFFFF"}]}
            ],
        }
        return {"result": {"content": [{"type": "text", "text": json.dumps({"node": sample})}]}}

    gen_code = mcp_primitives.handle_custom_tool_call(
        "figcraft_generate_code",
        {"node_id": 99, "framework": "react-tailwind", "response_format": "json"},
        mock_upstream,
    )
    assert gen_code.get("isError") is not True
    gen_payload = json.loads(gen_code["content"][0]["text"])
    assert gen_payload["component_name"] == "PrimaryButton"
    assert '<button type="button"' in gen_payload["code"]
    assert "bg-indigo-600" in gen_payload["code"]

    gen_bad_fw = mcp_primitives.handle_custom_tool_call(
        "figcraft_generate_code",
        {"node_id": 99, "framework": "angular"},
        mock_upstream,
    )
    assert gen_bad_fw.get("isError") is True
    print("  [PASS] Custom prompt rendering & figcraft_generate_code tool")


def test_bridge_e2e_stdio() -> None:
    proc = subprocess.Popen(
        [sys.executable, str(BRIDGE_PATH)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    def rpc(method: str, params: dict[str, Any], req_id: int) -> dict[str, Any]:
        assert proc.stdin and proc.stdout
        proc.stdin.write(
            json.dumps({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}) + "\n"
        )
        proc.stdin.flush()
        line = proc.stdout.readline()
        assert line, f"Empty stdout response for {method}"
        return json.loads(line)

    try:
        # 1. Initialize & enriched instructions
        init = rpc(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "mcp-primitives-test", "version": "1.0"},
            },
            1,
        )
        assert "result" in init
        instructions = init["result"].get("instructions", "")
        assert "[FigCraft Bridge Primitives & Engine Rules]" in instructions
        assert 'fill: "none"' in instructions

        assert proc.stdin
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()

        # 2. tools/list merged
        tools_res = rpc("tools/list", {}, 2)
        tools = {t["name"]: t for t in tools_res["result"]["tools"]}
        assert "create_node" in tools
        assert "figcraft_get_tokens" in tools
        assert "figcraft_extract_semantic_ast" in tools
        assert "figcraft_generate_code" in tools
        assert tools["figcraft_get_tokens"]["annotations"]["readOnlyHint"] is True
        assert tools["figcraft_extract_semantic_ast"]["annotations"]["readOnlyHint"] is True
        assert tools["figcraft_generate_code"]["annotations"]["readOnlyHint"] is True

        # 3. resources/list merged
        res_list = rpc("resources/list", {}, 3)
        uris = {r["uri"] for r in res_list["result"]["resources"]}
        assert {"figcraft://document", "figcraft://tokens", "figcraft://guidelines", "figcraft://canvas/semantic"} <= uris

        # 4. resources/templates/list merged
        tmpl_list = rpc("resources/templates/list", {}, 4)
        tmpls = {t["uriTemplate"] for t in tmpl_list["result"]["resourceTemplates"]}
        assert "figcraft://node/{id}" in tmpls
        assert "figcraft://node/{id}/semantic" in tmpls

        # 5. prompts/list merged
        prompts_res = rpc("prompts/list", {}, 5)
        prompt_names = {p["name"] for p in prompts_res["result"]["prompts"]}
        assert {
            "mobile_screen",
            "figcraft_dashboard_card",
            "figcraft_auth_screen",
            "figcraft_navbar",
            "figcraft_design_to_code",
        } <= prompt_names

        # 6. resources/read static local resources (figcraft://tokens & figcraft://guidelines)
        tokens_read = rpc("resources/read", {"uri": "figcraft://tokens"}, 6)
        tokens_json = json.loads(tokens_read["result"]["contents"][0]["text"])
        assert "colors" in tokens_json and "indigo" in tokens_json["colors"]

        guidelines_read = rpc("resources/read", {"uri": "figcraft://guidelines"}, 7)
        guidelines_md = guidelines_read["result"]["contents"][0]["text"]
        assert "strokeWeight" in guidelines_md

        # 7. prompts/get custom + invalid params check
        prompt_get = rpc(
            "prompts/get",
            {
                "name": "figcraft_navbar",
                "arguments": {"brand_name": "BuddyBuild", "theme": "dark"},
            },
            8,
        )
        assert "BuddyBuild" in prompt_get["result"]["messages"][0]["content"]["text"]

        prompt_err = rpc("prompts/get", {"name": "figcraft_navbar", "arguments": {}}, 9)
        assert "error" in prompt_err and prompt_err["error"]["code"] == -32602

        # 8. tools/call local-only figcraft_get_tokens (json & markdown & error)
        tok_tool_json = rpc(
            "tools/call",
            {"name": "figcraft_get_tokens", "arguments": {"category": "radius", "response_format": "json"}},
            10,
        )
        radius_data = json.loads(tok_tool_json["result"]["content"][0]["text"])
        assert radius_data["radius"]["xl"] == 12

        tok_tool_md = rpc(
            "tools/call",
            {"name": "figcraft_get_tokens", "arguments": {"category": "spacing", "response_format": "markdown"}},
            11,
        )
        assert "## spacing" in tok_tool_md["result"]["content"][0]["text"]

        tok_tool_bad = rpc(
            "tools/call",
            {"name": "figcraft_get_tokens", "arguments": {"category": "invalid_cat"}},
            12,
        )
        assert tok_tool_bad["result"].get("isError") is True

        # 9. Invalid node ID on semantic resource template returns -32602
        bad_node_uri = rpc("resources/read", {"uri": "figcraft://node/not-a-num/semantic"}, 13)
        assert "error" in bad_node_uri and bad_node_uri["error"]["code"] == -32602

        # 10. Live canvas semantic AST via resource & tool
        canvas_sem = rpc("resources/read", {"uri": "figcraft://canvas/semantic"}, 14)
        canvas_json = json.loads(canvas_sem["result"]["contents"][0]["text"])
        assert "document" in canvas_json and "pages" in canvas_json

        ast_tool_md = rpc(
            "tools/call",
            {"name": "figcraft_extract_semantic_ast", "arguments": {"response_format": "markdown"}},
            15,
        )
        assert ast_tool_md["result"].get("isError") is not True
        assert "# Document:" in ast_tool_md["result"]["content"][0]["text"]

        print(
            f"  [PASS] Bridge E2E stdio verified: "
            f"{len(tools)} tools, {len(uris)} resources, {len(tmpls)} templates, {len(prompt_names)} prompts"
        )
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()


def main() -> None:
    print("Running FigCraft MCP Primitives Verification Suite...")
    test_input_normalization_guardrails()
    test_uri_classification()
    test_custom_prompt_rendering_and_validation()
    test_bridge_e2e_stdio()
    print("\nAll MCP Primitives tests passed.")


if __name__ == "__main__":
    main()
