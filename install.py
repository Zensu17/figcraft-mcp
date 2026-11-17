#!/usr/bin/env python3
"""
FigCraft Universal MCP Installer
--------------------------------
Automatically configures FigCraft MCP across all detected AI tools on this computer:
- Google AntiGravity CLI & AntiGravity IDE (~/.gemini/config/mcp_config.json)
- OpenCode CLI (~/.config/opencode/opencode.json)
- Cursor IDE (~/.cursor/mcp.json)
- Claude Desktop (%APPDATA%/Claude/claude_desktop_config.json)

Dynamic & Portable:
- Uses the current user's home directory and python interpreter.
- No hardcoded usernames, paths, or fixed OS assumptions.
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# Paths relative to this installer
SCRIPT_DIR = Path(__file__).resolve().parent
BRIDGE_PATH = SCRIPT_DIR / "bridge.py"


def print_step(title):
    print(f"\n\033[1;36m==>\033[0m \033[1m{title}\033[0m")


def print_ok(msg):
    print(f"  \033[32m[OK]\033[0m {msg}")


def print_warn(msg):
    print(f"  \033[33m[WARN]\033[0m {msg}")


def print_err(msg):
    print(f"  \033[31m[FAIL]\033[0m {msg}")


def configure_antigravity():
    print_step("Configuring Google AntiGravity (CLI & IDE)...")
    config_dir = Path.home() / ".gemini" / "config"
    config_file = config_dir / "mcp_config.json"

    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        data = {}
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}

        mcp_servers = data.setdefault("mcpServers", {})
        mcp_servers["FigCraft"] = {
            "command": sys.executable,
            "args": [str(BRIDGE_PATH)],
        }

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print_ok(f"Registered in AntiGravity: {config_file}")
        return True
    except Exception as e:
        print_err(f"Failed to configure AntiGravity: {e}")
        return False


def configure_opencode():
    print_step("Configuring OpenCode CLI...")
    configured = False

    # 1. Update config file directly
    config_dir = Path.home() / ".config" / "opencode"
    config_file = config_dir / "opencode.json"
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            mcp_block = data.setdefault("mcp", {})
            mcp_block["FigCraft"] = {
                "type": "local",
                "command": [sys.executable, str(BRIDGE_PATH)],
                "enabled": True,
            }
            servers_block = mcp_block.setdefault("servers", {})
            servers_block["FigCraft"] = {
                "type": "local",
                "command": [sys.executable, str(BRIDGE_PATH)],
            }

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            print_ok(f"Updated OpenCode config: {config_file}")
            configured = True
        except Exception as e:
            print_warn(f"Notice updating opencode.json directly: {e}")

    # 2. Also try running opencode command if present in PATH
    opencode_bin = shutil.which("opencode")
    if opencode_bin:
        try:
            cmd = [
                opencode_bin,
                "mcp",
                "add",
                "--global",
                "FigCraft",
                "--",
                sys.executable,
                str(BRIDGE_PATH),
            ]
            subprocess.run(cmd, capture_output=True, text=True, check=False)
            print_ok("Registered via 'opencode mcp add --global'")
            configured = True
        except Exception as e:
            print_warn(f"Notice running opencode CLI command: {e}")

    if not configured:
        print_warn("OpenCode config not found (will be active once OpenCode is installed).")
    return configured


def configure_cursor():
    print_step("Configuring Cursor IDE...")
    cursor_dir = Path.home() / ".cursor"
    config_file = cursor_dir / "mcp.json"

    try:
        cursor_dir.mkdir(parents=True, exist_ok=True)
        data = {}
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception:
                data = {}

        mcp_servers = data.setdefault("mcpServers", {})
        mcp_servers["FigCraft"] = {
            "command": sys.executable,
            "args": [str(BRIDGE_PATH)],
        }

        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print_ok(f"Registered in Cursor: {config_file}")
        return True
    except Exception as e:
        print_err(f"Failed to configure Cursor: {e}")
        return False


def configure_claude_desktop():
    print_step("Checking Claude Desktop...")
    system = platform.system()
    config_file = None

    if system == "Windows":
        appdata = os.environ.get("APPDATA")
        if appdata:
            config_file = Path(appdata) / "Claude" / "claude_desktop_config.json"
    elif system == "Darwin":
        config_file = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"

    if config_file and config_file.parent.exists():
        try:
            data = {}
            if config_file.exists():
                try:
                    with open(config_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                except Exception:
                    data = {}

            mcp_servers = data.setdefault("mcpServers", {})
            mcp_servers["FigCraft"] = {
                "command": sys.executable,
                "args": [str(BRIDGE_PATH)],
            }

            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)

            print_ok(f"Registered in Claude Desktop: {config_file}")
            return True
        except Exception as e:
            print_warn(f"Could not update Claude Desktop config: {e}")
    else:
        print_warn("Claude Desktop not installed (skipped).")
    return False


def setup_windows_shortcut():
    if platform.system() != "Windows":
        return

    print_step("Configuring Windows Shortcuts (Start Menu & Desktop)...")
    try:
        from bridge import find_figcraft_binaries
        gui_path, _ = find_figcraft_binaries()
        if not gui_path or not gui_path.exists():
            print_warn("FigCraft GUI executable not found for shortcut update.")
            return

        appdata = os.environ.get("APPDATA")
        if not appdata:
            return

        candidate_shortcuts = [
            Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "FigCraft.lnk",
            Path.home() / "Desktop" / "FigCraft.lnk",
        ]
        public_desktop = os.environ.get("PUBLIC")
        if public_desktop:
            candidate_shortcuts.append(Path(public_desktop) / "Desktop" / "FigCraft.lnk")

        for shortcut_path in candidate_shortcuts:
            # Update existing shortcut or always ensure the start menu shortcut exists
            if shortcut_path.exists() or "Start Menu" in str(shortcut_path):
                ps_script = f"""
                $sh = New-Object -ComObject WScript.Shell
                $sc = $sh.CreateShortcut('{shortcut_path}')
                $sc.TargetPath = '{gui_path}'
                $sc.Arguments = '--control 1984'
                $sc.WorkingDirectory = '{gui_path.parent}'
                $sc.Description = 'FigCraft (AI Controlled)'
                $sc.Save()
                """
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, check=False)
                print_ok(f"Shortcut updated with '--control 1984': {shortcut_path}")
    except Exception as e:
        print_warn(f"Notice updating shortcuts: {e}")


def uninstall():
    print("\033[1;33m==> Uninstalling FigCraft MCP configuration from all AI tools...\033[0m")
    
    # AntiGravity
    ag_cfg = Path.home() / ".gemini" / "config" / "mcp_config.json"
    if ag_cfg.exists():
        try:
            with open(ag_cfg, "r", encoding="utf-8") as f:
                d = json.load(f)
            if "FigCraft" in d.get("mcpServers", {}):
                del d["mcpServers"]["FigCraft"]
                with open(ag_cfg, "w", encoding="utf-8") as f:
                    json.dump(d, f, indent=2)
                print_ok("Removed FigCraft from AntiGravity")
        except Exception as e:
            print_warn(f"Error removing from AntiGravity: {e}")

    # OpenCode
    oc_cfg = Path.home() / ".config" / "opencode" / "opencode.json"
    if oc_cfg.exists():
        try:
            with open(oc_cfg, "r", encoding="utf-8") as f:
                d = json.load(f)
            mcp = d.get("mcp", {})
            mcp.pop("FigCraft", None)
            mcp.get("servers", {}).pop("FigCraft", None)
            with open(oc_cfg, "w", encoding="utf-8") as f:
                json.dump(d, f, indent=2)
            print_ok("Removed FigCraft from OpenCode")
        except Exception as e:
            print_warn(f"Error removing from OpenCode: {e}")

    # Cursor
    cur_cfg = Path.home() / ".cursor" / "mcp.json"
    if cur_cfg.exists():
        try:
            with open(cur_cfg, "r", encoding="utf-8") as f:
                d = json.load(f)
            if "FigCraft" in d.get("mcpServers", {}):
                del d["mcpServers"]["FigCraft"]
                with open(cur_cfg, "w", encoding="utf-8") as f:
                    json.dump(d, f, indent=2)
                print_ok("Removed FigCraft from Cursor")
        except Exception as e:
            print_warn(f"Error removing from Cursor: {e}")

    # Claude Desktop
    claude_cfg = None
    if platform.system() == "Windows" and os.environ.get("APPDATA"):
        claude_cfg = Path(os.environ["APPDATA"]) / "Claude" / "claude_desktop_config.json"
    elif platform.system() == "Darwin":
        claude_cfg = Path.home() / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json"

    if claude_cfg and claude_cfg.exists():
        try:
            with open(claude_cfg, "r", encoding="utf-8") as f:
                d = json.load(f)
            if "FigCraft" in d.get("mcpServers", {}):
                del d["mcpServers"]["FigCraft"]
                with open(claude_cfg, "w", encoding="utf-8") as f:
                    json.dump(d, f, indent=2)
                print_ok("Removed FigCraft from Claude Desktop")
        except Exception as e:
            print_warn(f"Error removing from Claude Desktop: {e}")

    print("\n\033[1;32m[OK] FigCraft MCP successfully uninstalled from all AI tools.\033[0m\n")


def main():
    print("\033[1;35m==================================================\033[0m")
    print("\033[1;35m   FigCraft Universal MCP Setup & Auto-Config     \033[0m")
    print("\033[1;35m==================================================\033[0m")
    print(f"System:  {platform.system()} ({platform.machine()})")
    print(f"Python:  {sys.executable}")
    print(f"Bridge:  {BRIDGE_PATH}")

    if "--uninstall" in sys.argv:
        uninstall()
        return

    # Validate bridge import
    try:
        sys.path.insert(0, str(SCRIPT_DIR))
        from bridge import find_figcraft_binaries
        gui, cli = find_figcraft_binaries()
        if cli:
            print_ok(f"FigCraft CLI found: {cli}")
        else:
            print_warn("FigCraft CLI not detected automatically. Please ensure FigCraft is installed.")
        if gui:
            print_ok(f"FigCraft GUI found: {gui}")
    except Exception as e:
        print_warn(f"Bridge test check: {e}")

    # Configure clients
    configure_antigravity()
    configure_opencode()
    configure_cursor()
    configure_claude_desktop()
    setup_windows_shortcut()

    print("\n\033[1;32m==================================================\033[0m")
    print("\033[1;32m   Installation & Configuration Complete!        \033[0m")
    print("\033[1;32m==================================================\033[0m")
    print("You can now prompt any AI agent to design in FigCraft!")
    print("Run 'python test_connection.py' to test the connection.\n")


if __name__ == "__main__":
    main()
