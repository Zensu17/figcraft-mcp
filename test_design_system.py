#!/usr/bin/env python3
"""
Verification Suite for FigCraft Design System, WCAG Contrast & Canvas Templates
-------------------------------------------------------------------------------
Validates:
1. Mathematical WCAG 2.2 AA contrast (>= 4.5:1) across all themes and semantic statuses.
2. Exact FigCraft engine batch schema compliance on all 7 component templates.
3. CSS custom property & Tailwind config export integrity.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import tokens

FORBIDDEN_PROP_KEYS = {"layoutMode", "itemSpacing", "strokeWidth", "fontWeight", "color"}
FORBIDDEN_ALIGNS = {"start", "end", "space-between", "space-around", "space-evenly"}


def validate_batch_commands(commands: list[dict], template_name: str) -> None:
    assert commands, f"Template '{template_name}' returned empty command list"
    defined_refs: set[str] = set()

    for idx, step in enumerate(commands):
        assert step.get("command") == "node.create", (
            f"{template_name}[{idx}] must use command='node.create', got {step}"
        )
        assert "action" not in step, f"{template_name}[{idx}] contains legacy 'action' key"

        params = step.get("params", {})
        assert params.get("type") in ("frame", "text"), f"Unexpected type in {template_name}[{idx}]"

        if idx > 0:
            parent = params.get("parent")
            assert isinstance(parent, dict) and "$ref" in parent, (
                f"{template_name}[{idx}] missing parent $ref: {params}"
            )
            assert parent["$ref"] in defined_refs, (
                f"{template_name}[{idx}] references undefined parent '{parent['$ref']}'"
            )

        props = params.get("props", {})
        for bad_key in FORBIDDEN_PROP_KEYS:
            assert bad_key not in props and bad_key not in params, (
                f"{template_name}[{idx}] contains forbidden FigCraft property '{bad_key}'"
            )

        if "mainAlign" in props:
            assert props["mainAlign"] not in FORBIDDEN_ALIGNS, (
                f"{template_name}[{idx}] invalid mainAlign '{props['mainAlign']}'"
            )
        if "crossAlign" in props:
            assert props["crossAlign"] not in FORBIDDEN_ALIGNS, (
                f"{template_name}[{idx}] invalid crossAlign '{props['crossAlign']}'"
            )

        if params.get("type") == "frame":
            assert "fill" in props, (
                f"{template_name}[{idx}] frame '{params.get('name')}' must specify explicit fill (or 'none')"
            )

        if "as" in step:
            assert step["as"] not in defined_refs, f"Duplicate step ref '{step['as']}'"
            defined_refs.add(step["as"])


def test_wcag_contrast_audit() -> None:
    audit = tokens.audit_theme_contrast()
    assert len(audit) >= 32
    failures = [item for item in audit if not item["pass_aa"]]
    assert not failures, f"WCAG AA contrast failures: {failures}"
    print(f"  [PASS] WCAG 2.2 AA contrast verified ({len(audit)}/ {len(audit)} pairs >= 4.5:1)")


def test_all_templates_and_themes() -> None:
    theme_names = tokens.list_themes()
    assert len(theme_names) == 4
    total_checked = 0

    for theme_name in theme_names:
        for tmpl in tokens.SUPPORTED_TEMPLATES:
            cmds = tokens.build_template_commands(tmpl, theme_name=theme_name, palette_name="stone")
            validate_batch_commands(cmds, f"{tmpl}:{theme_name}")
            total_checked += 1

    print(
        f"  [PASS] All {total_checked} template x theme combinations pass FigCraft batch schema checks"
    )


def test_exporters_and_boundary_validation() -> None:
    tw_json = json.loads(tokens.export_tailwind_theme())
    assert "stone" in tw_json["theme"]["extend"]["colors"]
    assert "indigo" in tw_json["theme"]["extend"]["colors"]

    css = tokens.export_css_variables("editorial-paper")
    assert "--fc-surface: #FAFAF9;" in css
    assert "--fc-accent: #B45309;" in css

    try:
        tokens.get_theme("nonexistent-theme")
        raise AssertionError("Expected ValueError for unknown theme")
    except ValueError as exc:
        assert "Available themes" in str(exc)

    try:
        tokens.build_template_commands("invalid_template")
        raise AssertionError("Expected ValueError for unknown template")
    except ValueError as exc:
        assert "Unsupported template" in str(exc)

    print("  [PASS] Tailwind/CSS exporters & boundary validation")


def main() -> None:
    print("Running FigCraft Design System Verification Suite...")
    test_wcag_contrast_audit()
    test_all_templates_and_themes()
    test_exporters_and_boundary_validation()
    print("\nAll Design System tests passed.")


if __name__ == "__main__":
    main()
