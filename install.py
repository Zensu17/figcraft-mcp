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
    print(f"  \033[32m✔\033[0m {msg}")


def print_warn(msg):
    print(f"  \033[33m!\033[0m {msg}")


def print_err(msg):
    print(f"  \033[31m✖\033[0m {msg}")


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

    print_step("Configuring Windows Start Menu Shortcut...")
    try:
        from bridge import find_figcraft_binaries
        gui_path, _ = find_figcraft_binaries()
        if not gui_path or not gui_path.exists():
            print_warn("FigCraft GUI executable not found for shortcut update.")
            return

        appdata = os.environ.get("APPDATA")
        if not appdata:
            return

        shortcut_path = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "FigCraft.lnk"
        
        # PowerShell script to create/update shortcut
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
        print_ok(f"Start Menu shortcut updated with '--control 1984': {shortcut_path}")
    except Exception as e:
        print_warn(f"Notice updating Start Menu shortcut: {e}")


def main():
    print("\033[1;35m==================================================\033[0m")
    print("\033[1;35m   FigCraft Universal MCP Setup & Auto-Config     \033[0m")
    print("\033[1;35m==================================================\033[0m")
    print(f"System:  {platform.system()} ({platform.machine()})")
    print(f"Python:  {sys.executable}")
    print(f"Bridge:  {BRIDGE_PATH}")

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
