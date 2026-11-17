#!/usr/bin/env python3
"""
FigCraft Universal MCP Smart Bridge
------------------------------------
Connects any AI client (AntiGravity CLI, AntiGravity IDE, OpenCode CLI, Cursor, Claude Desktop, etc.)
to an active FigCraft instance via Model Context Protocol (MCP).

Features:
- 100% dynamic paths: zero hardcoded user directories.
- Auto-detects FigCraft application & CLI across Windows, macOS, and Linux.
- Auto-launches the desktop app with `--control <port>` if not currently running.
- Seamlessly pipes stdio MCP protocol to `figcraft-cli mcp --attach <port>`.
- Gracefully falls back to headless MCP mode if GUI app cannot be reached.
"""

import os
import platform
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

DEFAULT_PORT = int(os.environ.get("FIGCRAFT_PORT", "1984"))
HOST = "127.0.0.1"


def find_figcraft_binaries():
    """
    Dynamically locate figcraft and figcraft-cli executables
    based on the current operating system and standard install locations.
    """
    system = platform.system()

    # 1. Environment variable override
    env_gui = os.environ.get("FIGCRAFT_PATH")
    env_cli = os.environ.get("FIGCRAFT_CLI_PATH")
    if env_gui and env_cli and Path(env_gui).exists() and Path(env_cli).exists():
        return Path(env_gui), Path(env_cli)

    gui_path = None
    cli_path = None

    if system == "Windows":
        candidates_dir = [
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "ArtCraft" / "FigCraft",
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "ArtCraft" / "FigCraft",
            Path.home() / "AppData" / "Local" / "Programs" / "FigCraft",
            Path.home() / "AppData" / "Local" / "ArtCraft" / "FigCraft",
        ]

        for d in candidates_dir:
            cand_gui = d / "figcraft.exe"
            cand_cli = d / "figcraft-cli.exe"
            if cand_gui.exists() and cand_cli.exists():
                gui_path, cli_path = cand_gui, cand_cli
                break

    elif system == "Darwin":  # macOS
        candidates = [
            (
                Path("/Applications/FigCraft.app/Contents/MacOS/figcraft"),
                Path("/Applications/FigCraft.app/Contents/MacOS/figcraft-cli"),
            ),
            (
                Path.home() / "Applications/FigCraft.app/Contents/MacOS/figcraft",
                Path.home() / "Applications/FigCraft.app/Contents/MacOS/figcraft-cli",
            ),
        ]
        for cg, cc in candidates:
            if cg.exists() and cc.exists():
                gui_path, cli_path = cg, cc
                break

    else:  # Linux / Unix
        cand_dirs = [
            Path("/usr/local/bin"),
            Path("/usr/bin"),
            Path.home() / ".local" / "bin",
            Path("/opt/figcraft"),
        ]
        for d in cand_dirs:
            cg = d / "figcraft"
            cc = d / "figcraft-cli"
            if cg.exists() and cc.exists():
                gui_path, cli_path = cg, cc
                break

    # Fallback to PATH search
    if not gui_path:
        w_gui = shutil.which("figcraft")
        if w_gui:
            gui_path = Path(w_gui)

    if not cli_path:
        w_cli = shutil.which("figcraft-cli")
        if w_cli:
            cli_path = Path(w_cli)

    return gui_path, cli_path


def is_port_open(host: str, port: int) -> bool:
    """Check if the control TCP port is accepting connections."""
    try:
        with socket.create_connection((host, port), timeout=0.4):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def ensure_figcraft_running(gui_path: Path, port: int) -> bool:
    """Ensure FigCraft GUI app is running with --control <port>."""
    if is_port_open(HOST, port):
        return True

    if not gui_path or not gui_path.exists():
        sys.stderr.write(f"[FigCraft Bridge] Notice: GUI binary not found. Will use headless engine.\n")
        sys.stderr.flush()
        return False

    # Launch GUI in detached mode depending on OS
    system = platform.system()
    try:
        if system == "Windows":
            # DETACHED_PROCESS = 0x00000008, CREATE_NEW_PROCESS_GROUP = 0x00000200
            creation_flags = 0x00000008 | 0x00000200
            subprocess.Popen(
                [str(gui_path), "--control", str(port)],
                cwd=str(gui_path.parent),
                creationflags=creation_flags,
                close_fds=True,
            )
        else:
            subprocess.Popen(
                [str(gui_path), "--control", str(port)],
                cwd=str(gui_path.parent),
                start_new_session=True,
                close_fds=True,
            )
    except Exception as e:
        sys.stderr.write(f"[FigCraft Bridge] Notice: Could not launch GUI automatically: {e}\n")
        sys.stderr.flush()

    # Wait for the control port to be listening (up to 10 seconds)
    start_time = time.time()
    while time.time() - start_time < 10.0:
        if is_port_open(HOST, port):
            return True
        time.sleep(0.3)

    return is_port_open(HOST, port)


def main():
    gui_path, cli_path = find_figcraft_binaries()

    if not cli_path or not cli_path.exists():
        sys.stderr.write(
            "[FigCraft Bridge] Error: figcraft-cli executable not found.\n"
            "Please ensure FigCraft is installed or set FIGCRAFT_CLI_PATH environment variable.\n"
        )
        sys.stderr.flush()
        sys.exit(1)

    app_ready = ensure_figcraft_running(gui_path, DEFAULT_PORT)

    if app_ready:
        cmd = [str(cli_path), "mcp", "--attach", str(DEFAULT_PORT)]
    else:
        sys.stderr.write("[FigCraft Bridge] Running in headless mode (app port not active)\n")
        sys.stderr.flush()
        cmd = [str(cli_path), "mcp"]

    try:
        proc = subprocess.Popen(cmd)
        return_code = proc.wait()
        sys.exit(return_code)
    except KeyboardInterrupt:
        proc.terminate()
        sys.exit(0)
    except Exception as e:
        sys.stderr.write(f"[FigCraft Bridge] Error running figcraft-cli: {e}\n")
        sys.stderr.flush()
        sys.exit(1)


if __name__ == "__main__":
    main()
