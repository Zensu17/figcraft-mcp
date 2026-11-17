#!/usr/bin/env python3
"""
Test Design-to-Code Pipeline
----------------------------
Demonstrates and verifies that FigCraft design tokens can be translated
into a production-grade React Tailwind CSS component.
"""

import json
import re
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
EXAMPLES_DIR = SCRIPT_DIR / "examples"


def tokens_to_react_tailwind(node: dict) -> str:
    """Simple converter mapping semantic UI tokens to React + Tailwind JSX."""
    node_type = node.get("type", "frame")

    if node_type == "text":
        color = node.get("color", "#FFFFFF")
        size = node.get("fontSize", 14)
        text = node.get("text", "")
        # Map font size to Tailwind
        if size >= 30:
            size_cls = "text-3xl font-extrabold"
        elif size >= 20:
            size_cls = "text-xl font-bold"
        elif size >= 16:
            size_cls = "text-base font-semibold"
        elif size >= 13:
            size_cls = "text-sm"
        else:
            size_cls = "text-xs"

        return f'<span className="{size_cls} text-[{color}]">{text}</span>'

    # Frame / Container
    classes = []
    direction = node.get("direction", "col")
    classes.append("flex")
    classes.append("flex-col" if direction == "col" else "flex-row")

    if "p" in node:
        classes.append(f"p-[{node['p']}px]")
    if "gap" in node:
        classes.append(f"gap-[{node['gap']}px]")
    if "bg" in node:
        classes.append(f"bg-[{node['bg']}]")
    if "rounded" in node:
        classes.append(f"rounded-[{node['rounded']}px]")
    if "justify" in node:
        j_map = {"between": "justify-between", "center": "justify-center", "start": "justify-start", "end": "justify-end"}
        classes.append(j_map.get(node["justify"], ""))
    if "items" in node:
        i_map = {"center": "items-center", "start": "items-start", "end": "items-end"}
        classes.append(i_map.get(node["items"], ""))

    cls_str = " ".join(c for c in classes if c)

    children_jsx = []
    for child in node.get("children", []):
        children_jsx.append(tokens_to_react_tailwind(child))

    joined_children = "\n        ".join(children_jsx)
    name = node.get("name", "Container")
    return f"""{'{/* ' + name + ' */}'}
      <div className="{cls_str}">
        {joined_children}
      </div>"""


def main():
    print("Testing Design-to-Code Pipeline...")

    # Sample FigCraft Weather Widget Token Tree (Identical to canvas node 57)
    weather_tokens = {
        "type": "frame",
        "name": "Simple Weather Widget",
        "direction": "col",
        "w": 280,
        "h": 190,
        "p": 20,
        "gap": 10,
        "rounded": 20,
        "bg": "#1E293B",
        "children": [
            {
                "type": "text",
                "name": "Location",
                "text": "📍 Jakarta, Indonesia",
                "fontSize": 12,
                "color": "#94A3B8"
            },
            {
                "type": "frame",
                "name": "Temperature Row",
                "direction": "row",
                "gap": 12,
                "items": "center",
                "children": [
                    {
                        "type": "text",
                        "name": "Temp",
                        "text": "29°C",
                        "fontSize": 34,
                        "color": "#F8FAFC"
                    },
                    {
                        "type": "text",
                        "name": "Condition",
                        "text": "⛅ Sebagian Berawan",
                        "fontSize": 13,
                        "color": "#38BDF8"
                    }
                ]
            },
            {
                "type": "frame",
                "name": "Metrics Row",
                "direction": "row",
                "justify": "between",
                "items": "center",
                "children": [
                    {
                        "type": "text",
                        "name": "Humidity",
                        "text": "💧 78%",
                        "fontSize": 11,
                        "color": "#94A3B8"
                    },
                    {
                        "type": "text",
                        "name": "Wind",
                        "text": "💨 14 km/j",
                        "fontSize": 11,
                        "color": "#94A3B8"
                    },
                    {
                        "type": "text",
                        "name": "UV Index",
                        "text": "☀️ UV Sedang",
                        "fontSize": 11,
                        "color": "#94A3B8"
                    }
                ]
            }
        ]
    }

    body_jsx = tokens_to_react_tailwind(weather_tokens)

    component_code = f"""import React from 'react';

export default function WeatherWidget() {{
  return (
    <div className="flex items-center justify-center p-6 bg-slate-950 min-h-screen">
      {body_jsx}
    </div>
  );
}}
"""

    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    out_file = EXAMPLES_DIR / "WeatherWidget.tsx"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(component_code)

    print(f"  ✔ Generated Component saved to: {out_file}")

    # Assertions
    assert "export default function WeatherWidget" in component_code
    assert "bg-[#1E293B]" in component_code
    assert "rounded-[20px]" in component_code
    assert "📍 Jakarta, Indonesia" in component_code
    assert "29°C" in component_code
    assert "⛅ Sebagian Berawan" in component_code
    assert "💧 78%" in component_code

    print("\n\033[1;32m=== Design-to-Code Pipeline Verified Successfully! ===\033[0m\n")


if __name__ == "__main__":
    main()
