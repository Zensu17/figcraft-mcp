#!/usr/bin/env python3
"""
FigCraft Standard Design Tokens & Canvas Starter Kit
----------------------------------------------------
Provides a standard design tokens API and CLI tool to generate token swatches,
starter buttons, and status badges directly onto the active FigCraft canvas.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).resolve().parent
TOKENS_FILE = SCRIPT_DIR / "tokens.json"
BRIDGE_PATH = SCRIPT_DIR / "bridge.py"

# ANSI Colors
GREEN = "\033[32m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
BOLD = "\033[1m"
RESET = "\033[0m"


def load_tokens() -> dict:
    """Loads tokens.json from disk."""
    if not TOKENS_FILE.is_file():
        raise FileNotFoundError(f"tokens.json not found at: {TOKENS_FILE}")
    with open(TOKENS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# Singleton in-memory cache
_TOKENS = None


def get_tokens() -> dict:
    global _TOKENS
    if _TOKENS is None:
        _TOKENS = load_tokens()
    return _TOKENS


def get_color(name_or_key: str, default: str = "#000000") -> str:
    """
    Get hex color by shade key, e.g. 'indigo-500', 'slate.900', or 'emerald'.
    Defaults to 500 shade if only palette name is provided.
    """
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


def get_typography(key: str) -> dict:
    """Get typography specs (size, lineHeight) by key, e.g. 'base', 'xl'."""
    typo = get_tokens().get("typography", {})
    return typo.get(key.lower(), {"size": 16, "lineHeight": 24})


def export_tailwind_theme() -> str:
    """Exports tokens.json as a theme.extend configuration object for Tailwind CSS."""
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


class CanvasClient:
    """Helper client to dispatch canvas drawing commands through bridge.py."""

    def __init__(self):
        self.proc = None
        self.req_id = 1

    def __enter__(self):
        self.proc = subprocess.Popen(
            [sys.executable, str(BRIDGE_PATH)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        # Initialize MCP handshake
        self._send_rpc("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "figcraft-tokens-generator", "version": "1.0"},
        })
        self.proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        self.proc.stdin.flush()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.proc:
            try:
                self.proc.stdin.close()
                self.proc.terminate()
                self.proc.wait(timeout=2)
            except Exception:
                pass

    def _send_rpc(self, method: str, params: dict) -> dict:
        req = {"jsonrpc": "2.0", "id": self.req_id, "method": method, "params": params}
        self.req_id += 1
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            return {}
        return json.loads(line)

    def call_tool(self, name: str, arguments: dict) -> dict:
        res = self._send_rpc("tools/call", {"name": name, "arguments": arguments})
        return res.get("result", {})

    def run_batch(self, commands: list[dict]) -> dict:
        return self.call_tool("batch", {"commands": commands})


def render_palette_swatch(palette_name: str):
    """Draws a complete vertical color swatch card onto the active FigCraft canvas."""
    tokens = get_tokens().get("colors", {})
    palette = tokens.get(palette_name.lower())
    if not palette:
        print(f"[FAIL] Palette '{palette_name}' not found. Available: {', '.join(tokens.keys())}")
        return

    print(f"{CYAN}Connecting to FigCraft to render '{palette_name}' color swatch card...{RESET}")

    commands = [
        # Main Card Container
        {
            "action": "create",
            "params": {
                "name": f"Palette: {palette_name.capitalize()}",
                "type": "frame",
                "x": 60,
                "y": 60,
                "width": 320,
                "height": 560,
                "fill": "#0F172A",
                "cornerRadius": 16,
                "layoutMode": "vertical",
                "padding": 20,
                "itemSpacing": 8,
            },
        },
        # Header Text
        {
            "action": "create",
            "params": {
                "name": "Header",
                "type": "text",
                "text": f"{palette_name.upper()} COLOR PALETTE",
                "fontSize": 14,
                "fontWeight": 700,
                "color": "#F8FAFC",
            },
        },
    ]

    # Add each shade row
    for shade, hex_val in palette.items():
        text_color = "#020617" if int(shade) < 500 else "#FFFFFF"
        commands.append({
            "action": "create",
            "params": {
                "name": f"Shade {shade}",
                "type": "frame",
                "width": 280,
                "height": 34,
                "fill": hex_val,
                "cornerRadius": 6,
                "layoutMode": "horizontal",
                "padding": 8,
                "itemSpacing": 12,
            },
        })
        commands.append({
            "action": "create",
            "params": {
                "name": f"Label {shade}",
                "type": "text",
                "text": f"{shade}  {hex_val}",
                "fontSize": 11,
                "fontWeight": 600,
                "color": text_color,
            },
        })

    with CanvasClient() as client:
        res = client.run_batch(commands)
        if res.get("isError"):
            print(f"[FAIL] Error creating canvas palette: {res}")
        else:
            print(f"{GREEN}[OK] Successfully rendered '{palette_name}' swatch card on FigCraft canvas!{RESET}")


def render_starter_buttons():
    """Draws a standard component set of Primary, Secondary, Outline, and Danger buttons."""
    print(f"{CYAN}Connecting to FigCraft to render Starter Buttons...{RESET}")

    commands = [
        # Parent Container
        {
            "action": "create",
            "params": {
                "name": "Component Library: Buttons",
                "type": "frame",
                "x": 420,
                "y": 60,
                "width": 340,
                "height": 380,
                "fill": "#18181B",
                "cornerRadius": 16,
                "layoutMode": "vertical",
                "padding": 24,
                "itemSpacing": 16,
            },
        },
        # Header
        {
            "action": "create",
            "params": {
                "name": "Title",
                "type": "text",
                "text": "BUTTON COMPONENTS",
                "fontSize": 14,
                "fontWeight": 700,
                "color": "#F4F4F5",
            },
        },
        # Primary Button (Indigo)
        {
            "action": "create",
            "params": {
                "name": "Button / Primary",
                "type": "frame",
                "width": 292,
                "height": 44,
                "fill": "#4F46E5",
                "cornerRadius": 8,
                "layoutMode": "horizontal",
                "padding": 12,
            },
        },
        {
            "action": "create",
            "params": {
                "name": "Label",
                "type": "text",
                "text": "Primary Action",
                "fontSize": 14,
                "fontWeight": 600,
                "color": "#FFFFFF",
            },
        },
        # Secondary Button (Slate/Dark)
        {
            "action": "create",
            "params": {
                "name": "Button / Secondary",
                "type": "frame",
                "width": 292,
                "height": 44,
                "fill": "#27272A",
                "cornerRadius": 8,
                "layoutMode": "horizontal",
                "padding": 12,
            },
        },
        {
            "action": "create",
            "params": {
                "name": "Label",
                "type": "text",
                "text": "Secondary Action",
                "fontSize": 14,
                "fontWeight": 600,
                "color": "#E4E4E7",
            },
        },
        # Outline Button
        {
            "action": "create",
            "params": {
                "name": "Button / Outline",
                "type": "frame",
                "width": 292,
                "height": 44,
                "fill": "#18181B",
                "stroke": "#52525B",
                "strokeWidth": 1,
                "cornerRadius": 8,
                "layoutMode": "horizontal",
                "padding": 12,
            },
        },
        {
            "action": "create",
            "params": {
                "name": "Label",
                "type": "text",
                "text": "Outline Action",
                "fontSize": 14,
                "fontWeight": 600,
                "color": "#A1A1AA",
            },
        },
        # Danger Button (Rose)
        {
            "action": "create",
            "params": {
                "name": "Button / Danger",
                "type": "frame",
                "width": 292,
                "height": 44,
                "fill": "#E11D48",
                "cornerRadius": 8,
                "layoutMode": "horizontal",
                "padding": 12,
            },
        },
        {
            "action": "create",
            "params": {
                "name": "Label",
                "type": "text",
                "text": "Danger Action",
                "fontSize": 14,
                "fontWeight": 600,
                "color": "#FFFFFF",
            },
        },
    ]

    with CanvasClient() as client:
        res = client.run_batch(commands)
        if res.get("isError"):
            print(f"[FAIL] Error creating starter buttons: {res}")
        else:
            print(f"{GREEN}[OK] Successfully rendered Button components on FigCraft canvas!{RESET}")


def render_starter_badges():
    """Draws a standard component set of status badges (Success, Warning, Danger, Info)."""
    print(f"{CYAN}Connecting to FigCraft to render Starter Badges...{RESET}")

    commands = [
        # Parent Container
        {
            "action": "create",
            "params": {
                "name": "Component Library: Status Badges",
                "type": "frame",
                "x": 800,
                "y": 60,
                "width": 280,
                "height": 280,
                "fill": "#0F172A",
                "cornerRadius": 16,
                "layoutMode": "vertical",
                "padding": 24,
                "itemSpacing": 14,
            },
        },
        # Title
        {
            "action": "create",
            "params": {
                "name": "Title",
                "type": "text",
                "text": "STATUS BADGES",
                "fontSize": 14,
                "fontWeight": 700,
                "color": "#F8FAFC",
            },
        },
        # Success Badge
        {
            "action": "create",
            "params": {
                "name": "Badge / Success",
                "type": "frame",
                "width": 120,
                "height": 28,
                "fill": "#064E3B",
                "cornerRadius": 6,
                "layoutMode": "horizontal",
                "padding": 6,
            },
        },
        {
            "action": "create",
            "params": {
                "name": "Label",
                "type": "text",
                "text": "ACTIVE",
                "fontSize": 11,
                "fontWeight": 700,
                "color": "#34D399",
            },
        },
        # Warning Badge
        {
            "action": "create",
            "params": {
                "name": "Badge / Warning",
                "type": "frame",
                "width": 120,
                "height": 28,
                "fill": "#78350F",
                "cornerRadius": 6,
                "layoutMode": "horizontal",
                "padding": 6,
            },
        },
        {
            "action": "create",
            "params": {
                "name": "Label",
                "type": "text",
                "text": "PENDING",
                "fontSize": 11,
                "fontWeight": 700,
                "color": "#FCD34D",
            },
        },
        # Danger Badge
        {
            "action": "create",
            "params": {
                "name": "Badge / Danger",
                "type": "frame",
                "width": 120,
                "height": 28,
                "fill": "#881337",
                "cornerRadius": 6,
                "layoutMode": "horizontal",
                "padding": 6,
            },
        },
        {
            "action": "create",
            "params": {
                "name": "Label",
                "type": "text",
                "text": "FAILED",
                "fontSize": 11,
                "fontWeight": 700,
                "color": "#FDA4AF",
            },
        },
        # Info Badge
        {
            "action": "create",
            "params": {
                "name": "Badge / Info",
                "type": "frame",
                "width": 120,
                "height": 28,
                "fill": "#0C4A6E",
                "cornerRadius": 6,
                "layoutMode": "horizontal",
                "padding": 6,
            },
        },
        {
            "action": "create",
            "params": {
                "name": "Label",
                "type": "text",
                "text": "INFO",
                "fontSize": 11,
                "fontWeight": 700,
                "color": "#7DD3FC",
            },
        },
    ]

    with CanvasClient() as client:
        res = client.run_batch(commands)
        if res.get("isError"):
            print(f"[FAIL] Error creating starter badges: {res}")
        else:
            print(f"{GREEN}[OK] Successfully rendered Status Badges on FigCraft canvas!{RESET}")


def list_tokens():
    tokens = get_tokens()
    print(f"\n{BOLD}FigCraft Design Tokens Summary:{RESET}")
    print(f"  Color Palettes : {', '.join(tokens.get('colors', {}).keys())}")
    print(f"  Spacing Scales : {', '.join(tokens.get('spacing', {}).keys())}")
    print(f"  Border Radii   : {', '.join(tokens.get('radius', {}).keys())}")
    print(f"  Typography     : {', '.join(tokens.get('typography', {}).keys())}\n")


def main():
    parser = argparse.ArgumentParser(description="FigCraft Design Tokens API and Canvas Generator")
    parser.add_argument("--palette", type=str, help="Render color swatch card to FigCraft canvas (e.g. indigo, slate, sky)")
    parser.add_argument("--starter-buttons", action="store_true", help="Render button component library to FigCraft canvas")
    parser.add_argument("--starter-badges", action="store_true", help="Render status badges library to FigCraft canvas")
    parser.add_argument("--export-tailwind", action="store_true", help="Print tailwind.config.js theme extension snippet")
    parser.add_argument("--list", action="store_true", help="List available tokens and scales")

    args = parser.parse_args()

    if args.list:
        list_tokens()
    elif args.export_tailwind:
        print(export_tailwind_theme())
    elif args.palette:
        render_palette_swatch(args.palette)
    elif args.starter_buttons:
        render_starter_buttons()
    elif args.starter_badges:
        render_starter_badges()
    else:
        list_tokens()
        print("Usage examples:")
        print("  python tokens.py --palette indigo")
        print("  python tokens.py --starter-buttons")
        print("  python tokens.py --starter-badges")
        print("  python tokens.py --export-tailwind\n")


if __name__ == "__main__":
    main()
