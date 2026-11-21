#!/usr/bin/env python3
"""
Security Hardening, Mock Socket & Bridge Reliability Test Suite
---------------------------------------------------------------
Follows TDD (RED -> GREEN -> REFACTOR) and STRIDE threat model controls:
- Input boundary validation (JSON-RPC size, depth, batch limits, port bounds)
- Path safety (UNC path blocking, null-byte rejection, traversal/allowlist root checks)
- Codegen output hardening (CSS/HTML/JSX attribute injection, Vue mustache injection, Dart hex safety)
- Bridge reliability (real ephemeral loopback TCP socket check, mocked upstream stdio without GUI)
"""

from __future__ import annotations

import io
import json
import os
import socket
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import bridge
import codegen_helper
import security


class TestSecurityValidation(unittest.TestCase):
    def test_validate_port_accepts_valid_unprivileged_ports(self) -> None:
        self.assertEqual(security.validate_port(1984), 1984)
        self.assertEqual(security.validate_port("8080"), 8080)
        self.assertEqual(security.validate_port(65535), 65535)

    def test_validate_port_rejects_privileged_and_out_of_range_ports(self) -> None:
        for bad in (0, -1, 80, 443, 1023, 65536, "abc", None):
            with self.assertRaises(ValueError, msg=f"Port {bad!r} should be rejected"):
                security.validate_port(bad)

    def test_validate_hex_color_accepts_valid_hex(self) -> None:
        self.assertEqual(security.validate_hex_color("#0F172A"), "#0F172A")
        self.assertEqual(security.validate_hex_color("#fff"), "#fff")
        self.assertEqual(security.validate_hex_color("#1E293BCC"), "#1E293BCC")

    def test_validate_hex_color_rejects_injection_payloads(self) -> None:
        payloads = [
            '#000" onclick="alert(1)',
            "#000; } </style><script>alert(1)</script>",
            "javascript:alert(1)",
            "#ZZZZZZ",
            "rgb(0,0,0)",
            "",
        ]
        for bad in payloads:
            self.assertIsNone(security.validate_hex_color(bad), f"Payload should be rejected: {bad}")

    def test_validate_file_path_blocks_unc_null_and_traversal(self) -> None:
        dangerous = [
            r"\\attacker.example\share\leak.figcraft",
            "//attacker.example/share/leak.figcraft",
            "design\x00.figcraft",
            "../../../Windows/System32/drivers/etc/hosts",
            r"..\..\secret.txt",
            "   ",
        ]
        for bad in dangerous:
            with self.assertRaises(ValueError, msg=f"Dangerous path should be rejected: {bad!r}"):
                security.validate_file_path(bad)

    def test_validate_file_path_enforces_allowed_roots_when_configured(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            inside = root / "designs" / "app.figcraft"
            outside = root.parent / "outside.figcraft"

            validated = security.validate_file_path(str(inside), allowed_roots=[root])
            self.assertEqual(validated, inside)

            with self.assertRaises(ValueError):
                security.validate_file_path(str(outside), allowed_roots=[root])

    def test_validate_rpc_message_blocks_oversized_and_deep_payloads(self) -> None:
        huge = "x" * (security.MAX_RPC_LINE_BYTES + 10)
        with self.assertRaises(ValueError):
            security.validate_raw_line_size(huge)

        deep: Any = "leaf"
        for _ in range(security.MAX_JSON_DEPTH + 5):
            deep = {"nested": deep}
        with self.assertRaises(ValueError):
            security.validate_json_depth(deep)

    def test_validate_tool_call_security_blocks_batch_flood_and_unc_file_ops(self) -> None:
        # Excessive batch commands
        too_many = {"name": "batch", "arguments": {"commands": [{"command": "node.create"}] * (security.MAX_BATCH_COMMANDS + 1)}}
        with self.assertRaises(ValueError):
            security.validate_tool_call_security(too_many)

        # UNC path in open_file
        unc_open = {"name": "open_file", "arguments": {"path": r"\\evil\share\payload.fig"}}
        with self.assertRaises(ValueError):
            security.validate_tool_call_security(unc_open)

        # UNC path nested inside batch step
        unc_batch = {
            "name": "batch",
            "arguments": {
                "commands": [
                    {"command": "file.save", "params": {"path": "//evil/share/out.fig"}}
                ]
            },
        }
        with self.assertRaises(ValueError):
            security.validate_tool_call_security(unc_batch)

        # Safe normal create_node passes
        safe = {"name": "create_node", "arguments": {"type": "frame", "name": "Card"}}
        security.validate_tool_call_security(safe)

    def test_sanitize_log_message_strips_crlf_log_injection(self) -> None:
        dirty = "normal info\r\n[FAKE] elevated=true\x00"
        cleaned = security.sanitize_log_message(dirty)
        self.assertNotIn("\n", cleaned)
        self.assertNotIn("\r", cleaned)
        self.assertNotIn("\x00", cleaned)


class TestCodegenOutputHardening(unittest.TestCase):
    def test_react_and_vue_strip_malicious_color_attribute_injection(self) -> None:
        malicious_ast = {
            "type": "frame",
            "name": "Card",
            "direction": "col",
            "bg": '#000" onClick="alert(1)',
            "borderColor": "#111; } body{display:none}",
            "children": [
                {
                    "type": "text",
                    "name": "Body",
                    "text": "{{ constructor.constructor('alert(1)')() }}",
                    "fontSize": 14,
                    "color": "#FFF' onmouseover='x",
                }
            ],
        }

        react_code = codegen_helper.generate_code(malicious_ast, framework="react-tailwind", include_props=False)["code"]
        self.assertNotIn("onClick", react_code)
        self.assertNotIn("onmouseover", react_code)

        vue_code = codegen_helper.generate_code(malicious_ast, framework="vue", include_props=False)["code"]
        self.assertNotIn("onClick", vue_code)
        self.assertNotIn("{{ constructor", vue_code)

    def test_html_css_blocks_style_breakout_xss(self) -> None:
        malicious_ast = {
            "type": "frame",
            "name": "Card",
            "bg": "#000; } </style><script>alert(1)</script>",
            "children": [
                {
                    "type": "text",
                    "name": "Title",
                    "text": "<img src=x onerror=alert(1)>",
                    "color": "#FFF; } </style><svg onload=alert(1)>",
                }
            ],
        }

        html_code = codegen_helper.generate_code(malicious_ast, framework="html-css")["code"]
        self.assertNotIn("<script>", html_code)
        self.assertNotIn("<svg", html_code)
        self.assertNotIn("<img ", html_code)
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", html_code)

    def test_flutter_rejects_non_hex_colors_safely(self) -> None:
        bad_ast = {
            "type": "frame",
            "name": "Card",
            "bg": "#ZZZZZZ",
            "children": [
                {"type": "text", "name": "Note", "text": "Price $100 'quoted'", "color": "not-a-color"}
            ],
        }
        dart_code = codegen_helper.generate_code(bad_ast, framework="flutter", include_props=False)["code"]
        self.assertNotIn("0xFFZZZZZZ", dart_code)
        self.assertIn(r"Price \$100 \'quoted\'", dart_code)


class TestBridgeSocketAndMockedMiddleware(unittest.TestCase):
    def test_is_port_open_against_real_ephemeral_loopback_socket(self) -> None:
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.bind(("127.0.0.1", 0))
        srv.listen(1)
        port = srv.getsockname()[1]
        try:
            self.assertTrue(bridge.is_port_open("127.0.0.1", port))
        finally:
            srv.close()

        # After closing, connection must be refused
        self.assertFalse(bridge.is_port_open("127.0.0.1", port))

    def test_bridge_blocks_malformed_json_and_unc_tool_without_launching_gui(self) -> None:
        b = bridge.LazyMcpBridge(gui_path=None, cli_path=Path("fake-cli"), port=1984)
        client_out: list[dict[str, Any]] = []
        upstream_out: list[Any] = []
        attached_called = [False]

        def fake_write_client(payload: Any) -> None:
            client_out.append(payload if isinstance(payload, dict) else json.loads(payload))

        def fake_write_upstream(payload: Any) -> None:
            upstream_out.append(payload)

        def fake_transition() -> None:
            attached_called[0] = True
            b.is_attached = True

        b._write_client = fake_write_client  # type: ignore[method-assign]
        b._write_upstream = fake_write_upstream  # type: ignore[method-assign]
        b.transition_to_attached = fake_transition  # type: ignore[method-assign]

        # 1. Malformed JSON returns JSON-RPC Parse Error -32700, never forwarded upstream
        b._handle_client_message("{broken json\n")
        self.assertEqual(client_out[-1]["error"]["code"], -32700)
        self.assertEqual(len(upstream_out), 0)

        # 2. Local-only tool figcraft_get_tokens does NOT attach GUI
        b._handle_client_message(
            json.dumps({
                "jsonrpc": "2.0",
                "id": 10,
                "method": "tools/call",
                "params": {"name": "figcraft_get_tokens", "arguments": {"category": "radius"}},
            })
        )
        self.assertFalse(attached_called[0])
        self.assertIn("radius", client_out[-1]["result"]["content"][0]["text"])

        # 3. UNC path in open_file blocked BEFORE transitioning to GUI or calling upstream
        b._handle_client_message(
            json.dumps({
                "jsonrpc": "2.0",
                "id": 11,
                "method": "tools/call",
                "params": {"name": "open_file", "arguments": {"path": r"\\evil\share\a.fig"}},
            })
        )
        self.assertFalse(attached_called[0])
        self.assertTrue(client_out[-1]["result"]["isError"])
        self.assertEqual(len(upstream_out), 0)

        # 4. Oversized message rejected with -32600 Invalid Request
        b._handle_client_message(" " * (security.MAX_RPC_LINE_BYTES + 20))
        self.assertEqual(client_out[-1]["error"]["code"], -32600)
        self.assertEqual(len(upstream_out), 0)

        # 5. Live resource read triggers lazy attach
        b._handle_client_message(
            json.dumps({
                "jsonrpc": "2.0",
                "id": 12,
                "method": "resources/read",
                "params": {"uri": "figcraft://document"},
            })
        )
        self.assertTrue(attached_called[0])
        self.assertEqual(len(upstream_out), 1)


if __name__ == "__main__":
    unittest.main()
