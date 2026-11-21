#!/usr/bin/env python3
"""
FigCraft UI AST Cleaner, Token Mapper & Multi-Framework Code Generator
----------------------------------------------------------------------
Extracts semantic design tokens from FigCraft node trees, maps colors/spacing/radius
back to tokens.json, infers typed component props (Code Connect pattern), and generates
production-ready React + Tailwind, Vue 3, Flutter, or semantic HTML/CSS code.

Zero external dependencies: 100% Python standard library.
"""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import security

SCRIPT_DIR = Path(__file__).resolve().parent
BRIDGE_PATH = SCRIPT_DIR / "bridge.py"
TOKENS_PATH = SCRIPT_DIR / "tokens.json"

SUPPORTED_FRAMEWORKS: tuple[str, ...] = ("react-tailwind", "vue", "flutter", "html-css")

_RESERVED_IDENTIFIERS: set[str] = {
    "break", "case", "catch", "class", "const", "continue", "debugger", "default",
    "delete", "do", "else", "enum", "export", "extends", "false", "finally", "for",
    "function", "if", "import", "in", "instanceof", "interface", "key", "let", "new",
    "null", "package", "private", "protected", "public", "ref", "return", "static",
    "super", "switch", "this", "throw", "true", "try", "type", "typeof", "var",
    "void", "while", "with", "yield", "final", "widget", "build", "context", "child",
}

_FONT_STYLE_TO_TW: dict[str, str] = {
    "thin": "font-thin",
    "extralight": "font-extralight",
    "light": "font-light",
    "regular": "font-normal",
    "normal": "font-normal",
    "medium": "font-medium",
    "semibold": "font-semibold",
    "bold": "font-bold",
    "extrabold": "font-extrabold",
    "black": "font-black",
}

_FONT_STYLE_TO_CSS: dict[str, int] = {
    "thin": 100,
    "extralight": 200,
    "light": 300,
    "regular": 400,
    "normal": 400,
    "medium": 500,
    "semibold": 600,
    "bold": 700,
    "extrabold": 800,
    "black": 900,
}

_FONT_STYLE_TO_DART: dict[str, str] = {
    "thin": "FontWeight.w100",
    "extralight": "FontWeight.w200",
    "light": "FontWeight.w300",
    "regular": "FontWeight.w400",
    "normal": "FontWeight.w400",
    "medium": "FontWeight.w500",
    "semibold": "FontWeight.w600",
    "bold": "FontWeight.w700",
    "extrabold": "FontWeight.w800",
    "black": "FontWeight.w900",
}

_TOKEN_CACHE: dict[str, Any] | None = None


def _load_token_maps() -> dict[str, Any]:
    """Load reverse lookup tables from tokens.json (hex -> palette-shade, px -> scale)."""
    global _TOKEN_CACHE
    if _TOKEN_CACHE is not None:
        return _TOKEN_CACHE

    color_map: dict[str, str] = {
        "#FFFFFF": "white",
        "#000000": "black",
    }
    spacing_map: dict[int, str] = {}
    radius_map: dict[int, str] = {}
    font_size_map: dict[int, str] = {}

    if TOKENS_PATH.is_file():
        try:
            data = json.loads(TOKENS_PATH.read_text(encoding="utf-8"))
            for palette, shades in data.get("colors", {}).items():
                if isinstance(shades, dict):
                    for shade, hex_val in shades.items():
                        if isinstance(hex_val, str):
                            color_map[hex_val.upper()] = f"{palette}-{shade}"

            for key, px in data.get("spacing", {}).items():
                if isinstance(px, (int, float)):
                    spacing_map[round(px)] = str(key)

            for key, px in data.get("radius", {}).items():
                if isinstance(px, (int, float)):
                    radius_map[round(px)] = "" if key == "default" else str(key)

            for key, spec in data.get("typography", {}).items():
                if isinstance(spec, dict) and isinstance(spec.get("size"), (int, float)):
                    font_size_map[round(spec["size"])] = str(key)
        except Exception:
            pass

    _TOKEN_CACHE = {
        "colors": color_map,
        "spacing": spacing_map,
        "radius": radius_map,
        "fontSize": font_size_map,
    }
    return _TOKEN_CACHE


def _infer_semantic_role(name: str, node_type: str) -> str | None:
    """Infer semantic HTML/UI role from layer naming conventions."""
    if node_type == "text":
        return None
    lower = name.strip().lower()
    if not lower:
        return None
    if any(k in lower for k in ("navbar", "nav bar", "navigation", "top nav", "bottom nav")):
        return "nav"
    if any(k in lower for k in ("button", "btn", "cta")):
        return "button"
    if any(k in lower for k in ("input", "field", "search bar", "textbox")):
        return "input"
    if "header" in lower and "row" not in lower:
        return "header"
    if "footer" in lower:
        return "footer"
    return None


def _parse_padding(p_val: Any) -> dict[str, int]:
    """Normalize numeric or [top, right, bottom, left] padding to semantic keys."""
    if isinstance(p_val, (int, float)):
        val = round(p_val)
        return {"p": val} if val > 0 else {}
    if isinstance(p_val, list) and p_val:
        nums = [round(v) for v in p_val if isinstance(v, (int, float))]
        if not nums:
            return {}
        if len(nums) == 1 or len(set(nums)) == 1:
            return {"p": nums[0]} if nums[0] > 0 else {}
        if len(nums) == 2:
            out: dict[str, int] = {}
            if nums[0] > 0:
                out["py"] = nums[0]
            if nums[1] > 0:
                out["px"] = nums[1]
            return out
        if len(nums) >= 4:
            t, r, b, l = nums[0], nums[1], nums[2], nums[3]
            if t == b and l == r:
                out = {}
                if t > 0:
                    out["py"] = t
                if l > 0:
                    out["px"] = l
                return out
            return {"pt": t, "pr": r, "pb": b, "pl": l}
    return {}


def clean_node(node: dict[str, Any]) -> dict[str, Any]:
    """Recursively clean and extract semantic UI tokens from a FigCraft node."""
    if not isinstance(node, dict):
        return {}

    node_type = (node.get("type") or "frame").lower()
    name = node.get("name", "")

    cleaned: dict[str, Any] = {
        "type": node_type,
        "name": name,
    }

    role = _infer_semantic_role(name, node_type)
    if role:
        cleaned["role"] = role

    if node.get("visible") is False:
        cleaned["visible"] = False

    opacity = node.get("opacity")
    if isinstance(opacity, (int, float)) and opacity < 1.0:
        cleaned["opacity"] = round(float(opacity), 2)

    # Dimensions
    if "width" in node and isinstance(node["width"], (int, float)):
        cleaned["w"] = round(node["width"])
    if "height" in node and isinstance(node["height"], (int, float)):
        cleaned["h"] = round(node["height"])

    # Corner Radius
    radius = node.get("cornerRadius")
    if isinstance(radius, (int, float)) and radius > 0:
        cleaned["rounded"] = round(radius)

    # Fills (Background Color)
    fills = node.get("fills", [])
    if fills and isinstance(fills, list):
        for f in fills:
            if isinstance(f, dict) and f.get("type") == "solid" and "color" in f:
                if f.get("visible", True) is not False:
                    cleaned["bg"] = f["color"]
                    break
    elif isinstance(node.get("fill"), str) and node["fill"].lower() != "none":
        cleaned["bg"] = node["fill"]

    # Auto Layout properties
    layout = node.get("layout")
    align_map = {
        "min": "start",
        "max": "end",
        "start": "start",
        "end": "end",
        "center": "center",
        "baseline": "baseline",
        "spaceBetween": "between",
        "space-between": "between",
        "spaceAround": "around",
        "spaceEvenly": "evenly",
    }
    if layout:
        if isinstance(layout, dict):
            mode = str(layout.get("mode", "vertical")).lower()
            cleaned["direction"] = "col" if mode == "vertical" else "row"
            if "gap" in layout and isinstance(layout["gap"], (int, float)):
                cleaned["gap"] = round(layout["gap"])
            if "padding" in layout:
                cleaned.update(_parse_padding(layout["padding"]))
            if "mainAlign" in layout:
                cleaned["justify"] = align_map.get(layout["mainAlign"], layout["mainAlign"])
            if "crossAlign" in layout:
                cleaned["items"] = align_map.get(layout["crossAlign"], layout["crossAlign"])
        else:
            cleaned["direction"] = "col" if str(layout).lower() == "vertical" else "row"
            if "gap" in node and isinstance(node["gap"], (int, float)):
                cleaned["gap"] = round(node["gap"])
            if "padding" in node:
                cleaned.update(_parse_padding(node["padding"]))
            if "mainAlign" in node:
                cleaned["justify"] = align_map.get(node["mainAlign"], node["mainAlign"])
            if "crossAlign" in node:
                cleaned["items"] = align_map.get(node["crossAlign"], node["crossAlign"])

    # Strokes / Borders
    strokes = node.get("strokes", [])
    if strokes and isinstance(strokes, list):
        for s in strokes:
            if isinstance(s, dict) and s.get("type") == "solid" and "color" in s:
                if s.get("visible", True) is not False:
                    cleaned["borderColor"] = s["color"]
                    break
    elif node.get("stroke") and isinstance(node["stroke"], str):
        cleaned["borderColor"] = node["stroke"]

    stroke_weight = node.get("strokeWeight") or node.get("strokeWidth")
    if isinstance(stroke_weight, (int, float)) and stroke_weight > 0:
        cleaned["borderWidth"] = round(stroke_weight)

    # Component Metadata (Code Connect style)
    if node.get("mainComponentName"):
        cleaned["mainComponentName"] = str(node["mainComponentName"])
    if isinstance(node.get("componentPropertyDefinitions"), dict) and node["componentPropertyDefinitions"]:
        cleaned["componentPropertyDefinitions"] = node["componentPropertyDefinitions"]
    if isinstance(node.get("componentProperties"), dict) and node["componentProperties"]:
        cleaned["componentProperties"] = node["componentProperties"]

    # Typography / Text layer
    if node_type == "text" or "text" in node or "characters" in node:
        cleaned["text"] = node.get("characters") if "characters" in node else node.get("text", "")
        if "fontSize" in node and isinstance(node["fontSize"], (int, float)):
            cleaned["fontSize"] = round(node["fontSize"])
        if "fontStyle" in node and node["fontStyle"]:
            cleaned["fontStyle"] = str(node["fontStyle"])
        if "textAlign" in node and node["textAlign"]:
            cleaned["textAlign"] = str(node["textAlign"]).lower()
        if "lineHeight" in node and isinstance(node["lineHeight"], (int, float)):
            cleaned["lineHeight"] = round(node["lineHeight"])
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


def to_pascal_case(raw: str, fallback: str = "FigCraftComponent") -> str:
    """Convert an arbitrary FigCraft layer name into a valid PascalCase identifier."""
    tokens = re.findall(r"[A-Za-z0-9]+", raw or "")
    if not tokens:
        return fallback
    result = "".join(t[:1].upper() + t[1:] for t in tokens)
    if result[0].isdigit():
        result = f"Component{result}"
    return result


def to_camel_case(raw: str, fallback: str = "value") -> str:
    """Convert an arbitrary FigCraft layer or property name into a valid camelCase identifier."""
    tokens = re.findall(r"[A-Za-z0-9]+", raw or "")
    if not tokens:
        return fallback
    first = tokens[0].lower()
    rest = [t[:1].upper() + t[1:] for t in tokens[1:]]
    ident = first + "".join(rest)
    if ident[0].isdigit():
        ident = f"prop{ident}"
    if ident.lower() in _RESERVED_IDENTIFIERS:
        ident = f"{ident}Value"
    return ident


def _unique_prop_name(base: str, used: set[str]) -> str:
    candidate = base
    idx = 2
    while candidate in used:
        candidate = f"{base}{idx}"
        idx += 1
    used.add(candidate)
    return candidate


def extract_component_props(ast_node: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[int, str]]:
    """
    Extract typed component props from a cleaned semantic AST using Code Connect patterns.

    Returns:
      - props: list of prop specifications ({name, kind, ts_type, dart_type, default, source_layer, options?})
      - node_prop_bindings: mapping of id(node_dict) -> prop_name for codegen interpolation
    """
    props: list[dict[str, Any]] = []
    used_names: set[str] = set()
    bindings: dict[int, str] = {}

    # 1. Explicit componentPropertyDefinitions (VARIANT, BOOLEAN, TEXT, SLOT)
    prop_defs = ast_node.get("componentPropertyDefinitions")
    if isinstance(prop_defs, dict):
        for raw_key, spec in prop_defs.items():
            if not isinstance(spec, dict):
                continue
            prop_kind = str(spec.get("type", "TEXT")).upper()
            clean_key = raw_key.split("#")[0].strip()
            prop_name = _unique_prop_name(to_camel_case(clean_key, "prop"), used_names)
            default_val = spec.get("defaultValue")

            if prop_kind == "VARIANT":
                raw_opts = spec.get("variantOptions") or ([default_val] if default_val is not None else ["default"])
                options = [str(o) for o in raw_opts]
                ts_union = " | ".join(json.dumps(o) for o in options)
                props.append({
                    "name": prop_name,
                    "kind": "variant",
                    "ts_type": ts_union,
                    "dart_type": "String",
                    "default": str(default_val if default_val is not None else options[0]),
                    "options": options,
                    "source_layer": clean_key,
                })
            elif prop_kind == "BOOLEAN":
                props.append({
                    "name": prop_name,
                    "kind": "boolean",
                    "ts_type": "boolean",
                    "dart_type": "bool",
                    "default": bool(default_val) if default_val is not None else False,
                    "source_layer": clean_key,
                })
            elif prop_kind == "SLOT":
                props.append({
                    "name": prop_name,
                    "kind": "slot",
                    "ts_type": "React.ReactNode",
                    "dart_type": "Widget?",
                    "default": None,
                    "source_layer": clean_key,
                })
            else:
                props.append({
                    "name": prop_name,
                    "kind": "text",
                    "ts_type": "string",
                    "dart_type": "String",
                    "default": str(default_val if default_val is not None else ""),
                    "source_layer": clean_key,
                })

    # 2. Traverse AST for text layers & slot containers
    def visit(node: dict[str, Any]) -> None:
        n_type = node.get("type", "frame")
        n_name = str(node.get("name", "")).strip()

        if n_type == "text":
            base = to_camel_case(n_name, "label")
            prop_name = _unique_prop_name(base, used_names)
            text_val = str(node.get("text", ""))
            props.append({
                "name": prop_name,
                "kind": "text",
                "ts_type": "string",
                "dart_type": "String",
                "default": text_val,
                "source_layer": n_name or prop_name,
            })
            bindings[id(node)] = prop_name
            return

        if n_name and any(tok in n_name.lower() for tok in ("slot", "children")) and not node.get("children"):
            base = to_camel_case(n_name, "contentSlot")
            prop_name = _unique_prop_name(base, used_names)
            props.append({
                "name": prop_name,
                "kind": "slot",
                "ts_type": "React.ReactNode",
                "dart_type": "Widget?",
                "default": None,
                "source_layer": n_name,
            })
            bindings[id(node)] = prop_name
            return

        for child in node.get("children", []):
            if isinstance(child, dict):
                visit(child)

    visit(ast_node)
    return props, bindings


def _tw_color(prefix: str, hex_color: str) -> str:
    safe_hex = security.validate_hex_color(hex_color)
    if not safe_hex:
        return ""
    tokens = _load_token_maps()["colors"]
    matched = tokens.get(safe_hex.upper())
    return f"{prefix}-{matched}" if matched else f"{prefix}-[{safe_hex}]"


def _tw_spacing(prefix: str, px: int) -> str:
    tokens = _load_token_maps()["spacing"]
    matched = tokens.get(px)
    return f"{prefix}-{matched}" if matched is not None else f"{prefix}-[{px}px]"


def _tw_radius(px: int) -> str:
    if px >= 9999:
        return "rounded-full"
    tokens = _load_token_maps()["radius"]
    if px in tokens:
        suffix = tokens[px]
        return "rounded" if suffix == "" else f"rounded-{suffix}"
    return f"rounded-[{px}px]"


def _tw_font_size(px: int) -> str:
    tokens = _load_token_maps()["fontSize"]
    matched = tokens.get(px)
    return f"text-{matched}" if matched else f"text-[{px}px]"


def _tw_font_weight(style: str | None, font_size: int) -> str:
    if style:
        norm = style.strip().lower().replace(" ", "").replace("-", "")
        if norm in _FONT_STYLE_TO_TW:
            return _FONT_STYLE_TO_TW[norm]
    if font_size >= 28:
        return "font-extrabold"
    if font_size >= 20:
        return "font-bold"
    if font_size >= 16:
        return "font-semibold"
    return ""


def _build_tailwind_classes(node: dict[str, Any]) -> list[str]:
    classes: list[str] = []
    if node.get("visible") is False:
        classes.append("hidden")

    if node.get("type") == "text":
        size = int(node.get("fontSize", 14))
        classes.append(_tw_font_size(size))
        weight = _tw_font_weight(node.get("fontStyle"), size)
        if weight:
            classes.append(weight)
        if "color" in node:
            classes.append(_tw_color("text", str(node["color"])))
        align = node.get("textAlign")
        if align in ("left", "center", "right", "justify"):
            classes.append(f"text-{align}")
        if "opacity" in node:
            classes.append(f"opacity-[{node['opacity']}]")
        return classes

    direction = node.get("direction")
    if direction:
        classes.append("flex")
        classes.append("flex-col" if direction == "col" else "flex-row")
    elif node.get("children"):
        classes.append("flex")
        classes.append("flex-col")

    if "p" in node:
        classes.append(_tw_spacing("p", int(node["p"])))
    if "px" in node:
        classes.append(_tw_spacing("px", int(node["px"])))
    if "py" in node:
        classes.append(_tw_spacing("py", int(node["py"])))
    for side in ("pt", "pr", "pb", "pl"):
        if side in node:
            classes.append(_tw_spacing(side, int(node[side])))

    if "gap" in node:
        classes.append(_tw_spacing("gap", int(node["gap"])))
    if "bg" in node:
        classes.append(_tw_color("bg", str(node["bg"])))
    if "rounded" in node:
        classes.append(_tw_radius(int(node["rounded"])))

    if "borderColor" in node or "borderWidth" in node:
        bw = int(node.get("borderWidth", 1))
        classes.append("border" if bw == 1 else f"border-[{bw}px]")
        if "borderColor" in node:
            classes.append(_tw_color("border", str(node["borderColor"])))

    j_map = {
        "between": "justify-between",
        "around": "justify-around",
        "evenly": "justify-evenly",
        "center": "justify-center",
        "start": "justify-start",
        "end": "justify-end",
    }
    if "justify" in node and node["justify"] in j_map:
        classes.append(j_map[node["justify"]])

    i_map = {
        "center": "items-center",
        "start": "items-start",
        "end": "items-end",
        "baseline": "items-baseline",
    }
    if "items" in node and node["items"] in i_map:
        classes.append(i_map[node["items"]])

    if "opacity" in node:
        classes.append(f"opacity-[{node['opacity']}]")

    return [c for c in classes if c]


def _escape_jsx_text(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("{", '{"{"}')
        .replace("}", '{"}"}')
    )


def _escape_dart_string(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("'", "\\'")
        .replace("$", "\\$")
        .replace("\n", "\\n")
    )


def _hex_to_dart_color(hex_color: str) -> str:
    safe_hex = security.validate_hex_color(hex_color)
    if not safe_hex:
        return "Color(0xFFFFFFFF)"
    cleaned = safe_hex.lstrip("#").upper()
    if len(cleaned) == 3:
        cleaned = "".join(ch * 2 for ch in cleaned)
    if len(cleaned) == 6:
        return f"Color(0xFF{cleaned})"
    if len(cleaned) == 8:
        # CSS #RRGGBBAA -> Flutter 0xAARRGGBB
        return f"Color(0x{cleaned[6:8]}{cleaned[0:6]})"
    return "Color(0xFFFFFFFF)"


def _select_html_tag(node: dict[str, Any]) -> str:
    if node.get("type") == "text":
        size = int(node.get("fontSize", 14))
        if size >= 28:
            return "h1"
        if size >= 20:
            return "h2"
        if size >= 16:
            return "h3"
        return "span"
    role = node.get("role")
    if role == "button":
        return "button"
    if role == "nav":
        return "nav"
    if role == "header":
        return "header"
    if role == "footer":
        return "footer"
    return "div"


def _render_react_node(
    node: dict[str, Any],
    bindings: dict[int, str],
    include_props: bool,
    indent: int,
) -> str:
    pad = " " * indent
    tag = _select_html_tag(node)
    cls = " ".join(_build_tailwind_classes(node))
    extra_attr = ' type="button"' if tag == "button" else ""
    cls_attr = f' className="{cls}"' if cls else ""

    if node.get("type") == "text":
        prop_name = bindings.get(id(node)) if include_props else None
        content = f"{{{prop_name}}}" if prop_name else _escape_jsx_text(str(node.get("text", "")))
        return f"{pad}<{tag}{cls_attr}>{content}</{tag}>"

    slot_prop = bindings.get(id(node)) if include_props else None
    if slot_prop:
        return f"{pad}<{tag}{extra_attr}{cls_attr}>{{{slot_prop}}}</{tag}>"

    children = node.get("children", [])
    if not children:
        return f"{pad}<{tag}{extra_attr}{cls_attr} />"

    lines = [f"{pad}<{tag}{extra_attr}{cls_attr}>"]
    for child in children:
        if isinstance(child, dict):
            lines.append(_render_react_node(child, bindings, include_props, indent + 2))
    lines.append(f"{pad}</{tag}>")
    return "\n".join(lines)


def generate_react_tailwind(
    ast_node: dict[str, Any],
    component_name: str,
    props: list[dict[str, Any]],
    bindings: dict[int, str],
    include_props: bool = True,
) -> str:
    lines: list[str] = ["import React from 'react';", ""]
    if include_props and props:
        lines.append(f"export interface {component_name}Props {{")
        for p in props:
            lines.append(f"  {p['name']}?: {p['ts_type']};")
        lines.append("}")
        lines.append("")

        params_list: list[str] = []
        for p in props:
            if p["kind"] == "slot":
                params_list.append(f"  {p['name']},")
            elif p["kind"] == "boolean":
                default_js = "true" if p["default"] else "false"
                params_list.append(f"  {p['name']} = {default_js},")
            else:
                params_list.append(f"  {p['name']} = {json.dumps(p['default'])},")

        lines.append(f"export default function {component_name}({{")
        lines.extend(params_list)
        lines.append(f"}}: {component_name}Props) {{")
    else:
        lines.append(f"export default function {component_name}() {{")

    lines.append("  return (")
    lines.append(_render_react_node(ast_node, bindings, include_props, indent=4))
    lines.append("  );")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def _render_vue_node(
    node: dict[str, Any],
    bindings: dict[int, str],
    include_props: bool,
    indent: int,
) -> str:
    pad = " " * indent
    tag = _select_html_tag(node)
    cls = " ".join(_build_tailwind_classes(node))
    extra_attr = ' type="button"' if tag == "button" else ""
    cls_attr = f' class="{cls}"' if cls else ""

    if node.get("type") == "text":
        prop_name = bindings.get(id(node)) if include_props else None
        if prop_name:
            content = f"{{{{ props.{prop_name} }}}}"
        else:
            escaped = html.escape(str(node.get("text", "")))
            content = escaped.replace("{{", "&#123;&#123;").replace("}}", "&#125;&#125;")
        return f"{pad}<{tag}{cls_attr}>{content}</{tag}>"

    slot_prop = bindings.get(id(node)) if include_props else None
    if slot_prop:
        return f'{pad}<{tag}{extra_attr}{cls_attr}><slot name="{slot_prop}" /></{tag}>'

    children = node.get("children", [])
    if not children:
        return f"{pad}<{tag}{extra_attr}{cls_attr} />"

    lines = [f"{pad}<{tag}{extra_attr}{cls_attr}>"]
    for child in children:
        if isinstance(child, dict):
            lines.append(_render_vue_node(child, bindings, include_props, indent + 2))
    lines.append(f"{pad}</{tag}>")
    return "\n".join(lines)


def generate_vue_sfc(
    ast_node: dict[str, Any],
    props: list[dict[str, Any]],
    bindings: dict[int, str],
    include_props: bool = True,
) -> str:
    lines: list[str] = ['<script setup lang="ts">']
    non_slot_props = [p for p in props if p["kind"] != "slot"]
    if include_props and non_slot_props:
        lines.append("interface Props {")
        for p in non_slot_props:
            lines.append(f"  {p['name']}?: {p['ts_type']};")
        lines.append("}")
        lines.append("")
        lines.append("const props = withDefaults(defineProps<Props>(), {")
        for p in non_slot_props:
            default_js = ("true" if p["default"] else "false") if p["kind"] == "boolean" else json.dumps(p["default"])
            lines.append(f"  {p['name']}: {default_js},")
        lines.append("});")
    lines.append("</script>")
    lines.append("")
    lines.append("<template>")
    lines.append(_render_vue_node(ast_node, bindings, include_props, indent=2))
    lines.append("</template>")
    lines.append("")
    return "\n".join(lines)


def _render_flutter_node(
    node: dict[str, Any],
    bindings: dict[int, str],
    include_props: bool,
    indent: int,
) -> str:
    pad = " " * indent
    inner = " " * (indent + 2)

    if node.get("type") == "text":
        prop_name = bindings.get(id(node)) if include_props else None
        text_expr = prop_name if prop_name else f"'{_escape_dart_string(str(node.get('text', '')))}'"
        style_parts: list[str] = []
        if "fontSize" in node:
            style_parts.append(f"fontSize: {float(node['fontSize'])}")
        if "color" in node:
            style_parts.append(f"color: {_hex_to_dart_color(str(node['color']))}")
        style_key = str(node.get("fontStyle", "")).strip().lower().replace(" ", "")
        if style_key in _FONT_STYLE_TO_DART:
            style_parts.append(f"fontWeight: {_FONT_STYLE_TO_DART[style_key]}")
        if style_parts:
            return f"{pad}Text({text_expr}, style: const TextStyle({', '.join(style_parts)}))"
        return f"{pad}Text({text_expr})"

    slot_prop = bindings.get(id(node)) if include_props else None
    if slot_prop:
        return f"{pad}{slot_prop} ?? const SizedBox.shrink()"

    direction = node.get("direction", "col")
    is_row = direction == "row"
    children = [c for c in node.get("children", []) if isinstance(c, dict)]
    gap = int(node.get("gap", 0))

    child_widget: str | None = None
    if children:
        flex_cls = "Row" if is_row else "Column"
        flex_args: list[str] = []
        j_map = {
            "start": "MainAxisAlignment.start",
            "end": "MainAxisAlignment.end",
            "center": "MainAxisAlignment.center",
            "between": "MainAxisAlignment.spaceBetween",
            "around": "MainAxisAlignment.spaceAround",
            "evenly": "MainAxisAlignment.spaceEvenly",
        }
        i_map = {
            "start": "CrossAxisAlignment.start",
            "end": "CrossAxisAlignment.end",
            "center": "CrossAxisAlignment.center",
        }
        if node.get("justify") in j_map:
            flex_args.append(f"mainAxisAlignment: {j_map[node['justify']]}")
        if node.get("items") in i_map:
            flex_args.append(f"crossAxisAlignment: {i_map[node['items']]}")
        if not is_row:
            flex_args.append("mainAxisSize: MainAxisSize.min")

        rendered_children: list[str] = []
        for idx, c in enumerate(children):
            rendered_children.append(_render_flutter_node(c, bindings, include_props, indent + 6))
            if gap > 0 and idx < len(children) - 1:
                dim = "width" if is_row else "height"
                rendered_children.append(f"{' ' * (indent + 6)}const SizedBox({dim}: {float(gap)})")

        flex_header = f"{inner}child: {flex_cls}(\n"
        for fa in flex_args:
            flex_header += f"{' ' * (indent + 4)}{fa},\n"
        flex_header += f"{' ' * (indent + 4)}children: [\n"
        flex_header += ",\n".join(rendered_children) + ",\n"
        flex_header += f"{' ' * (indent + 4)}],\n{inner}),"
        child_widget = flex_header

    container_args: list[str] = []
    if "p" in node:
        container_args.append(f"{inner}padding: const EdgeInsets.all({float(node['p'])}),")
    elif "px" in node or "py" in node:
        h = float(node.get("px", 0))
        v = float(node.get("py", 0))
        container_args.append(f"{inner}padding: const EdgeInsets.symmetric(horizontal: {h}, vertical: {v}),")
    elif any(k in node for k in ("pt", "pr", "pb", "pl")):
        container_args.append(
            f"{inner}padding: const EdgeInsets.fromLTRB("
            f"{float(node.get('pl', 0))}, {float(node.get('pt', 0))}, "
            f"{float(node.get('pr', 0))}, {float(node.get('pb', 0))}),"
        )

    deco_parts: list[str] = []
    if "bg" in node:
        deco_parts.append(f"color: {_hex_to_dart_color(str(node['bg']))}")
    if "rounded" in node:
        deco_parts.append(f"borderRadius: BorderRadius.circular({float(node['rounded'])})")
    if "borderColor" in node or "borderWidth" in node:
        bc = _hex_to_dart_color(str(node.get("borderColor", "#334155")))
        bw = float(node.get("borderWidth", 1))
        deco_parts.append(f"border: Border.all(color: {bc}, width: {bw})")
    if deco_parts:
        container_args.append(f"{inner}decoration: BoxDecoration({', '.join(deco_parts)}),")

    if child_widget:
        container_args.append(child_widget)

    if not container_args:
        return f"{pad}const SizedBox.shrink()"

    return f"{pad}Container(\n" + "\n".join(container_args) + f"\n{pad})"


def generate_flutter_widget(
    ast_node: dict[str, Any],
    component_name: str,
    props: list[dict[str, Any]],
    bindings: dict[int, str],
    include_props: bool = True,
) -> str:
    lines: list[str] = ["import 'package:flutter/material.dart';", ""]
    lines.append(f"class {component_name} extends StatelessWidget {{")
    if include_props and props:
        for p in props:
            lines.append(f"  final {p['dart_type']} {p['name']};")
        lines.append("")
        lines.append(f"  const {component_name}({{")
        lines.append("    super.key,")
        for p in props:
            if p["kind"] == "slot":
                lines.append(f"    this.{p['name']},")
            elif p["kind"] == "boolean":
                lines.append(f"    this.{p['name']} = {'true' if p['default'] else 'false'},")
            else:
                lines.append(f"    this.{p['name']} = '{_escape_dart_string(str(p['default']))}',")
        lines.append("  });")
    else:
        lines.append(f"  const {component_name}({{super.key}});")

    lines.append("")
    lines.append("  @override")
    lines.append("  Widget build(BuildContext context) {")
    lines.append("    return " + _render_flutter_node(ast_node, bindings, include_props, indent=4).lstrip() + ";")
    lines.append("  }")
    lines.append("}")
    lines.append("")
    return "\n".join(lines)


def generate_html_css(ast_node: dict[str, Any], component_name: str) -> str:
    """Generate standalone semantic HTML5 with clean scoped CSS classes."""
    css_rules: list[str] = []
    counter = [0]
    root_slug = re.sub(r"[^a-z0-9]+", "-", component_name.lower()).strip("-") or "component"

    def build_node(node: dict[str, Any], indent: int) -> str:
        counter[0] += 1
        slug = re.sub(r"[^a-z0-9]+", "-", str(node.get("name", "node")).lower()).strip("-") or "node"
        cls_name = f"{root_slug}__{slug}-{counter[0]}"
        tag = _select_html_tag(node)
        pad = " " * indent

        decls: list[str] = []
        if node.get("type") == "text":
            if "fontSize" in node:
                decls.append(f"font-size: {node['fontSize']}px;")
            style_key = str(node.get("fontStyle", "")).strip().lower().replace(" ", "")
            if style_key in _FONT_STYLE_TO_CSS:
                decls.append(f"font-weight: {_FONT_STYLE_TO_CSS[style_key]};")
            if "color" in node:
                safe_c = security.validate_hex_color(node["color"])
                if safe_c:
                    decls.append(f"color: {safe_c};")
            if "textAlign" in node:
                decls.append(f"text-align: {node['textAlign']};")
            if decls:
                css_rules.append(f".{cls_name} {{ {' '.join(decls)} }}")
            return f'{pad}<{tag} class="{cls_name}">{html.escape(str(node.get("text", "")))}</{tag}>'

        direction = node.get("direction")
        if direction or node.get("children"):
            decls.append("display: flex;")
            decls.append(f"flex-direction: {'row' if direction == 'row' else 'column'};")
        if "p" in node:
            decls.append(f"padding: {node['p']}px;")
        elif "px" in node or "py" in node:
            decls.append(f"padding: {node.get('py', 0)}px {node.get('px', 0)}px;")
        elif any(k in node for k in ("pt", "pr", "pb", "pl")):
            decls.append(
                f"padding: {node.get('pt', 0)}px {node.get('pr', 0)}px "
                f"{node.get('pb', 0)}px {node.get('pl', 0)}px;"
            )
        if "gap" in node:
            decls.append(f"gap: {node['gap']}px;")
        if "bg" in node:
            safe_bg = security.validate_hex_color(node["bg"])
            if safe_bg:
                decls.append(f"background-color: {safe_bg};")
        if "rounded" in node:
            decls.append(f"border-radius: {node['rounded']}px;")
        if "borderColor" in node or "borderWidth" in node:
            safe_bc = security.validate_hex_color(node.get("borderColor")) or "#334155"
            decls.append(
                f"border: {node.get('borderWidth', 1)}px solid {safe_bc};"
            )
        j_map = {
            "start": "flex-start",
            "end": "flex-end",
            "center": "center",
            "between": "space-between",
            "around": "space-around",
            "evenly": "space-evenly",
        }
        i_map = {
            "start": "flex-start",
            "end": "flex-end",
            "center": "center",
            "baseline": "baseline",
        }
        if node.get("justify") in j_map:
            decls.append(f"justify-content: {j_map[node['justify']]};")
        if node.get("items") in i_map:
            decls.append(f"align-items: {i_map[node['items']]};")

        if decls:
            css_rules.append(f".{cls_name} {{ {' '.join(decls)} }}")

        extra_attr = ' type="button"' if tag == "button" else ""
        children = [c for c in node.get("children", []) if isinstance(c, dict)]
        if not children:
            return f'{pad}<{tag}{extra_attr} class="{cls_name}"></{tag}>'

        inner = "\n".join(build_node(c, indent + 2) for c in children)
        return f'{pad}<{tag}{extra_attr} class="{cls_name}">\n{inner}\n{pad}</{tag}>'

    markup = build_node(ast_node, indent=0)
    styles = "\n".join(css_rules)
    return f"<style>\n{styles}\n</style>\n\n{markup}\n"


def generate_code(
    ast_node: dict[str, Any],
    framework: str = "react-tailwind",
    component_name: str | None = None,
    include_props: bool = True,
) -> dict[str, Any]:
    """
    Generate typed frontend component code from a cleaned semantic AST node.

    Returns a stable contract dict:
      {
        "component_name": str,
        "framework": str,
        "props": list[dict],
        "code": str,
      }
    """
    fw = framework.strip().lower()
    if fw not in SUPPORTED_FRAMEWORKS:
        raise ValueError(
            f"Unsupported framework '{framework}'. Choose one of: {', '.join(SUPPORTED_FRAMEWORKS)}."
        )

    comp_name = to_pascal_case(component_name or str(ast_node.get("name", "FigCraftComponent")))
    props, bindings = extract_component_props(ast_node)

    if fw == "react-tailwind":
        code = generate_react_tailwind(ast_node, comp_name, props, bindings, include_props=include_props)
    elif fw == "vue":
        code = generate_vue_sfc(ast_node, props, bindings, include_props=include_props)
    elif fw == "flutter":
        code = generate_flutter_widget(ast_node, comp_name, props, bindings, include_props=include_props)
    else:
        code = generate_html_css(ast_node, comp_name)

    return {
        "component_name": comp_name,
        "framework": fw,
        "props": props if include_props else [],
        "code": code,
    }


def query_figcraft_node(node_id: int | None = None) -> dict[str, Any]:
    """Connect to FigCraft via MCP bridge and fetch a specific node or active document."""
    proc = subprocess.Popen(
        [sys.executable, str(BRIDGE_PATH)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    def send_rpc(method: str, params: dict[str, Any], req_id: int) -> dict[str, Any]:
        assert proc.stdin and proc.stdout
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
                "clientInfo": {"name": "codegen-helper", "version": "2.0"},
            },
            1,
        )
        assert proc.stdin
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


def run_self_test() -> bool:
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

    generated = generate_code(cleaned, framework="react-tailwind")
    assert generated["component_name"] == "SimpleWeatherWidget"
    assert "bg-slate-800" in generated["code"]
    assert "location?: string" in generated["code"]

    raw_len = len(json.dumps(raw_sample))
    clean_len = len(json.dumps(cleaned))
    reduction = ((raw_len - clean_len) / raw_len) * 100
    print(f"[PASS] Self-test passed! AST Cleaned successfully ({reduction:.1f}% token reduction)")
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="FigCraft AST Cleaner & Multi-Framework Codegen")
    parser.add_argument("--node", type=int, help="Fetch and clean node by ID from FigCraft canvas")
    parser.add_argument("--doc", action="store_true", help="Fetch and inspect the active document")
    parser.add_argument("--file", type=str, help="Read and clean FigCraft node from a JSON file")
    parser.add_argument(
        "--framework",
        type=str,
        choices=SUPPORTED_FRAMEWORKS,
        help="Generate frontend code for the target framework instead of outputting raw AST JSON",
    )
    parser.add_argument("--name", type=str, help="Override generated component name (PascalCase)")
    parser.add_argument("--no-props", action="store_true", help="Disable typed props extraction")
    parser.add_argument("--out", type=str, help="Write generated output to a file path")
    parser.add_argument("--test", action="store_true", help="Run internal self-test")
    args = parser.parse_args()

    if args.test:
        run_self_test()
        return

    raw_node: dict[str, Any] = {}
    if args.node is not None:
        raw_node = query_figcraft_node(args.node)
    elif args.doc:
        raw_doc = query_figcraft_node(None)
        if raw_doc:
            print(json.dumps(raw_doc, indent=2))
        return
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            raw_node = json.load(f)
    else:
        input_data = sys.stdin.read().strip()
        if input_data:
            raw_node = json.loads(input_data)
        else:
            parser.print_help()
            return

    if not raw_node:
        return

    cleaned = clean_node(raw_node)
    if args.framework:
        result = generate_code(
            cleaned,
            framework=args.framework,
            component_name=args.name,
            include_props=not args.no_props,
        )
        output_text = result["code"]
    else:
        output_text = json.dumps(cleaned, indent=2)

    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output_text, encoding="utf-8")
        print(f"[OK] Written output to: {out_path}")
    else:
        print(output_text)


if __name__ == "__main__":
    main()
