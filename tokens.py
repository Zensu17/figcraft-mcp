#!/usr/bin/env python3
"""
FigCraft Standard Design Tokens, Themes & Canvas Component Templates
--------------------------------------------------------------------
Provides a curated design tokens API, WCAG AA contrast verification, CSS/Tailwind
exporters, and pure FigCraft batch builders for reusable, anti-slop UI components
(palette swatches, buttons, status badges, segmented controls, data tables, UI state
kits, and theme specimens).

Zero external dependencies: 100% Python standard library.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
TOKENS_FILE = SCRIPT_DIR / "tokens.json"
BRIDGE_PATH = SCRIPT_DIR / "bridge.py"

GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
BOLD = "\033[1m"
RESET = "\033[0m"

SUPPORTED_TEMPLATES: tuple[str, ...] = (
    "palette_swatch",
    "buttons",
    "badges",
    "segmented_control",
    "data_table",
    "state_cards",
    "theme_board",
)

_TOKENS: dict[str, Any] | None = None


def load_tokens() -> dict[str, Any]:
    """Load tokens.json from disk."""
    if not TOKENS_FILE.is_file():
        raise FileNotFoundError(f"tokens.json not found at: {TOKENS_FILE}")
    with open(TOKENS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def get_tokens() -> dict[str, Any]:
    global _TOKENS
    if _TOKENS is None:
        _TOKENS = load_tokens()
    return _TOKENS


def reload_tokens() -> dict[str, Any]:
    global _TOKENS
    _TOKENS = load_tokens()
    return _TOKENS


def get_color(name_or_key: str, default: str = "#000000") -> str:
    """Get hex color by shade key, e.g. 'indigo-500', 'slate.900', or 'emerald'."""
    tokens = get_tokens().get("colors", {})
    cleaned = name_or_key.replace(".", "-").strip().lower()
    if "-" in cleaned:
        palette, shade = cleaned.split("-", 1)
    else:
        palette, shade = cleaned, "500"
    return tokens.get(palette, {}).get(shade, default)


def get_spacing(key: str | int, default: int = 16) -> int:
    """Get spacing in pixels by scale key, e.g. '4' -> 16, '8' -> 32."""
    spacing = get_tokens().get("spacing", {})
    return spacing.get(str(key), default)


def get_radius(key: str, default: int = 8) -> int:
    """Get border radius in pixels by key, e.g. 'lg' -> 8, 'full' -> 9999."""
    radius = get_tokens().get("radius", {})
    return radius.get(key.lower(), default)


def get_typography(key: str) -> dict[str, int]:
    """Get typography specs (size, lineHeight) by key, e.g. 'base', 'xl'."""
    typo = get_tokens().get("typography", {})
    return typo.get(key.lower(), {"size": 16, "lineHeight": 24})


def list_themes() -> list[str]:
    """Return all available theme preset names."""
    return list(get_tokens().get("themes", {}).keys())


def get_theme(theme_name: str = "obsidian-studio") -> dict[str, Any]:
    """Retrieve a named visual theme preset with explicit error on unknown theme."""
    themes = get_tokens().get("themes", {})
    key = theme_name.strip().lower()
    if key not in themes:
        raise ValueError(
            f"Unknown theme '{theme_name}'. Available themes: {', '.join(themes.keys())}."
        )
    return themes[key]


def get_semantic_tokens(mode: str = "dark") -> dict[str, dict[str, str]]:
    """Retrieve WCAG-verified status tokens for 'dark' or 'light' mode."""
    sem = get_tokens().get("semantic", {})
    return sem.get(mode if mode in ("dark", "light") else "dark", {})


# ---------------------------------------------------------------------------
# WCAG 2.2 Contrast Ratio Utilities
# ---------------------------------------------------------------------------

def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    cleaned = hex_color.strip().lstrip("#")
    if len(cleaned) != 6:
        raise ValueError(f"Expected 6-digit hex color, got '{hex_color}'.")
    return (int(cleaned[0:2], 16), int(cleaned[2:4], 16), int(cleaned[4:6], 16))


def _relative_luminance(hex_color: str) -> float:
    r, g, b = _hex_to_rgb(hex_color)

    def channel(c: int) -> float:
        s = c / 255.0
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def contrast_ratio(fg_hex: str, bg_hex: str) -> float:
    """Compute WCAG 2.2 contrast ratio between two 6-digit hex colors (1.0 to 21.0)."""
    l1 = _relative_luminance(fg_hex)
    l2 = _relative_luminance(bg_hex)
    lighter, darker = max(l1, l2), min(l1, l2)
    return round((lighter + 0.05) / (darker + 0.05), 2)


def check_wcag_aa(fg_hex: str, bg_hex: str, large_text: bool = False) -> bool:
    """Return True if fg/bg pair satisfies WCAG 2.2 AA (4.5:1 normal, 3.0:1 large)."""
    threshold = 3.0 if large_text else 4.5
    return contrast_ratio(fg_hex, bg_hex) >= threshold


def audit_theme_contrast() -> list[dict[str, Any]]:
    """Audit all theme and semantic color pairs against WCAG 2.2 AA (4.5:1)."""
    results: list[dict[str, Any]] = []
    tokens = get_tokens()

    for theme_name, t in tokens.get("themes", {}).items():
        pairs = [
            ("textPrimary on surface", t["textPrimary"], t["surface"]),
            ("textPrimary on surfaceElevated", t["textPrimary"], t["surfaceElevated"]),
            ("textMuted on surface", t["textMuted"], t["surface"]),
            ("textMuted on surfaceElevated", t["textMuted"], t["surfaceElevated"]),
            ("onAccent on accent", t["onAccent"], t["accent"]),
            ("onDanger on danger", t["onDanger"], t["danger"]),
        ]
        for label, fg, bg in pairs:
            ratio = contrast_ratio(fg, bg)
            results.append({
                "scope": f"theme:{theme_name}",
                "pair": label,
                "fg": fg,
                "bg": bg,
                "ratio": ratio,
                "pass_aa": ratio >= 4.5,
            })

    for mode, statuses in tokens.get("semantic", {}).items():
        for status_name, spec in statuses.items():
            ratio = contrast_ratio(spec["fg"], spec["bg"])
            results.append({
                "scope": f"semantic:{mode}",
                "pair": f"{status_name} fg on bg",
                "fg": spec["fg"],
                "bg": spec["bg"],
                "ratio": ratio,
                "pass_aa": ratio >= 4.5,
            })

    return results


# ---------------------------------------------------------------------------
# Exporters (Tailwind & CSS Custom Properties)
# ---------------------------------------------------------------------------

def export_tailwind_theme() -> str:
    """Export tokens.json as a theme.extend configuration object for Tailwind CSS."""
    tokens = get_tokens()
    snippet = {
        "theme": {
            "extend": {
                "colors": tokens.get("colors", {}),
                "borderRadius": {k: f"{v}px" for k, v in tokens.get("radius", {}).items()},
                "spacing": {k: f"{v}px" for k, v in tokens.get("spacing", {}).items()},
            }
        }
    }
    return json.dumps(snippet, indent=2)


def export_css_variables(theme_name: str = "obsidian-studio") -> str:
    """Export a theme preset and spacing/radius tokens as CSS custom properties."""
    t = get_theme(theme_name)
    sem = get_semantic_tokens(t["mode"])
    lines = [
        f"/* FigCraft Theme: {theme_name} ({t['mode']}) */",
        ":root {",
        f"  --fc-surface: {t['surface']};",
        f"  --fc-surface-elevated: {t['surfaceElevated']};",
        f"  --fc-surface-subtle: {t['surfaceSubtle']};",
        f"  --fc-border: {t['border']};",
        f"  --fc-border-strong: {t['borderStrong']};",
        f"  --fc-text-primary: {t['textPrimary']};",
        f"  --fc-text-muted: {t['textMuted']};",
        f"  --fc-accent: {t['accent']};",
        f"  --fc-on-accent: {t['onAccent']};",
        f"  --fc-danger: {t['danger']};",
        f"  --fc-on-danger: {t['onDanger']};",
        f"  --fc-radius-card: {t['radiusCard']}px;",
        f"  --fc-radius-control: {t['radiusControl']}px;",
    ]
    for status, spec in sem.items():
        lines.append(f"  --fc-{status}-bg: {spec['bg']};")
        lines.append(f"  --fc-{status}-fg: {spec['fg']};")
    lines.append("}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Pure FigCraft Batch Builders (Valid Engine Schema + $ref Hierarchy)
# ---------------------------------------------------------------------------

def _node_step(
    node_type: str,
    name: str,
    *,
    as_ref: str | None = None,
    parent_ref: str | None = None,
    text: str | None = None,
    x: int | None = None,
    y: int | None = None,
    width: int | None = None,
    height: int | None = None,
    props: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Construct a valid FigCraft batch `node.create` step."""
    params: dict[str, Any] = {"type": node_type, "name": name}
    if parent_ref is not None:
        params["parent"] = {"$ref": parent_ref}
    if text is not None:
        params["text"] = text
    if x is not None:
        params["x"] = x
    if y is not None:
        params["y"] = y
    if width is not None:
        params["width"] = width
    if height is not None:
        params["height"] = height
    if props:
        params["props"] = props

    step: dict[str, Any] = {"command": "node.create", "params": params}
    if as_ref:
        step["as"] = as_ref
    return step


def build_palette_swatch_commands(palette_name: str, x: int = 60, y: int = 60) -> list[dict[str, Any]]:
    """Build FigCraft batch commands for a palette swatch card with WCAG contrast annotations."""
    colors = get_tokens().get("colors", {})
    key = palette_name.strip().lower()
    palette = colors.get(key)
    if not palette:
        raise ValueError(
            f"Palette '{palette_name}' not found. Available: {', '.join(colors.keys())}."
        )

    commands: list[dict[str, Any]] = [
        _node_step(
            "frame",
            f"Palette: {key.capitalize()}",
            as_ref="root",
            x=x,
            y=y,
            width=320,
            height=540,
            props={
                "fill": "#0F172A",
                "stroke": "#334155",
                "strokeWeight": 1,
                "cornerRadius": 14,
                "layout": "vertical",
                "padding": 20,
                "gap": 8,
            },
        ),
        _node_step(
            "text",
            "Palette Title",
            parent_ref="root",
            text=f"{key.capitalize()} Color Scale",
            props={"fontSize": 16, "fontStyle": "Bold", "fill": "#F8FAFC"},
        ),
    ]

    for shade, hex_val in palette.items():
        dark_ratio = contrast_ratio("#09090B", hex_val)
        light_ratio = contrast_ratio("#FFFFFF", hex_val)
        fg = "#09090B" if dark_ratio >= light_ratio else "#FFFFFF"
        best_ratio = max(dark_ratio, light_ratio)
        row_ref = f"swatch_{shade}"
        commands.append(
            _node_step(
                "frame",
                f"Shade {shade}",
                as_ref=row_ref,
                parent_ref="root",
                width=280,
                height=36,
                props={
                    "fill": hex_val,
                    "cornerRadius": 6,
                    "layout": "horizontal",
                    "padding": 10,
                    "mainAlign": "spaceBetween",
                    "crossAlign": "center",
                },
            )
        )
        commands.append(
            _node_step(
                "text",
                f"Shade Code {shade}",
                parent_ref=row_ref,
                text=f"{shade}  {hex_val}",
                props={"fontSize": 12, "fontStyle": "SemiBold", "fill": fg},
            )
        )
        commands.append(
            _node_step(
                "text",
                f"Contrast {shade}",
                parent_ref=row_ref,
                text=f"{best_ratio:.1f}:1",
                props={"fontSize": 11, "fontStyle": "Medium", "fill": fg},
            )
        )

    return commands


def build_starter_buttons_commands(
    theme_name: str = "obsidian-studio", x: int = 420, y: int = 60
) -> list[dict[str, Any]]:
    """Build FigCraft batch commands for 44px-tall accessible button variants."""
    t = get_theme(theme_name)
    r_ctrl = t["radiusControl"]

    variants = [
        ("btn_primary", "Button / Primary", "Save changes", t["accent"], t["onAccent"], None),
        ("btn_secondary", "Button / Secondary", "Export CSV", t["surfaceSubtle"], t["textPrimary"], t["border"]),
        ("btn_outline", "Button / Outline", "Cancel", "none", t["textPrimary"], t["borderStrong"]),
        ("btn_danger", "Button / Destructive", "Delete project", t["danger"], t["onDanger"], None),
    ]

    commands: list[dict[str, Any]] = [
        _node_step(
            "frame",
            f"Buttons ({theme_name})",
            as_ref="root",
            x=x,
            y=y,
            width=340,
            height=330,
            props={
                "fill": t["surfaceElevated"],
                "stroke": t["border"],
                "strokeWeight": 1,
                "cornerRadius": t["radiusCard"],
                "layout": "vertical",
                "padding": 24,
                "gap": 14,
            },
        ),
        _node_step(
            "text",
            "Section Heading",
            parent_ref="root",
            text=f"Button Actions ({theme_name})",
            props={"fontSize": 15, "fontStyle": "Bold", "fill": t["textPrimary"]},
        ),
    ]

    for ref, name, label, fill_c, fg_c, stroke_c in variants:
        btn_props: dict[str, Any] = {
            "fill": fill_c,
            "cornerRadius": r_ctrl,
            "layout": "horizontal",
            "padding": 12,
            "mainAlign": "center",
            "crossAlign": "center",
        }
        if stroke_c:
            btn_props["stroke"] = stroke_c
            btn_props["strokeWeight"] = 1

        commands.append(
            _node_step(
                "frame",
                name,
                as_ref=ref,
                parent_ref="root",
                width=292,
                height=44,
                props=btn_props,
            )
        )
        commands.append(
            _node_step(
                "text",
                f"{name} Label",
                parent_ref=ref,
                text=label,
                props={"fontSize": 14, "fontStyle": "SemiBold", "fill": fg_c},
            )
        )

    return commands


def build_starter_badges_commands(
    theme_name: str = "obsidian-studio", x: int = 800, y: int = 60
) -> list[dict[str, Any]]:
    """Build FigCraft batch commands for functional WCAG AA status badges."""
    t = get_theme(theme_name)
    sem = get_semantic_tokens(t["mode"])

    items = [
        ("badge_success", "Badge / Operational", "Operational", sem["success"]),
        ("badge_warning", "Badge / Pending", "Pending review", sem["warning"]),
        ("badge_danger", "Badge / Failed", "Action failed", sem["danger"]),
        ("badge_info", "Badge / Draft", "Draft saved", sem["info"]),
    ]

    commands: list[dict[str, Any]] = [
        _node_step(
            "frame",
            f"Status Badges ({theme_name})",
            as_ref="root",
            x=x,
            y=y,
            width=280,
            height=260,
            props={
                "fill": t["surfaceElevated"],
                "stroke": t["border"],
                "strokeWeight": 1,
                "cornerRadius": t["radiusCard"],
                "layout": "vertical",
                "padding": 24,
                "gap": 12,
            },
        ),
        _node_step(
            "text",
            "Badges Heading",
            parent_ref="root",
            text="System Status Badges",
            props={"fontSize": 15, "fontStyle": "Bold", "fill": t["textPrimary"]},
        ),
    ]

    for ref, name, label, spec in items:
        commands.append(
            _node_step(
                "frame",
                name,
                as_ref=ref,
                parent_ref="root",
                width=148,
                height=30,
                props={
                    "fill": spec["bg"],
                    "stroke": spec["border"],
                    "strokeWeight": 1,
                    "cornerRadius": 6,
                    "layout": "horizontal",
                    "padding": 8,
                    "mainAlign": "center",
                    "crossAlign": "center",
                },
            )
        )
        commands.append(
            _node_step(
                "text",
                f"{name} Label",
                parent_ref=ref,
                text=label,
                props={"fontSize": 12, "fontStyle": "SemiBold", "fill": spec["fg"]},
            )
        )

    return commands


def build_segmented_control_commands(
    theme_name: str = "obsidian-studio",
    items: list[str] | None = None,
    active_index: int = 0,
    x: int = 60,
    y: int = 640,
) -> list[dict[str, Any]]:
    """Build a crisp segmented tab switcher using transparent/elevated surface contrast."""
    t = get_theme(theme_name)
    labels = items or ["Overview", "Deployments", "Logs"]
    safe_active = max(0, min(active_index, len(labels) - 1))

    commands: list[dict[str, Any]] = [
        _node_step(
            "frame",
            f"Segmented Control ({theme_name})",
            as_ref="root",
            x=x,
            y=y,
            width=360,
            height=48,
            props={
                "fill": t["surfaceSubtle"],
                "stroke": t["border"],
                "strokeWeight": 1,
                "cornerRadius": t["radiusControl"] + 2,
                "layout": "horizontal",
                "padding": 4,
                "gap": 4,
                "mainAlign": "spaceBetween",
                "crossAlign": "center",
            },
        )
    ]

    for idx, label in enumerate(labels):
        is_active = idx == safe_active
        seg_ref = f"seg_{idx}"
        seg_props: dict[str, Any] = {
            "fill": t["surfaceElevated"] if is_active else "none",
            "cornerRadius": t["radiusControl"],
            "layout": "horizontal",
            "padding": 10,
            "mainAlign": "center",
            "crossAlign": "center",
        }
        if is_active:
            seg_props["stroke"] = t["borderStrong"]
            seg_props["strokeWeight"] = 1

        commands.append(
            _node_step(
                "frame",
                f"Segment / {label}",
                as_ref=seg_ref,
                parent_ref="root",
                width=112,
                height=40,
                props=seg_props,
            )
        )
        commands.append(
            _node_step(
                "text",
                f"Segment Label {idx}",
                parent_ref=seg_ref,
                text=label,
                props={
                    "fontSize": 13,
                    "fontStyle": "SemiBold" if is_active else "Medium",
                    "fill": t["textPrimary"] if is_active else t["textMuted"],
                },
            )
        )

    return commands


def build_data_table_commands(
    theme_name: str = "obsidian-studio", x: int = 420, y: int = 440
) -> list[dict[str, Any]]:
    """Build a decision-oriented operational data table with clear columns and status tokens."""
    t = get_theme(theme_name)
    sem = get_semantic_tokens(t["mode"])

    rows = [
        ("build-worker-01", "Failed", "Exit code 137 (OOM)", sem["danger"]),
        ("webhook-relay", "Pending review", "Queued 4m ago", sem["warning"]),
        ("schema-sync", "Operational", "Completed in 1.2s", sem["success"]),
    ]

    commands: list[dict[str, Any]] = [
        _node_step(
            "frame",
            f"Jobs Table ({theme_name})",
            as_ref="root",
            x=x,
            y=y,
            width=560,
            height=240,
            props={
                "fill": t["surfaceElevated"],
                "stroke": t["border"],
                "strokeWeight": 1,
                "cornerRadius": t["radiusCard"],
                "layout": "vertical",
                "padding": 20,
                "gap": 10,
            },
        ),
        _node_step(
            "frame",
            "Table Header Wrapper",
            as_ref="header_row",
            parent_ref="root",
            width=520,
            height=32,
            props={
                "fill": "none",
                "layout": "horizontal",
                "padding": 6,
                "mainAlign": "spaceBetween",
                "crossAlign": "center",
            },
        ),
        _node_step(
            "text",
            "Col Job",
            parent_ref="header_row",
            text="Job",
            props={"fontSize": 12, "fontStyle": "SemiBold", "fill": t["textMuted"]},
        ),
        _node_step(
            "text",
            "Col Status",
            parent_ref="header_row",
            text="Status",
            props={"fontSize": 12, "fontStyle": "SemiBold", "fill": t["textMuted"]},
        ),
        _node_step(
            "text",
            "Col Detail",
            parent_ref="header_row",
            text="Last diagnostic",
            props={"fontSize": 12, "fontStyle": "SemiBold", "fill": t["textMuted"]},
        ),
    ]

    for idx, (job_name, status_label, detail, spec) in enumerate(rows):
        row_ref = f"row_{idx}"
        badge_ref = f"row_badge_{idx}"
        commands.append(
            _node_step(
                "frame",
                f"Row / {job_name}",
                as_ref=row_ref,
                parent_ref="root",
                width=520,
                height=44,
                props={
                    "fill": t["surface"],
                    "stroke": t["border"],
                    "strokeWeight": 1,
                    "cornerRadius": 8,
                    "layout": "horizontal",
                    "padding": 10,
                    "mainAlign": "spaceBetween",
                    "crossAlign": "center",
                },
            )
        )
        commands.append(
            _node_step(
                "text",
                f"Job Name {idx}",
                parent_ref=row_ref,
                text=job_name,
                props={"fontSize": 13, "fontStyle": "SemiBold", "fill": t["textPrimary"]},
            )
        )
        commands.append(
            _node_step(
                "frame",
                f"Status Pill {idx}",
                as_ref=badge_ref,
                parent_ref=row_ref,
                width=118,
                height=26,
                props={
                    "fill": spec["bg"],
                    "cornerRadius": 6,
                    "layout": "horizontal",
                    "padding": 6,
                    "mainAlign": "center",
                    "crossAlign": "center",
                },
            )
        )
        commands.append(
            _node_step(
                "text",
                f"Status Text {idx}",
                parent_ref=badge_ref,
                text=status_label,
                props={"fontSize": 11, "fontStyle": "SemiBold", "fill": spec["fg"]},
            )
        )
        commands.append(
            _node_step(
                "text",
                f"Detail Text {idx}",
                parent_ref=row_ref,
                text=detail,
                props={"fontSize": 12, "fontStyle": "Regular", "fill": t["textMuted"]},
            )
        )

    return commands


def build_state_cards_commands(
    theme_name: str = "obsidian-studio", x: int = 800, y: int = 360
) -> list[dict[str, Any]]:
    """Build Empty, Loading, and Error UI state cards (antislop R-27: cause + next action)."""
    t = get_theme(theme_name)
    sem = get_semantic_tokens(t["mode"])

    states = [
        (
            "state_empty",
            "State / Empty",
            "No deployments yet",
            "Connect a repository branch to run your first build.",
            "Connect repository",
            t["accent"],
            t["onAccent"],
        ),
        (
            "state_loading",
            "State / Loading",
            "Loading build history",
            "Fetching the latest 25 runs from the runner queue.",
            None,
            None,
            None,
        ),
        (
            "state_error",
            "State / Error",
            "Could not reach build API",
            "Connection timed out after 10s. Check port 1984 and retry.",
            "Retry connection",
            sem["danger"]["bg"],
            sem["danger"]["fg"],
        ),
    ]

    commands: list[dict[str, Any]] = [
        _node_step(
            "frame",
            f"UI States Kit ({theme_name})",
            as_ref="root",
            x=x,
            y=y,
            width=360,
            height=460,
            props={
                "fill": "none",
                "layout": "vertical",
                "gap": 16,
            },
        )
    ]

    for ref, name, heading, body, cta_label, cta_bg, cta_fg in states:
        commands.append(
            _node_step(
                "frame",
                name,
                as_ref=ref,
                parent_ref="root",
                width=360,
                height=140,
                props={
                    "fill": t["surfaceElevated"],
                    "stroke": t["border"],
                    "strokeWeight": 1,
                    "cornerRadius": t["radiusCard"],
                    "layout": "vertical",
                    "padding": 20,
                    "gap": 8,
                },
            )
        )
        commands.append(
            _node_step(
                "text",
                f"{name} Heading",
                parent_ref=ref,
                text=heading,
                props={"fontSize": 15, "fontStyle": "Bold", "fill": t["textPrimary"]},
            )
        )
        commands.append(
            _node_step(
                "text",
                f"{name} Body",
                parent_ref=ref,
                text=body,
                props={"fontSize": 13, "fontStyle": "Regular", "fill": t["textMuted"]},
            )
        )
        if cta_label and cta_bg and cta_fg:
            btn_ref = f"{ref}_cta"
            commands.append(
                _node_step(
                    "frame",
                    f"{name} Action Button",
                    as_ref=btn_ref,
                    parent_ref=ref,
                    width=170,
                    height=36,
                    props={
                        "fill": cta_bg,
                        "cornerRadius": t["radiusControl"],
                        "layout": "horizontal",
                        "padding": 8,
                        "mainAlign": "center",
                        "crossAlign": "center",
                    },
                )
            )
            commands.append(
                _node_step(
                    "text",
                    f"{name} Action Label",
                    parent_ref=btn_ref,
                    text=cta_label,
                    props={"fontSize": 13, "fontStyle": "SemiBold", "fill": cta_fg},
                )
            )

    return commands


def build_theme_board_commands(
    theme_name: str = "editorial-paper", x: int = 60, y: int = 60
) -> list[dict[str, Any]]:
    """Build a compact visual Theme Specimen board displaying surfaces, accent, and typography."""
    t = get_theme(theme_name)
    accent_ratio = contrast_ratio(t["onAccent"], t["accent"])
    text_ratio = contrast_ratio(t["textPrimary"], t["surfaceElevated"])

    commands: list[dict[str, Any]] = [
        _node_step(
            "frame",
            f"Theme Specimen: {theme_name}",
            as_ref="root",
            x=x,
            y=y,
            width=460,
            height=300,
            props={
                "fill": t["surface"],
                "stroke": t["border"],
                "strokeWeight": 1,
                "cornerRadius": t["radiusCard"],
                "layout": "vertical",
                "padding": 28,
                "gap": 18,
            },
        ),
        _node_step(
            "frame",
            "Header Group",
            as_ref="header",
            parent_ref="root",
            width=404,
            height=56,
            props={"fill": "none", "layout": "vertical", "gap": 6},
        ),
        _node_step(
            "text",
            "Theme Title",
            parent_ref="header",
            text=f"{theme_name} ({t['mode']})",
            props={"fontSize": 22, "fontStyle": "Bold", "fill": t["textPrimary"]},
        ),
        _node_step(
            "text",
            "Theme Summary",
            parent_ref="header",
            text=t["description"],
            props={"fontSize": 13, "fontStyle": "Regular", "fill": t["textMuted"]},
        ),
        _node_step(
            "frame",
            "Swatch Row",
            as_ref="swatches",
            parent_ref="root",
            width=404,
            height=72,
            props={"fill": "none", "layout": "horizontal", "gap": 12, "crossAlign": "center"},
        ),
    ]

    swatch_specs = [
        ("sw_elev", "Elevated", t["surfaceElevated"], t["textPrimary"], f"Text {text_ratio:.1f}:1"),
        ("sw_sub", "Subtle", t["surfaceSubtle"], t["textPrimary"], t["surfaceSubtle"]),
        ("sw_acc", "Accent", t["accent"], t["onAccent"], f"AA {accent_ratio:.1f}:1"),
    ]
    for ref, label, bg_c, fg_c, meta in swatch_specs:
        commands.append(
            _node_step(
                "frame",
                f"Swatch / {label}",
                as_ref=ref,
                parent_ref="swatches",
                width=126,
                height=68,
                props={
                    "fill": bg_c,
                    "stroke": t["border"],
                    "strokeWeight": 1,
                    "cornerRadius": t["radiusControl"],
                    "layout": "vertical",
                    "padding": 10,
                    "gap": 4,
                },
            )
        )
        commands.append(
            _node_step(
                "text",
                f"{label} Name",
                parent_ref=ref,
                text=label,
                props={"fontSize": 12, "fontStyle": "SemiBold", "fill": fg_c},
            )
        )
        commands.append(
            _node_step(
                "text",
                f"{label} Meta",
                parent_ref=ref,
                text=meta,
                props={"fontSize": 11, "fontStyle": "Regular", "fill": fg_c},
            )
        )

    return commands


def build_template_commands(
    template_name: str,
    *,
    theme_name: str = "obsidian-studio",
    palette_name: str = "indigo",
    x: int | None = None,
    y: int | None = None,
) -> list[dict[str, Any]]:
    """Unified factory returning valid FigCraft batch commands for any supported template."""
    tmpl = template_name.strip().lower()
    if tmpl not in SUPPORTED_TEMPLATES:
        raise ValueError(
            f"Unsupported template '{template_name}'. Choose one of: {', '.join(SUPPORTED_TEMPLATES)}."
        )

    if tmpl == "palette_swatch":
        return build_palette_swatch_commands(palette_name, x=60 if x is None else x, y=60 if y is None else y)
    if tmpl == "buttons":
        return build_starter_buttons_commands(theme_name, x=420 if x is None else x, y=60 if y is None else y)
    if tmpl == "badges":
        return build_starter_badges_commands(theme_name, x=800 if x is None else x, y=60 if y is None else y)
    if tmpl == "segmented_control":
        return build_segmented_control_commands(theme_name, x=60 if x is None else x, y=640 if y is None else y)
    if tmpl == "data_table":
        return build_data_table_commands(theme_name, x=420 if x is None else x, y=440 if y is None else y)
    if tmpl == "state_cards":
        return build_state_cards_commands(theme_name, x=800 if x is None else x, y=360 if y is None else y)
    return build_theme_board_commands(theme_name, x=60 if x is None else x, y=60 if y is None else y)


# ---------------------------------------------------------------------------
# Live Canvas Client (via bridge.py)
# ---------------------------------------------------------------------------

class CanvasClient:
    """Helper client to dispatch canvas drawing commands through bridge.py."""

    def __init__(self) -> None:
        self.proc: subprocess.Popen[str] | None = None
        self.req_id = 1

    def __enter__(self) -> "CanvasClient":
        self.proc = subprocess.Popen(
            [sys.executable, str(BRIDGE_PATH)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        self._send_rpc("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "figcraft-tokens-generator", "version": "2.0"},
        })
        assert self.proc.stdin
        self.proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        self.proc.stdin.flush()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.proc:
            try:
                if self.proc.stdin:
                    self.proc.stdin.close()
                self.proc.terminate()
                self.proc.wait(timeout=2)
            except Exception:
                pass

    def _send_rpc(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        assert self.proc and self.proc.stdin and self.proc.stdout
        req = {"jsonrpc": "2.0", "id": self.req_id, "method": method, "params": params}
        self.req_id += 1
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            return {}
        return json.loads(line)

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        res = self._send_rpc("tools/call", {"name": name, "arguments": arguments})
        return res.get("result", {})

    def run_batch(self, commands: list[dict[str, Any]], label: str = "FigCraft Template") -> dict[str, Any]:
        return self.call_tool("batch", {"commands": commands, "onError": "abort", "label": label})


def _dispatch_template(template_name: str, theme_name: str = "obsidian-studio", palette_name: str = "indigo") -> None:
    commands = build_template_commands(template_name, theme_name=theme_name, palette_name=palette_name)
    print(f"{CYAN}Connecting to FigCraft to render '{template_name}' (theme={theme_name})...{RESET}")
    with CanvasClient() as client:
        res = client.run_batch(commands, label=f"Render {template_name}")
        if res.get("isError"):
            print(f"{RED}[FAIL] Error rendering '{template_name}': {res}{RESET}")
        else:
            print(f"{GREEN}[OK] Rendered '{template_name}' ({len(commands)} steps) on FigCraft canvas.{RESET}")


def render_palette_swatch(palette_name: str) -> None:
    _dispatch_template("palette_swatch", palette_name=palette_name)


def render_starter_buttons(theme_name: str = "obsidian-studio") -> None:
    _dispatch_template("buttons", theme_name=theme_name)


def render_starter_badges(theme_name: str = "obsidian-studio") -> None:
    _dispatch_template("badges", theme_name=theme_name)


def list_tokens() -> None:
    tokens = get_tokens()
    print(f"\n{BOLD}FigCraft Design Tokens Summary (v{tokens.get('version', '1.0.0')}):{RESET}")
    print(f"  Color Palettes : {', '.join(tokens.get('colors', {}).keys())}")
    print(f"  Theme Presets  : {', '.join(tokens.get('themes', {}).keys())}")
    print(f"  Templates      : {', '.join(SUPPORTED_TEMPLATES)}")
    print(f"  Spacing Scales : {', '.join(tokens.get('spacing', {}).keys())}")
    print(f"  Border Radii   : {', '.join(tokens.get('radius', {}).keys())}")
    print(f"  Typography     : {', '.join(tokens.get('typography', {}).keys())}\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="FigCraft Design Tokens, Themes & Component Templates")
    parser.add_argument("--theme", type=str, default="obsidian-studio", help="Theme preset name (default: obsidian-studio)")
    parser.add_argument("--palette", type=str, help="Render color swatch card to FigCraft canvas (e.g. indigo, stone)")
    parser.add_argument("--starter-buttons", action="store_true", help="Render 44px accessible button library")
    parser.add_argument("--starter-badges", action="store_true", help="Render WCAG AA status badges library")
    parser.add_argument("--segmented-control", action="store_true", help="Render segmented tab control")
    parser.add_argument("--data-table", action="store_true", help="Render decision-first operational data table")
    parser.add_argument("--state-cards", action="store_true", help="Render Empty/Loading/Error UI state kit")
    parser.add_argument("--theme-board", action="store_true", help="Render visual theme specimen card")
    parser.add_argument("--export-tailwind", action="store_true", help="Print tailwind.config.js theme extension snippet")
    parser.add_argument("--export-css", action="store_true", help="Print CSS custom properties for selected --theme")
    parser.add_argument("--audit-contrast", action="store_true", help="Audit all themes and semantic tokens for WCAG AA")
    parser.add_argument("--list", action="store_true", help="List available tokens, themes, and templates")

    args = parser.parse_args()

    if args.list:
        list_tokens()
    elif args.export_tailwind:
        print(export_tailwind_theme())
    elif args.export_css:
        print(export_css_variables(args.theme))
    elif args.audit_contrast:
        audit = audit_theme_contrast()
        failures = [r for r in audit if not r["pass_aa"]]
        for r in audit:
            tag = f"{GREEN}[PASS]{RESET}" if r["pass_aa"] else f"{RED}[FAIL]{RESET}"
            print(f"  {tag} {r['scope']} | {r['pair']} ({r['fg']} on {r['bg']}) = {r['ratio']:.2f}:1")
        if failures:
            sys.exit(1)
        print(f"\n{GREEN}All {len(audit)} color pairs pass WCAG 2.2 AA (>= 4.5:1).{RESET}")
    elif args.palette:
        render_palette_swatch(args.palette)
    elif args.starter_buttons:
        render_starter_buttons(args.theme)
    elif args.starter_badges:
        render_starter_badges(args.theme)
    elif args.segmented_control:
        _dispatch_template("segmented_control", theme_name=args.theme)
    elif args.data_table:
        _dispatch_template("data_table", theme_name=args.theme)
    elif args.state_cards:
        _dispatch_template("state_cards", theme_name=args.theme)
    elif args.theme_board:
        _dispatch_template("theme_board", theme_name=args.theme)
    else:
        list_tokens()


if __name__ == "__main__":
    main()
