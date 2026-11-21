#!/usr/bin/env python3
"""
Unified Headless Unit Test Suite (No FigCraft GUI Required)
-----------------------------------------------------------
Covers mcp_primitives, codegen_helper, and tokens modules via stdlib unittest.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import codegen_helper
import mcp_primitives
import tokens


class TestMcpPrimitivesUnit(unittest.TestCase):
    def test_normalizer_rewrites_common_llm_property_typos(self) -> None:
        raw = {
            "name": "create_node",
            "arguments": {
                "type": "frame",
                "props": {
                    "strokeWidth": 2,
                    "mainAlign": "space-between",
                    "crossAlign": "end",
                    "fontWeight": 700,
                },
            },
        }
        norm = mcp_primitives.normalize_tool_call_params(raw)
        props = norm["arguments"]["props"]
        self.assertEqual(props["strokeWeight"], 2)
        self.assertNotIn("strokeWidth", props)
        self.assertEqual(props["mainAlign"], "spaceBetween")
        self.assertEqual(props["crossAlign"], "max")
        self.assertEqual(props["fontStyle"], "Bold")
        self.assertNotIn("fontWeight", props)

    def test_merge_helpers_deduplicate_entries(self) -> None:
        base_tools = {"tools": [{"name": "create_node"}, {"name": "figcraft_get_tokens"}]}
        merged = mcp_primitives.merge_tools_list(base_tools)
        names = [t["name"] for t in merged["tools"]]
        self.assertEqual(names.count("figcraft_get_tokens"), 1)
        self.assertIn("figcraft_extract_semantic_ast", names)
        self.assertIn("figcraft_generate_code", names)
        self.assertIn("figcraft_render_template", names)

    def test_custom_resources_read_tokens_and_guidelines(self) -> None:
        def unused_upstream(_m: str, _p: dict[str, Any]) -> dict[str, Any]:
            raise AssertionError("Static local resource must not call upstream")

        tok_res = mcp_primitives.handle_custom_resource_read("figcraft://tokens", unused_upstream)
        data = json.loads(tok_res["contents"][0]["text"])
        self.assertIn("themes", data)
        self.assertIn("semantic", data)

        guide_res = mcp_primitives.handle_custom_resource_read("figcraft://guidelines", unused_upstream)
        self.assertIn("strokeWeight", guide_res["contents"][0]["text"])

    def test_node_semantic_resource_rejects_non_numeric_id(self) -> None:
        def unused_upstream(_m: str, _p: dict[str, Any]) -> dict[str, Any]:
            return {}

        with self.assertRaises(ValueError):
            mcp_primitives.handle_custom_resource_read("figcraft://node/bad/semantic", unused_upstream)


class TestDesignSystemAndCodegenUnit(unittest.TestCase):
    def test_all_themes_and_semantic_pairs_pass_wcag_aa(self) -> None:
        audit = tokens.audit_theme_contrast()
        failures = [r for r in audit if not r["pass_aa"]]
        self.assertEqual(failures, [], f"WCAG AA failures detected: {failures}")

    def test_all_templates_emit_valid_node_create_batch_steps(self) -> None:
        for theme in tokens.list_themes():
            for tmpl in tokens.SUPPORTED_TEMPLATES:
                cmds = tokens.build_template_commands(tmpl, theme_name=theme, palette_name="indigo")
                self.assertGreater(len(cmds), 0)
                self.assertEqual(cmds[0]["command"], "node.create")

    def test_codegen_generates_all_four_frameworks(self) -> None:
        ast = codegen_helper.clean_node({
            "name": "Save Button",
            "type": "FRAME",
            "cornerRadius": 8,
            "layout": {"mode": "horizontal", "padding": [12, 20, 12, 20], "mainAlign": "center", "crossAlign": "center"},
            "fills": [{"type": "solid", "color": "#4F46E5"}],
            "children": [
                {"name": "Label", "type": "TEXT", "characters": "Save changes", "fontSize": 14, "fontStyle": "SemiBold", "fills": [{"type": "solid", "color": "#FFFFFF"}]}
            ],
        })
        for fw in codegen_helper.SUPPORTED_FRAMEWORKS:
            out = codegen_helper.generate_code(ast, framework=fw)
            self.assertEqual(out["framework"], fw)
            self.assertIn("Save changes", out["code"])


if __name__ == "__main__":
    unittest.main()
