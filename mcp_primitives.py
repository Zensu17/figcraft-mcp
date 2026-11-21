#!/usr/bin/env python3
"""
FigCraft MCP Primitives Middleware
----------------------------------
Provides custom MCP Resources, Resource Templates, Prompts, Workflow Tools,
and input normalization guardrails layered on top of FigCraft's native MCP server.

Zero external dependencies: 100% Python standard library.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Callable

from codegen_helper import SUPPORTED_FRAMEWORKS, clean_node, generate_code
from tokens import SUPPORTED_TEMPLATES, build_template_commands, list_themes

SCRIPT_DIR = Path(__file__).resolve().parent
TOKENS_PATH = SCRIPT_DIR / "tokens.json"
GUIDELINES_PATH = SCRIPT_DIR / "skills" / "figcraft-designer" / "SKILL.md"

UpstreamCaller = Callable[[str, dict[str, Any]], dict[str, Any]]

ENGINE_GUARDRAIL_INSTRUCTIONS = (
    "\n\n[FigCraft Bridge Primitives & Engine Rules]\n"
    "- Transparent Layout Wrappers: Frames default to solid white (#FFFFFF) if `fill` is omitted. "
    "Always pass `fill: \"none\"` for structural flex wrappers.\n"
    "- Property Names: Use `strokeWeight` (not `strokeWidth`), `fontStyle` such as \"Bold\"/\"SemiBold\" "
    "(not numeric `fontWeight`), and `min`/`max` for `mainAlign`/`crossAlign` (not \"start\"/\"end\").\n"
    "- Bridge Resources: `figcraft://tokens` (design tokens), `figcraft://guidelines` (design rules), "
    "`figcraft://canvas/semantic` (cleaned semantic AST of active document), "
    "`figcraft://node/{id}/semantic` (cleaned semantic AST of one node).\n"
    "- Bridge Workflow Tools: `figcraft_get_tokens`, `figcraft_extract_semantic_ast`, `figcraft_generate_code`, and `figcraft_render_template`."
)

CUSTOM_RESOURCES: list[dict[str, Any]] = [
    {
        "uri": "figcraft://tokens",
        "name": "design_tokens",
        "title": "Design Tokens",
        "description": (
            "Active FigCraft design tokens from tokens.json (colors, spacing, radius, "
            "typography, and font weights) for consistent UI styling."
        ),
        "mimeType": "application/json",
    },
    {
        "uri": "figcraft://guidelines",
        "name": "design_guidelines",
        "title": "FigCraft Design Guidelines",
        "description": (
            "Mandatory FigCraft engine rules and UI design guidelines (transparent layout wrappers, "
            "alignment enums, strokeWeight/fontStyle naming, and batching best practices)."
        ),
        "mimeType": "text/markdown",
    },
    {
        "uri": "figcraft://canvas/semantic",
        "name": "canvas_semantic_ast",
        "title": "Active Canvas Semantic AST",
        "description": (
            "Compact semantic UI token tree extracted from the active FigCraft document, "
            "stripping noisy coordinates and internal metadata for fast design-to-code analysis."
        ),
        "mimeType": "application/json",
    },
]

CUSTOM_RESOURCE_TEMPLATES: list[dict[str, Any]] = [
    {
        "uriTemplate": "figcraft://node/{id}/semantic",
        "name": "node_semantic_ast",
        "title": "Layer Semantic AST",
        "description": (
            "Compact semantic UI token tree for a single FigCraft layer and its children "
            "(flex direction, padding, gap, colors, typography, radius)."
        ),
        "mimeType": "application/json",
    },
]

CUSTOM_PROMPTS: list[dict[str, Any]] = [
    {
        "name": "figcraft_dashboard_card",
        "title": "Design Analytics Metric Card",
        "description": (
            "Generate a crisp dark or light analytics metric card on the FigCraft canvas "
            "using standard design tokens and single-undo batching."
        ),
        "arguments": [
            {
                "name": "metric_name",
                "description": "Metric title, e.g. 'Monthly Recurring Revenue' or 'Active Users'",
                "required": True,
            },
            {
                "name": "metric_value",
                "description": "Primary metric figure, e.g. '$148,520' or '24,810'",
                "required": True,
            },
            {
                "name": "trend",
                "description": "Trend badge text, e.g. '+18.4%' (default '+12.4%')",
                "required": False,
            },
            {
                "name": "theme",
                "description": "Color theme: 'dark' or 'light' (default 'dark')",
                "required": False,
            },
        ],
    },
    {
        "name": "figcraft_auth_screen",
        "title": "Design Authentication Card",
        "description": (
            "Generate a structured login or registration card with labeled inputs, CTA button, "
            "and proper FigCraft auto-layout rules."
        ),
        "arguments": [
            {
                "name": "brand_name",
                "description": "Product or brand name shown in the card header",
                "required": True,
            },
            {
                "name": "mode",
                "description": "Flow type: 'login' or 'register' (default 'login')",
                "required": False,
            },
            {
                "name": "theme",
                "description": "Color theme: 'dark' or 'light' (default 'dark')",
                "required": False,
            },
        ],
    },
    {
        "name": "figcraft_navbar",
        "title": "Design Desktop Top Navbar",
        "description": (
            "Generate a horizontal desktop navigation bar with logo, navigation links, "
            "and primary CTA button using transparent flex wrappers."
        ),
        "arguments": [
            {
                "name": "brand_name",
                "description": "Brand or logo text on the left side",
                "required": True,
            },
            {
                "name": "links",
                "description": "Comma-separated nav links (default 'Products, Solutions, Pricing, Docs')",
                "required": False,
            },
            {
                "name": "cta_label",
                "description": "Primary CTA button text (default 'Get Started')",
                "required": False,
            },
            {
                "name": "theme",
                "description": "Color theme: 'dark' or 'light' (default 'dark')",
                "required": False,
            },
        ],
    },
    {
        "name": "figcraft_design_to_code",
        "title": "Convert FigCraft Node to Frontend Code",
        "description": (
            "Extract semantic UI tokens from a FigCraft node and convert them into "
            "idiomatic production frontend component code."
        ),
        "arguments": [
            {
                "name": "node_id",
                "description": "Numeric FigCraft layer ID to inspect and convert",
                "required": True,
            },
            {
                "name": "framework",
                "description": "Target framework: 'react-tailwind', 'flutter', 'vue', or 'html-css' (default 'react-tailwind')",
                "required": False,
            },
        ],
    },
]

CUSTOM_TOOLS: list[dict[str, Any]] = [
    {
        "name": "figcraft_get_tokens",
        "title": "Get Design Tokens",
        "description": (
            "Read FigCraft design tokens (colors, spacing, radius, typography, fontWeight) "
            "from tokens.json. Supports optional category filtering and JSON or Markdown output. "
            "Does not launch the FigCraft GUI."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "enum": ["colors", "themes", "semantic", "spacing", "radius", "typography", "fontWeight"],
                    "description": "Optional token category to return. Omit to return all categories.",
                },
                "response_format": {
                    "type": "string",
                    "enum": ["json", "markdown"],
                    "default": "json",
                    "description": "Output format: 'json' (machine-readable) or 'markdown' (human-readable).",
                },
            },
            "additionalProperties": False,
        },
        "annotations": {
            "title": "Get Design Tokens",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "figcraft_extract_semantic_ast",
        "title": "Extract Semantic UI AST",
        "description": (
            "Fetch a FigCraft node (by node_id) or the active document and return a cleaned, "
            "compact semantic UI AST (layout direction, gap, padding, colors, border, typography) "
            "optimized for design-to-code generation."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "node_id": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Optional FigCraft layer ID. Omit to extract the active document.",
                },
                "response_format": {
                    "type": "string",
                    "enum": ["json", "markdown"],
                    "default": "json",
                    "description": "Output format: 'json' (structured AST) or 'markdown' (indented tree summary).",
                },
            },
            "additionalProperties": False,
        },
        "annotations": {
            "title": "Extract Semantic UI AST",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "figcraft_generate_code",
        "title": "Generate Frontend Code from FigCraft Node",
        "description": (
            "Fetch a FigCraft layer by node_id, clean its semantic AST, reverse-map tokens.json "
            "values, extract typed component props (Code Connect pattern), and generate idiomatic "
            "React + Tailwind, Vue 3, Flutter, or semantic HTML/CSS code."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "node_id": {
                    "type": "integer",
                    "minimum": 1,
                    "description": "Numeric FigCraft layer ID to convert into frontend code.",
                },
                "framework": {
                    "type": "string",
                    "enum": list(SUPPORTED_FRAMEWORKS),
                    "default": "react-tailwind",
                    "description": "Target frontend framework: 'react-tailwind', 'vue', 'flutter', or 'html-css'.",
                },
                "component_name": {
                    "type": "string",
                    "description": "Optional PascalCase component name override. Auto-derived from layer name if omitted.",
                },
                "include_props": {
                    "type": "boolean",
                    "default": True,
                    "description": "Extract text layers, slots, and componentPropertyDefinitions into typed props.",
                },
                "response_format": {
                    "type": "string",
                    "enum": ["code", "json"],
                    "default": "code",
                    "description": "'code' returns generated source directly; 'json' returns {component_name, framework, props, code, ast}.",
                },
            },
            "required": ["node_id"],
            "additionalProperties": False,
        },
        "annotations": {
            "title": "Generate Frontend Code from FigCraft Node",
            "readOnlyHint": True,
            "destructiveHint": False,
            "idempotentHint": True,
            "openWorldHint": False,
        },
    },
    {
        "name": "figcraft_render_template",
        "title": "Render Curated UI Component Template",
        "description": (
            "Render a WCAG-verified, anti-slop UI component kit onto the FigCraft canvas "
            "as a single undoable batch operation (buttons, badges, segmented_control, "
            "data_table, state_cards, theme_board, or palette_swatch). Set dry_run=true to "
            "preview the batch JSON without modifying the canvas."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "template": {
                    "type": "string",
                    "enum": list(SUPPORTED_TEMPLATES),
                    "description": "Template name to render onto the canvas.",
                },
                "theme": {
                    "type": "string",
                    "enum": list_themes(),
                    "default": "obsidian-studio",
                    "description": "Curated WCAG AA theme preset.",
                },
                "palette": {
                    "type": "string",
                    "default": "indigo",
                    "description": "Palette name when template='palette_swatch' (e.g. indigo, stone, slate, emerald).",
                },
                "x": {
                    "type": "integer",
                    "description": "Optional page X coordinate override.",
                },
                "y": {
                    "type": "integer",
                    "description": "Optional page Y coordinate override.",
                },
                "dry_run": {
                    "type": "boolean",
                    "default": False,
                    "description": "If true, return the batch command payload JSON without modifying the canvas.",
                },
            },
            "required": ["template"],
            "additionalProperties": False,
        },
        "annotations": {
            "title": "Render Curated UI Component Template",
            "readOnlyHint": False,
            "destructiveHint": False,
            "idempotentHint": False,
            "openWorldHint": False,
        },
    },
]

_MAIN_ALIGN_MAP: dict[str, str] = {
    "start": "min",
    "flex-start": "min",
    "end": "max",
    "flex-end": "max",
    "space-between": "spaceBetween",
    "between": "spaceBetween",
    "space-around": "spaceAround",
    "around": "spaceAround",
    "space-evenly": "spaceEvenly",
    "evenly": "spaceEvenly",
}

_CROSS_ALIGN_MAP: dict[str, str] = {
    "start": "min",
    "flex-start": "min",
    "end": "max",
    "flex-end": "max",
}

_FONT_WEIGHT_MAP: dict[int, str] = {
    100: "Thin",
    200: "ExtraLight",
    300: "Light",
    400: "Regular",
    500: "Medium",
    600: "SemiBold",
    700: "Bold",
    800: "ExtraBold",
    900: "Black",
}

_NODE_SEMANTIC_URI_RE = re.compile(r"^figcraft://node/([^/]+)/semantic$")
_CUSTOM_PROMPT_NAMES = {p["name"] for p in CUSTOM_PROMPTS}
_CUSTOM_TOOL_NAMES = {t["name"] for t in CUSTOM_TOOLS}
_LOCAL_ONLY_TOOLS = {"figcraft_get_tokens"}


def is_custom_tool(name: str) -> bool:
    return name in _CUSTOM_TOOL_NAMES


def is_local_only_tool(name: str) -> bool:
    return name in _LOCAL_ONLY_TOOLS


def is_custom_prompt(name: str) -> bool:
    return name in _CUSTOM_PROMPT_NAMES


def is_custom_resource_uri(uri: str) -> bool:
    if uri in ("figcraft://tokens", "figcraft://guidelines", "figcraft://canvas/semantic"):
        return True
    return bool(_NODE_SEMANTIC_URI_RE.match(uri))


def is_live_canvas_uri(uri: str) -> bool:
    """Return True if reading this URI requires the live attached FigCraft GUI."""
    if uri in ("figcraft://document", "figcraft://comments", "figcraft://canvas/semantic"):
        return True
    if uri.startswith("figcraft://node/"):
        return True
    return False


def _normalize_prop_bag(bag: dict[str, Any]) -> dict[str, Any]:
    """Normalize common LLM property mismatches to exact FigCraft engine property names."""
    out = dict(bag)

    if "strokeWidth" in out:
        val = out.pop("strokeWidth")
        if "strokeWeight" not in out:
            out["strokeWeight"] = val

    if "mainAlign" in out and isinstance(out["mainAlign"], str):
        mapped = _MAIN_ALIGN_MAP.get(out["mainAlign"].strip().lower())
        if mapped:
            out["mainAlign"] = mapped

    if "crossAlign" in out and isinstance(out["crossAlign"], str):
        mapped = _CROSS_ALIGN_MAP.get(out["crossAlign"].strip().lower())
        if mapped:
            out["crossAlign"] = mapped

    if "fontWeight" in out:
        raw_weight = out.pop("fontWeight")
        if "fontStyle" not in out:
            if isinstance(raw_weight, (int, float)):
                nearest = min(_FONT_WEIGHT_MAP.keys(), key=lambda k: abs(k - int(raw_weight)))
                out["fontStyle"] = _FONT_WEIGHT_MAP[nearest]
            elif isinstance(raw_weight, str):
                cleaned = raw_weight.strip()
                if cleaned.isdigit():
                    nearest = min(_FONT_WEIGHT_MAP.keys(), key=lambda k: abs(k - int(cleaned)))
                    out["fontStyle"] = _FONT_WEIGHT_MAP[nearest]
                elif cleaned:
                    out["fontStyle"] = cleaned

    return out


def normalize_tool_call_params(params: dict[str, Any]) -> dict[str, Any]:
    """Return a deep-copied tools/call params dict with FigCraft engine guardrails applied."""
    normalized = copy.deepcopy(params)
    tool_name = normalized.get("name", "")
    arguments = normalized.get("arguments")
    if not isinstance(arguments, dict):
        return normalized

    if tool_name in ("create_node", "set_properties"):
        arguments = _normalize_prop_bag(arguments)
        if isinstance(arguments.get("props"), dict):
            arguments["props"] = _normalize_prop_bag(arguments["props"])
        normalized["arguments"] = arguments

    elif tool_name == "batch":
        commands = arguments.get("commands")
        if isinstance(commands, list):
            new_commands: list[Any] = []
            for step in commands:
                if isinstance(step, dict):
                    step_copy = dict(step)
                    step_params = step_copy.get("params")
                    if isinstance(step_params, dict):
                        step_params = _normalize_prop_bag(step_params)
                        if isinstance(step_params.get("props"), dict):
                            step_params["props"] = _normalize_prop_bag(step_params["props"])
                        step_copy["params"] = step_params
                    new_commands.append(step_copy)
                else:
                    new_commands.append(step)
            arguments["commands"] = new_commands

    return normalized


def _clean_node_preserving_id(node: dict[str, Any]) -> dict[str, Any]:
    """Wrap codegen_helper.clean_node while preserving numeric/string layer IDs."""
    cleaned = clean_node(node)
    if "id" in node:
        cleaned = {"id": node["id"], **cleaned}

    raw_children = node.get("children")
    if isinstance(raw_children, list) and raw_children:
        cleaned["children"] = [
            _clean_node_preserving_id(c) for c in raw_children if isinstance(c, dict)
        ]
    return cleaned


def clean_document_ast(doc: dict[str, Any]) -> dict[str, Any]:
    """Extract compact semantic AST from an inspect_document JSON payload."""
    pages_out: list[dict[str, Any]] = []
    for page in doc.get("pages", []):
        if not isinstance(page, dict):
            continue
        page_entry: dict[str, Any] = {
            "id": page.get("id"),
            "name": page.get("name", ""),
        }
        if "background" in page:
            page_entry["background"] = page["background"]
        children = page.get("children", [])
        if isinstance(children, list):
            page_entry["children"] = [
                _clean_node_preserving_id(c) for c in children if isinstance(c, dict)
            ]
        else:
            page_entry["children"] = []
        pages_out.append(page_entry)

    return {
        "document": doc.get("name", "Untitled"),
        "currentPage": doc.get("currentPage"),
        "selection": doc.get("selection", []),
        "pages": pages_out,
    }


def _load_tokens_json() -> dict[str, Any]:
    if not TOKENS_PATH.is_file():
        raise FileNotFoundError(
            f"tokens.json not found at {TOKENS_PATH}. Ensure the repository files are intact."
        )
    return json.loads(TOKENS_PATH.read_text(encoding="utf-8"))


def format_tokens_markdown(tokens_data: dict[str, Any], category: str | None = None) -> str:
    """Format design tokens as concise Markdown for human/LLM inspection."""
    lines: list[str] = [f"# {tokens_data.get('name', 'FigCraft Design Tokens')}"]
    categories = [category] if category else ["colors", "themes", "semantic", "spacing", "radius", "typography", "fontWeight"]

    for cat in categories:
        if cat not in tokens_data:
            continue
        section = tokens_data[cat]
        lines.append(f"\n## {cat}")
        if cat == "colors" and isinstance(section, dict):
            for palette, shades in section.items():
                if isinstance(shades, dict):
                    swatch_str = ", ".join(f"{k}: `{v}`" for k, v in shades.items())
                    lines.append(f"- **{palette}**: {swatch_str}")
        elif cat == "themes" and isinstance(section, dict):
            for t_name, t_spec in section.items():
                if isinstance(t_spec, dict):
                    lines.append(
                        f"- **{t_name}** ({t_spec.get('mode')}): surface `{t_spec.get('surface')}`, "
                        f"elevated `{t_spec.get('surfaceElevated')}`, accent `{t_spec.get('accent')}` - {t_spec.get('description', '')}"
                    )
        elif cat == "semantic" and isinstance(section, dict):
            for mode, statuses in section.items():
                if isinstance(statuses, dict):
                    st_str = ", ".join(f"{k}({v.get('fg')} on {v.get('bg')})" for k, v in statuses.items())
                    lines.append(f"- **{mode}**: {st_str}")
        elif cat == "typography" and isinstance(section, dict):
            for scale, spec in section.items():
                if isinstance(spec, dict):
                    lines.append(
                        f"- **{scale}**: size `{spec.get('size')}px`, lineHeight `{spec.get('lineHeight')}px`"
                    )
        elif isinstance(section, dict):
            items_str = ", ".join(f"{k}: `{v}`" for k, v in section.items())
            lines.append(f"- {items_str}")

    return "\n".join(lines)


def format_ast_markdown(node: dict[str, Any], depth: int = 0) -> str:
    """Format a semantic AST node or document as a readable indented Markdown tree."""
    if "pages" in node and isinstance(node["pages"], list):
        lines = [f"# Document: {node.get('document', 'Untitled')}"]
        for page in node["pages"]:
            lines.append(
                f"\n## Page: {page.get('name', 'Page')} (id={page.get('id')}, bg={page.get('background', 'none')})"
            )
            children = page.get("children", [])
            if not children:
                lines.append("- *(empty page)*")
            else:
                for child in children:
                    lines.append(format_ast_markdown(child, depth=0))
        return "\n".join(lines)

    indent = "  " * depth
    node_id = node.get("id")
    id_part = f"#{node_id} " if node_id is not None else ""
    header = f"{indent}- **{id_part}{node.get('name') or 'Unnamed'}** (`{node.get('type', 'frame')}`)"

    attrs: list[str] = []
    if "w" in node and "h" in node:
        attrs.append(f"{node['w']}x{node['h']}")
    if "direction" in node:
        attrs.append(f"flex-{node['direction']}")
    if "gap" in node:
        attrs.append(f"gap={node['gap']}")
    if "p" in node:
        attrs.append(f"p={node['p']}")
    if "bg" in node:
        attrs.append(f"bg={node['bg']}")
    if "color" in node:
        attrs.append(f"color={node['color']}")
    if "rounded" in node:
        attrs.append(f"rounded={node['rounded']}")
    if "fontSize" in node:
        attrs.append(f"font={node['fontSize']}px")
    if "fontStyle" in node:
        attrs.append(f"style={node['fontStyle']}")
    if "text" in node:
        preview = str(node["text"]).replace("\n", " ")[:60]
        attrs.append(f'text="{preview}"')

    line = f"{header}: {', '.join(attrs)}" if attrs else header
    lines = [line]
    for child in node.get("children", []):
        if isinstance(child, dict):
            lines.append(format_ast_markdown(child, depth=depth + 1))
    return "\n".join(lines)


def _fetch_upstream_tool_json(
    upstream_call: UpstreamCaller, tool_name: str, arguments: dict[str, Any]
) -> dict[str, Any]:
    """Call an upstream FigCraft tool and decode its JSON text payload."""
    resp = upstream_call("tools/call", {"name": tool_name, "arguments": arguments})
    if "error" in resp:
        err = resp["error"]
        msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
        raise RuntimeError(f"Upstream {tool_name} failed: {msg}")

    result = resp.get("result", {})
    if result.get("isError"):
        content = result.get("content", [])
        err_text = content[0].get("text", "Unknown FigCraft error") if content else "Unknown FigCraft error"
        raise RuntimeError(err_text)

    content = result.get("content", [])
    if not content or content[0].get("type") != "text":
        raise RuntimeError(f"Upstream {tool_name} returned empty or non-text content.")

    data = json.loads(content[0]["text"])
    if not isinstance(data, dict):
        raise RuntimeError(f"Upstream {tool_name} returned non-object JSON payload.")
    return data


def handle_custom_resource_read(uri: str, upstream_call: UpstreamCaller) -> dict[str, Any]:
    """Resolve custom bridge resource URIs into MCP resources/read result payloads."""
    if uri == "figcraft://tokens":
        tokens_data = _load_tokens_json()
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(tokens_data, indent=2),
                }
            ]
        }

    if uri == "figcraft://guidelines":
        if not GUIDELINES_PATH.is_file():
            raise FileNotFoundError(
                f"Guidelines file not found at {GUIDELINES_PATH}."
            )
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "text/markdown",
                    "text": GUIDELINES_PATH.read_text(encoding="utf-8"),
                }
            ]
        }

    if uri == "figcraft://canvas/semantic":
        raw_doc = _fetch_upstream_tool_json(upstream_call, "inspect_document", {})
        semantic_doc = clean_document_ast(raw_doc)
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(semantic_doc, indent=2),
                }
            ]
        }

    match = _NODE_SEMANTIC_URI_RE.match(uri)
    if match:
        raw_id = match.group(1)
        if not raw_id.isdigit() or int(raw_id) <= 0:
            raise ValueError(
                f"Invalid node ID '{raw_id}' in URI '{uri}'. Expected a positive integer, e.g. figcraft://node/125/semantic."
            )
        node_id = int(raw_id)
        raw_payload = _fetch_upstream_tool_json(upstream_call, "get_node", {"id": node_id})
        raw_node = raw_payload.get("node", raw_payload)
        semantic_node = _clean_node_preserving_id(raw_node)
        return {
            "contents": [
                {
                    "uri": uri,
                    "mimeType": "application/json",
                    "text": json.dumps(semantic_node, indent=2),
                }
            ]
        }

    raise ValueError(f"Unknown custom resource URI: {uri}")


def handle_custom_prompt_get(name: str, arguments: dict[str, Any] | None) -> dict[str, Any]:
    """Render a custom FigCraft prompt template into an MCP prompts/get result."""
    args = arguments or {}

    if name == "figcraft_dashboard_card":
        metric_name = str(args.get("metric_name", "")).strip()
        metric_value = str(args.get("metric_value", "")).strip()
        if not metric_name or not metric_value:
            raise ValueError(
                "Missing required arguments for 'figcraft_dashboard_card': "
                "provide both 'metric_name' and 'metric_value'."
            )
        trend = str(args.get("trend", "+12.4%")).strip() or "+12.4%"
        theme = str(args.get("theme", "dark")).strip().lower()
        bg, border, title_c, value_c, badge_bg, badge_fg = (
            ("#FFFFFF", "#E2E8F0", "#64748B", "#0F172A", "#DCFCE7", "#15803D")
            if theme == "light"
            else ("#1E293B", "#334155", "#94A3B8", "#F8FAFC", "#064E3B", "#34D399")
        )
        prompt_text = (
            f"Create an analytics metric card in FigCraft using a single `batch` call (`onError: \"abort\"`):\n"
            f"- Container frame: name 'Metric Card - {metric_name}', vertical auto-layout, width 280, padding 20, "
            f"gap 12, cornerRadius 14, fill '{bg}', stroke '{border}', strokeWeight 1.\n"
            f"- Header wrapper frame: horizontal auto-layout, mainAlign 'spaceBetween', crossAlign 'center', "
            f"fill 'none' (mandatory transparent wrapper).\n"
            f"  - Title text: '{metric_name}', fontSize 13, fontStyle 'Medium', fill '{title_c}'.\n"
            f"  - Trend badge frame: fill '{badge_bg}', cornerRadius 6, padding 6, containing text '{trend}' "
            f"at fontSize 11, fontStyle 'SemiBold', fill '{badge_fg}'.\n"
            f"- Main metric text: '{metric_value}', fontSize 28, fontStyle 'Bold', fill '{value_c}'.\n"
            f"- After creation, call `screenshot` on the created frame ID to verify spacing and contrast."
        )
        return {
            "description": f"Build analytics metric card for {metric_name}",
            "messages": [{"role": "user", "content": {"type": "text", "text": prompt_text}}],
        }

    if name == "figcraft_auth_screen":
        brand_name = str(args.get("brand_name", "")).strip()
        if not brand_name:
            raise ValueError(
                "Missing required argument for 'figcraft_auth_screen': provide 'brand_name'."
            )
        mode = str(args.get("mode", "login")).strip().lower()
        theme = str(args.get("theme", "dark")).strip().lower()
        is_register = mode == "register"
        heading = f"Create your {brand_name} account" if is_register else f"Sign in to {brand_name}"
        cta = "Create Account" if is_register else "Sign In"
        bg, border, input_bg, fg, muted = (
            ("#FFFFFF", "#E2E8F0", "#F8FAFC", "#0F172A", "#64748B")
            if theme == "light"
            else ("#18181B", "#27272A", "#27272A", "#FAFAFA", "#A1A1AA")
        )
        extra_field = "- Full Name input group (label 'Full Name', input height 44).\n" if is_register else ""
        prompt_text = (
            f"Design a {theme}-mode {mode} card for '{brand_name}' in FigCraft using `batch` (`onError: \"abort\"`):\n"
            f"- Card container: vertical auto-layout, width 400, padding 32, gap 16, cornerRadius 16, "
            f"fill '{bg}', stroke '{border}', strokeWeight 1.\n"
            f"- Header group (`fill: \"none\"`, vertical, gap 6): title '{heading}' (fontSize 22, fontStyle 'Bold', fill '{fg}') "
            f"and subtitle (fontSize 13, fill '{muted}').\n"
            f"{extra_field}"
            f"- Email input group (`fill: \"none\"`, vertical, gap 6): label 'Email' (12px) + input frame (height 44, fill '{input_bg}', cornerRadius 8, padding 12).\n"
            f"- Password input group (`fill: \"none\"`, vertical, gap 6): label 'Password' (12px) + input frame (height 44, fill '{input_bg}', cornerRadius 8, padding 12).\n"
            f"- CTA button frame: height 44, fill '#4F46E5', cornerRadius 8, mainAlign 'center', crossAlign 'center', "
            f"with text '{cta}' (fontSize 14, fontStyle 'SemiBold', fill '#FFFFFF').\n"
            f"- Verify the rendered frame with `screenshot`."
        )
        return {
            "description": f"Build {mode} authentication card for {brand_name}",
            "messages": [{"role": "user", "content": {"type": "text", "text": prompt_text}}],
        }

    if name == "figcraft_navbar":
        brand_name = str(args.get("brand_name", "")).strip()
        if not brand_name:
            raise ValueError(
                "Missing required argument for 'figcraft_navbar': provide 'brand_name'."
            )
        links = str(args.get("links", "Products, Solutions, Pricing, Docs")).strip()
        cta_label = str(args.get("cta_label", "Get Started")).strip() or "Get Started"
        theme = str(args.get("theme", "dark")).strip().lower()
        bg, fg, muted, border = (
            ("#FFFFFF", "#0F172A", "#475569", "#E2E8F0")
            if theme == "light"
            else ("#0F172A", "#F8FAFC", "#94A3B8", "#1E293B")
        )
        prompt_text = (
            f"Design a desktop Top Navbar in FigCraft using a single `batch` call (`onError: \"abort\"`):\n"
            f"- Main container: horizontal auto-layout, width 1200, height 72, padding 24, "
            f"mainAlign 'spaceBetween', crossAlign 'center', fill '{bg}', stroke '{border}', strokeWeight 1.\n"
            f"- Left logo text: '{brand_name}', fontSize 20, fontStyle 'Bold', fill '{fg}'.\n"
            f"- Center links wrapper: horizontal auto-layout, gap 28, crossAlign 'center', fill 'none' "
            f"(transparent wrapper) with links [{links}] at fontSize 14, fontStyle 'Medium', fill '{muted}'.\n"
            f"- Right CTA button: fill '#6366F1', cornerRadius 8, padding 12, mainAlign 'center', crossAlign 'center', "
            f"text '{cta_label}' at fontSize 14, fontStyle 'SemiBold', fill '#FFFFFF'.\n"
            f"- Verify layout alignment using `screenshot`."
        )
        return {
            "description": f"Build desktop top navbar for {brand_name}",
            "messages": [{"role": "user", "content": {"type": "text", "text": prompt_text}}],
        }

    if name == "figcraft_design_to_code":
        raw_node_id = str(args.get("node_id", "")).strip()
        if not raw_node_id.isdigit():
            raise ValueError(
                "Invalid or missing 'node_id' for 'figcraft_design_to_code': expected a numeric layer ID."
            )
        framework = str(args.get("framework", "react-tailwind")).strip().lower() or "react-tailwind"
        prompt_text = (
            f"Convert FigCraft layer #{raw_node_id} into production-grade `{framework}` code:\n"
            f"1. Call tool `figcraft_generate_code` with `node_id: {raw_node_id}` and `framework: \"{framework}\"` "
            f"(or inspect `figcraft://node/{raw_node_id}/semantic` directly).\n"
            f"2. Optionally read `figcraft://tokens` to verify named token mappings.\n"
            f"3. Capture a reference visual with `screenshot` for layer {raw_node_id}.\n"
            f"4. Review and refine the generated `{framework}` component preserving typed props, "
            f"flex direction, padding, gap, typography scale, and accessibility."
        )
        return {
            "description": f"Convert FigCraft node #{raw_node_id} to {framework}",
            "messages": [{"role": "user", "content": {"type": "text", "text": prompt_text}}],
        }

    raise ValueError(f"Unknown custom prompt: {name}")


def handle_custom_tool_call(
    name: str,
    arguments: dict[str, Any] | None,
    upstream_call: UpstreamCaller,
) -> dict[str, Any]:
    """Execute custom bridge workflow tools and return MCP tools/call result objects."""
    args = arguments or {}

    if name == "figcraft_get_tokens":
        category = args.get("category")
        response_format = str(args.get("response_format", "json")).strip().lower()
        valid_categories = {"colors", "themes", "semantic", "spacing", "radius", "typography", "fontWeight"}

        if response_format not in ("json", "markdown"):
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Invalid response_format '{response_format}'. "
                            "Use 'json' or 'markdown'."
                        ),
                    }
                ],
            }

        if category is not None and category not in valid_categories:
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Invalid token category '{category}'. "
                            f"Choose one of: {', '.join(sorted(valid_categories))}."
                        ),
                    }
                ],
            }

        try:
            tokens_data = _load_tokens_json()
            if response_format == "markdown":
                text = format_tokens_markdown(tokens_data, category=category)
            else:
                payload = {category: tokens_data[category]} if category else tokens_data
                text = json.dumps(payload, indent=2)
            return {"content": [{"type": "text", "text": text}]}
        except Exception as e:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Failed to load design tokens: {e}"}],
            }

    if name == "figcraft_extract_semantic_ast":
        node_id = args.get("node_id")
        response_format = str(args.get("response_format", "json")).strip().lower()

        if response_format not in ("json", "markdown"):
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Invalid response_format '{response_format}'. "
                            "Use 'json' or 'markdown'."
                        ),
                    }
                ],
            }

        if node_id is not None and (isinstance(node_id, bool) or not isinstance(node_id, int) or node_id <= 0):
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Invalid node_id '{node_id}'. Provide a positive integer layer ID "
                            "or omit node_id to inspect the active document."
                        ),
                    }
                ],
            }

        try:
            if node_id is not None:
                raw_payload = _fetch_upstream_tool_json(upstream_call, "get_node", {"id": node_id})
                raw_node = raw_payload.get("node", raw_payload)
                ast_data = _clean_node_preserving_id(raw_node)
            else:
                raw_doc = _fetch_upstream_tool_json(upstream_call, "inspect_document", {})
                ast_data = clean_document_ast(raw_doc)

            text = (
                format_ast_markdown(ast_data)
                if response_format == "markdown"
                else json.dumps(ast_data, indent=2)
            )
            return {"content": [{"type": "text", "text": text}]}
        except Exception as e:
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Failed to extract semantic AST: {e}. "
                            "Verify the node_id exists using inspect_document first."
                        ),
                    }
                ],
            }

    if name == "figcraft_generate_code":
        node_id = args.get("node_id")
        framework = str(args.get("framework", "react-tailwind")).strip().lower()
        component_name = args.get("component_name")
        include_props = args.get("include_props", True)
        response_format = str(args.get("response_format", "code")).strip().lower()

        if node_id is None or isinstance(node_id, bool) or not isinstance(node_id, int) or node_id <= 0:
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Invalid or missing node_id '{node_id}'. Provide a positive integer layer ID "
                            "(find IDs via figcraft://canvas/semantic or inspect_document)."
                        ),
                    }
                ],
            }

        if framework not in SUPPORTED_FRAMEWORKS:
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Unsupported framework '{framework}'. "
                            f"Choose one of: {', '.join(SUPPORTED_FRAMEWORKS)}."
                        ),
                    }
                ],
            }

        if response_format not in ("code", "json"):
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"Invalid response_format '{response_format}'. Use 'code' or 'json'.",
                    }
                ],
            }

        if not isinstance(include_props, bool):
            return {
                "isError": True,
                "content": [{"type": "text", "text": "Invalid include_props: expected boolean."}],
            }

        try:
            raw_payload = _fetch_upstream_tool_json(upstream_call, "get_node", {"id": node_id})
            raw_node = raw_payload.get("node", raw_payload)
            ast_data = _clean_node_preserving_id(raw_node)
            generated = generate_code(
                ast_data,
                framework=framework,
                component_name=str(component_name) if component_name else None,
                include_props=include_props,
            )
            if response_format == "json":
                payload = {**generated, "ast": ast_data}
                return {"content": [{"type": "text", "text": json.dumps(payload, indent=2)}]}
            return {"content": [{"type": "text", "text": generated["code"]}]}
        except Exception as e:
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": (
                            f"Failed to generate {framework} code for node {node_id}: {e}. "
                            "Verify the node_id exists using figcraft://canvas/semantic first."
                        ),
                    }
                ],
            }

    if name == "figcraft_render_template":
        template_name = str(args.get("template", "")).strip().lower()
        theme_name = str(args.get("theme", "obsidian-studio")).strip().lower()
        palette_name = str(args.get("palette", "indigo")).strip().lower()
        x = args.get("x")
        y = args.get("y")
        dry_run = args.get("dry_run", False)

        if not isinstance(dry_run, bool):
            return {
                "isError": True,
                "content": [{"type": "text", "text": "Invalid dry_run: expected boolean."}],
            }
        if x is not None and (isinstance(x, bool) or not isinstance(x, int)):
            return {
                "isError": True,
                "content": [{"type": "text", "text": "Invalid x: expected integer."}],
            }
        if y is not None and (isinstance(y, bool) or not isinstance(y, int)):
            return {
                "isError": True,
                "content": [{"type": "text", "text": "Invalid y: expected integer."}],
            }

        try:
            commands = build_template_commands(
                template_name,
                theme_name=theme_name,
                palette_name=palette_name,
                x=x,
                y=y,
            )
        except ValueError as exc:
            return {
                "isError": True,
                "content": [{"type": "text", "text": str(exc)}],
            }

        if dry_run:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(
                            {
                                "template": template_name,
                                "theme": theme_name,
                                "stepCount": len(commands),
                                "commands": commands,
                            },
                            indent=2,
                        ),
                    }
                ]
            }

        try:
            resp = upstream_call(
                "tools/call",
                {
                    "name": "batch",
                    "arguments": {
                        "commands": commands,
                        "onError": "abort",
                        "label": f"Render {template_name} ({theme_name})",
                    },
                },
            )
            if "error" in resp:
                err = resp["error"]
                msg = err.get("message", str(err)) if isinstance(err, dict) else str(err)
                return {
                    "isError": True,
                    "content": [{"type": "text", "text": f"Failed to render template '{template_name}': {msg}"}],
                }
            return resp.get("result", {"content": [{"type": "text", "text": "Rendered template."}]})
        except Exception as exc:
            return {
                "isError": True,
                "content": [{"type": "text", "text": f"Failed to render template '{template_name}': {exc}"}],
            }

    return {
        "isError": True,
        "content": [{"type": "text", "text": f"Unknown custom bridge tool: {name}"}],
    }


def merge_initialize_result(result: dict[str, Any]) -> dict[str, Any]:
    """Augment initialize result with bridge capabilities and FigCraft engine guardrail instructions."""
    merged = copy.deepcopy(result)
    caps = merged.setdefault("capabilities", {})
    caps.setdefault("resources", {"listChanged": False, "subscribe": False})
    caps.setdefault("prompts", {"listChanged": False})
    caps.setdefault("tools", {"listChanged": False})

    instructions = merged.get("instructions", "")
    if "[FigCraft Bridge Primitives & Engine Rules]" not in instructions:
        merged["instructions"] = instructions + ENGINE_GUARDRAIL_INSTRUCTIONS
    return merged


def merge_tools_list(result: dict[str, Any]) -> dict[str, Any]:
    """Append custom bridge tools to upstream tools/list result without duplicates."""
    merged = copy.deepcopy(result)
    tools = merged.setdefault("tools", [])
    existing = {t.get("name") for t in tools if isinstance(t, dict)}
    for tool in CUSTOM_TOOLS:
        if tool["name"] not in existing:
            tools.append(copy.deepcopy(tool))
    return merged


def merge_resources_list(result: dict[str, Any]) -> dict[str, Any]:
    """Append custom bridge resources to upstream resources/list result without duplicates."""
    merged = copy.deepcopy(result)
    resources = merged.setdefault("resources", [])
    existing = {r.get("uri") for r in resources if isinstance(r, dict)}
    for res in CUSTOM_RESOURCES:
        if res["uri"] not in existing:
            resources.append(copy.deepcopy(res))
    return merged


def merge_resource_templates_list(result: dict[str, Any]) -> dict[str, Any]:
    """Append custom bridge resource templates to upstream resources/templates/list result."""
    merged = copy.deepcopy(result)
    templates = merged.setdefault("resourceTemplates", [])
    existing = {t.get("uriTemplate") for t in templates if isinstance(t, dict)}
    for tmpl in CUSTOM_RESOURCE_TEMPLATES:
        if tmpl["uriTemplate"] not in existing:
            templates.append(copy.deepcopy(tmpl))
    return merged


def merge_prompts_list(result: dict[str, Any]) -> dict[str, Any]:
    """Append custom bridge prompts to upstream prompts/list result without duplicates."""
    merged = copy.deepcopy(result)
    prompts = merged.setdefault("prompts", [])
    existing = {p.get("name") for p in prompts if isinstance(p, dict)}
    for prompt in CUSTOM_PROMPTS:
        if prompt["name"] not in existing:
            prompts.append(copy.deepcopy(prompt))
    return merged
