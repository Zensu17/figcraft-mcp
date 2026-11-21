#!/usr/bin/env python3
"""
Test Design-to-Code Pipeline
----------------------------
Verifies AST cleaning, token reverse-mapping, Code Connect props extraction,
and multi-framework code generation (React + Tailwind, Vue 3, Flutter, HTML/CSS).
"""

from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from codegen_helper import clean_node, extract_component_props, generate_code

EXAMPLES_DIR = SCRIPT_DIR / "examples"


def build_sample_weather_raw_node() -> dict:
    return {
        "id": 57,
        "name": "Weather Widget",
        "type": "FRAME",
        "width": 280.0,
        "height": 190.0,
        "cornerRadius": 16.0,
        "layout": {
            "mode": "vertical",
            "gap": 12.0,
            "padding": [20.0, 24.0, 20.0, 24.0],
            "mainAlign": "min",
            "crossAlign": "min",
        },
        "fills": [{"type": "solid", "color": "#1E293B"}],
        "strokes": [{"type": "solid", "color": "#334155"}],
        "strokeWeight": 1.0,
        "componentPropertyDefinitions": {
            "Theme#1:0": {
                "type": "VARIANT",
                "defaultValue": "dark",
                "variantOptions": ["dark", "light"],
            },
            "Compact#2:0": {
                "type": "BOOLEAN",
                "defaultValue": False,
            },
        },
        "children": [
            {
                "id": 58,
                "name": "Location",
                "type": "TEXT",
                "characters": "Jakarta, Indonesia",
                "fontSize": 12.0,
                "fontStyle": "Medium",
                "fills": [{"type": "solid", "color": "#94A3B8"}],
            },
            {
                "id": 59,
                "name": "Temperature Row",
                "type": "FRAME",
                "layout": {"mode": "horizontal", "gap": 12.0, "crossAlign": "center"},
                "children": [
                    {
                        "id": 60,
                        "name": "Temperature",
                        "type": "TEXT",
                        "characters": "29°C",
                        "fontSize": 36.0,
                        "fontStyle": "Bold",
                        "fills": [{"type": "solid", "color": "#F8FAFC"}],
                    },
                    {
                        "id": 61,
                        "name": "Condition",
                        "type": "TEXT",
                        "characters": "Partly Cloudy",
                        "fontSize": 14.0,
                        "fontStyle": "SemiBold",
                        "fills": [{"type": "solid", "color": "#38BDF8"}],
                    },
                ],
            },
            {
                "id": 62,
                "name": "Refresh Button",
                "type": "FRAME",
                "cornerRadius": 8.0,
                "layout": {
                    "mode": "horizontal",
                    "padding": [8.0, 16.0, 8.0, 16.0],
                    "mainAlign": "center",
                    "crossAlign": "center",
                },
                "fills": [{"type": "solid", "color": "#4F46E5"}],
                "children": [
                    {
                        "id": 63,
                        "name": "Action Label",
                        "type": "TEXT",
                        "characters": "Refresh Forecast",
                        "fontSize": 14.0,
                        "fontStyle": "SemiBold",
                        "fills": [{"type": "solid", "color": "#FFFFFF"}],
                    }
                ],
            },
            {
                "id": 64,
                "name": "Footer Slot",
                "type": "FRAME",
                "layout": {"mode": "horizontal"},
                "children": [],
            },
        ],
    }


def main() -> None:
    print("Testing Multi-Framework Design-to-Code Pipeline...")

    raw = build_sample_weather_raw_node()
    cleaned = clean_node(raw)

    # 1. Verify AST cleaning (asymmetric padding, stroke, role, componentPropertyDefinitions)
    assert cleaned["py"] == 20 and cleaned["px"] == 24
    assert cleaned["borderColor"] == "#334155" and cleaned["borderWidth"] == 1
    assert cleaned["children"][2]["role"] == "button"
    assert "componentPropertyDefinitions" in cleaned
    print("  [PASS] Semantic AST extraction (asymmetric padding, border, role, component props)")

    # 2. Verify Code Connect style props extraction
    props, bindings = extract_component_props(cleaned)
    prop_map = {p["name"]: p for p in props}
    assert prop_map["theme"]["kind"] == "variant"
    assert prop_map["theme"]["options"] == ["dark", "light"]
    assert prop_map["compact"]["kind"] == "boolean"
    assert prop_map["location"]["default"] == "Jakarta, Indonesia"
    assert prop_map["temperature"]["default"] == "29°C"
    assert prop_map["actionLabel"]["default"] == "Refresh Forecast"
    assert prop_map["footerSlot"]["kind"] == "slot"
    assert len(bindings) == 5
    print(f"  [PASS] Props extraction ({len(props)} typed props: variant, boolean, text, slot)")

    # 3. Verify React + Tailwind generation & token reverse lookup
    react_res = generate_code(cleaned, framework="react-tailwind")
    react_code = react_res["code"]
    assert "export interface WeatherWidgetProps" in react_code
    assert 'theme?: "dark" | "light";' in react_code
    assert "compact?: boolean;" in react_code
    assert "footerSlot?: React.ReactNode;" in react_code
    assert "bg-slate-800" in react_code
    assert "border-slate-700" in react_code
    assert "rounded-2xl" in react_code
    assert "py-5" in react_code and "px-6" in react_code
    assert "text-sky-400" in react_code
    assert "bg-indigo-600" in react_code
    assert '<button type="button"' in react_code
    assert "{footerSlot}" in react_code

    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EXAMPLES_DIR / "WeatherWidget.tsx"
    out_file.write_text(react_code, encoding="utf-8")
    print(f"  [PASS] React + Tailwind generator (saved example to {out_file})")

    # 4. Verify Vue 3 SFC generation
    vue_res = generate_code(cleaned, framework="vue")
    vue_code = vue_res["code"]
    assert '<script setup lang="ts">' in vue_code
    assert "withDefaults(defineProps<Props>()" in vue_code
    assert "{{ props.location }}" in vue_code
    assert '<slot name="footerSlot" />' in vue_code
    assert "bg-slate-800" in vue_code
    print("  [PASS] Vue 3 SFC generator")

    # 5. Verify Flutter Widget generation
    flutter_res = generate_code(cleaned, framework="flutter")
    flutter_code = flutter_res["code"]
    assert "class WeatherWidget extends StatelessWidget" in flutter_code
    assert "final String location;" in flutter_code
    assert "final Widget? footerSlot;" in flutter_code
    assert "Color(0xFF1E293B)" in flutter_code
    assert "BorderRadius.circular(16.0)" in flutter_code
    assert "FontWeight.w700" in flutter_code
    print("  [PASS] Flutter StatelessWidget generator")

    # 6. Verify HTML + CSS generation
    html_res = generate_code(cleaned, framework="html-css")
    html_code = html_res["code"]
    assert "<style>" in html_code
    assert "background-color: #1E293B;" in html_code
    assert "padding: 20px 24px;" in html_code
    assert '<button type="button"' in html_code
    assert "Jakarta, Indonesia" in html_code
    print("  [PASS] Semantic HTML + CSS generator")

    # 7. Verify boundary validation on unsupported framework
    try:
        generate_code(cleaned, framework="svelte")
        raise AssertionError("Expected ValueError for unsupported framework")
    except ValueError as exc:
        assert "Unsupported framework" in str(exc)
    print("  [PASS] Boundary validation rejects unsupported framework")

    print("\nAll Design-to-Code pipeline tests passed.")


if __name__ == "__main__":
    main()
