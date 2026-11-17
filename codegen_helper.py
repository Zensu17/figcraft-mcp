#!/usr/bin/env python3
"""
FigCraft UI AST Cleaner & Token Extractor
------------------------------------------
Extracts semantic design tokens from FigCraft node trees, stripping noisy absolute
coordinates and internal metadata to produce compact, high-signal UI tokens for AI codegen.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BRIDGE_PATH = SCRIPT_DIR / "bridge.py"


def clean_node(node: dict) -> dict:
    """Recursively clean and extract semantic UI tokens from a FigCraft node."""
    if not isinstance(node, dict):
        return {}

    node_type = (node.get("type") or "frame").lower()
    name = node.get("name", "")

    cleaned = {
        "type": node_type,
        "name": name,
    }

    # Dimensions
    if "width" in node:
        cleaned["w"] = round(node["width"])
    if "height" in node:
        cleaned["h"] = round(node["height"])

    # Corner Radius
    radius = node.get("cornerRadius")
    if radius:
        cleaned["rounded"] = round(radius)

    # Fills (Background Color)
    fills = node.get("fills", [])
    if fills and isinstance(fills, list):
        for f in fills:
            if isinstance(f, dict) and f.get("type") == "solid" and "color" in f:
                cleaned["bg"] = f["color"]
                break

    # Auto Layout properties
    layout = node.get("layout")
    if layout:
        # FigCraft engine stores layout as a dict: {"mode": "vertical"|"horizontal", "gap": float, "padding": [...], ...}
        if isinstance(layout, dict):
            mode = layout.get("mode", "vertical")
            cleaned["direction"] = "col" if mode == "vertical" else "row"
            if "gap" in layout:
                cleaned["gap"] = round(layout["gap"])
            if "padding" in layout:
                p_val = layout["padding"]
                if isinstance(p_val, list) and p_val:
                    cleaned["p"] = round(p_val[0])
                elif isinstance(p_val, (int, float)):
                    cleaned["p"] = round(p_val)
            align_map = {"min": "start", "max": "end", "start": "start", "end": "end", "center": "center", "spaceBetween": "between", "space-between": "between"}
            if "mainAlign" in layout:
                cleaned["justify"] = align_map.get(layout["mainAlign"], layout["mainAlign"])
            if "crossAlign" in layout:
                cleaned["items"] = align_map.get(layout["crossAlign"], layout["crossAlign"])
        else:
            cleaned["direction"] = "col" if str(layout).lower() == "vertical" else "row"
            if "gap" in node:
                cleaned["gap"] = round(node["gap"])
            if "padding" in node:
                p_val = node["padding"]
                cleaned["p"] = round(p_val[0]) if isinstance(p_val, list) else round(p_val)
            align_map = {"min": "start", "max": "end", "start": "start", "end": "end", "center": "center", "spaceBetween": "between", "space-between": "between"}
            if "mainAlign" in node:
                cleaned["justify"] = align_map.get(node["mainAlign"], node["mainAlign"])
            if "crossAlign" in node:
                cleaned["items"] = align_map.get(node["crossAlign"], node["crossAlign"])

    # Strokes / Borders
    strokes = node.get("strokes", [])
    if strokes and isinstance(strokes, list):
        for s in strokes:
            if isinstance(s, dict) and s.get("type") == "solid" and "color" in s:
                cleaned["borderColor"] = s["color"]
                break
    elif node.get("stroke") and isinstance(node["stroke"], str):
        cleaned["borderColor"] = node["stroke"]

    stroke_weight = node.get("strokeWeight") or node.get("strokeWidth")
    if stroke_weight:
        cleaned["borderWidth"] = round(stroke_weight)

    # Typography / Text layer
    if node_type == "text" or "text" in node or "characters" in node:
        cleaned["text"] = node.get("characters") or node.get("text", "")
        if "fontSize" in node:
            cleaned["fontSize"] = round(node["fontSize"])
        if "fontStyle" in node:
            cleaned["fontStyle"] = node["fontStyle"]
        # Text color from fills
        if "bg" in cleaned:
            cleaned["color"] = cleaned.pop("bg")

    # Children
    children = node.get("children", [])
    if children and isinstance(children, list):
        cleaned_children = [clean_node(c) for c in children if isinstance(c, dict)]
        if cleaned_children:
            cleaned["children"] = cleaned_children

    return cleaned


def query_figcraft_node(node_id: int = None) -> dict:
    """Connect to FigCraft via MCP bridge and fetch a specific node or active document."""
    proc = subprocess.Popen(
        [sys.executable, str(BRIDGE_PATH)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    def send_rpc(method, params, req_id):
        req = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
        proc.stdin.write(json.dumps(req) + "\n")
        proc.stdin.flush()
        line = proc.stdout.readline()
        return json.loads(line)

    try:
        # 1. Initialize
        send_rpc(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "codegen-helper", "version": "1.0"},
            },
            1,
        )
        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()

        # 2. Call get_node or inspect_document
        if node_id is not None:
            res = send_rpc("tools/call", {"name": "get_node", "arguments": {"id": node_id}}, 2)
        else:
            res = send_rpc("tools/call", {"name": "inspect_document", "arguments": {}}, 2)

        if res.get("result", {}).get("isError"):
            err_msg = res["result"]["content"][0]["text"]
            sys.stderr.write(f"[FigCraft Error] {err_msg}\n")
            return {}

        content_items = res.get("result", {}).get("content", [])
        if content_items and content_items[0].get("type") == "text":
            try:
                data = json.loads(content_items[0]["text"])
                return data.get("node", data)
            except Exception as e:
                sys.stderr.write(f"[Parse Error] {e}\n")
                return {}
        return {}
    finally:
        proc.terminate()


def run_self_test():
    """Unit test verifying that FigCraft AST is cleaned and compressed properly."""
    raw_sample = {
        "id": 57,
        "name": "Simple Weather Widget",
        "type": "FRAME",
        "absoluteBounds": {"x": 100.0, "y": 640.0, "width": 280.0, "height": 190.0},
        "width": 280.0,
        "height": 190.0,
        "cornerRadius": 20.0,
        "layout": "vertical",
        "gap": 10.0,
        "padding": 20.0,
        "fills": [{"type": "solid", "color": "#1E293B"}],
        "children": [
            {
                "id": 58,
                "name": "Location",
                "type": "TEXT",
                "text": "Jakarta, Indonesia",
                "fontSize": 12.0,
                "fills": [{"type": "solid", "color": "#94A3B8"}],
                "absoluteBounds": {"x": 120.0, "y": 660.0, "width": 120.0, "height": 16.0},
            }
        ],
    }

    cleaned = clean_node(raw_sample)
    assert cleaned["type"] == "frame"
    assert cleaned["direction"] == "col"
    assert cleaned["gap"] == 10
    assert cleaned["p"] == 20
    assert cleaned["bg"] == "#1E293B"
    assert len(cleaned["children"]) == 1
    child = cleaned["children"][0]
    assert child["type"] == "text"
    assert child["text"] == "Jakarta, Indonesia"
    assert child["color"] == "#94A3B8"

    raw_len = len(json.dumps(raw_sample))
    clean_len = len(json.dumps(cleaned))
    reduction = ((raw_len - clean_len) / raw_len) * 100
    print(f"[PASS] Self-test passed! AST Cleaned successfully ({reduction:.1f}% token reduction)")
    return True


def main():
    parser = argparse.ArgumentParser(description="FigCraft AST Cleaner for Codegen")
    parser.add_argument("--node", type=int, help="Fetch and clean node by ID from FigCraft canvas")
    parser.add_argument("--doc", action="store_true", help="Fetch and inspect the active document")
    parser.add_argument("--file", type=str, help="Read and clean FigCraft node from a JSON file")
    parser.add_argument("--test", action="store_true", help="Run internal self-test")
    args = parser.parse_args()

    if args.test:
        run_self_test()
        return

    if args.node is not None:
        raw_node = query_figcraft_node(args.node)
        if raw_node:
            cleaned = clean_node(raw_node)
            print(json.dumps(cleaned, indent=2))
        return

    if args.doc:
        raw_doc = query_figcraft_node(None)
        if raw_doc:
            print(json.dumps(raw_doc, indent=2))
        return

    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            raw_node = json.load(f)
        cleaned = clean_node(raw_node)
        print(json.dumps(cleaned, indent=2))
        return

    # Default: read stdin
    input_data = sys.stdin.read().strip()
    if input_data:
        raw_node = json.loads(input_data)
        cleaned = clean_node(raw_node)
        print(json.dumps(cleaned, indent=2))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
