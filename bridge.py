#!/usr/bin/env python3
"""
FigCraft Universal MCP Smart Bridge (Lazy / On-Demand Launch)
-------------------------------------------------------------
Connects AI clients (AntiGravity, OpenCode, Cursor, Claude Desktop, etc.)
to FigCraft via Model Context Protocol (MCP).

Key Behavior:
- Startup / Discovery: Runs headless figcraft-cli (NO GUI window opens on CLI boot).
- On-Demand Launch: FigCraft GUI opens ONLY when a tool (tools/call) is actually invoked.
- 100% dynamic & portable: zero hardcoded user paths.
"""

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path

DEFAULT_PORT = int(os.environ.get("FIGCRAFT_PORT", "1984"))
HOST = "127.0.0.1"
LOG_FILE = Path(__file__).resolve().parent / "figcraft_bridge.log"


def log_debug(msg):
    if os.environ.get("FIGCRAFT_DEBUG"):
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%X')}] {msg}\n")


def find_figcraft_binaries():
    """Dynamically locate figcraft and figcraft-cli executables."""
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

    else:  # Linux
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
        with socket.create_connection((host, port), timeout=0.3):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def ensure_figcraft_running(gui_path: Path, port: int) -> bool:
    """Launch FigCraft desktop GUI with --control <port> on demand."""
    if is_port_open(HOST, port):
        return True

    if not gui_path or not gui_path.exists():
        sys.stderr.write("[FigCraft Bridge] Notice: GUI binary not found. Using headless engine.\n")
        sys.stderr.flush()
        return False

    system = platform.system()
    try:
        if system == "Windows":
            creation_flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
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

    # Wait for the control port to open (up to 10 seconds)
    start_time = time.time()
    while time.time() - start_time < 10.0:
        if is_port_open(HOST, port):
            return True
        time.sleep(0.3)

    return is_port_open(HOST, port)


class LazyMcpBridge:
    def __init__(self, gui_path: Path, cli_path: Path, port: int):
        self.gui_path = gui_path
        self.cli_path = cli_path
        self.port = port
        self.proc = None
        self.is_attached = False
        self.stop_reader = False
        self.reader_thread = None
        self.last_init_params = None
        self.lock = threading.Lock()

    def start_headless(self):
        """Start headless instance for lightweight startup/discovery."""
        self.proc = subprocess.Popen(
            [str(self.cli_path), "mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        self.is_attached = False
        self._start_reader_thread()

    def _start_reader_thread(self):
        def reader():
            while not self.stop_reader and self.proc and self.proc.stdout:
                try:
                    line = self.proc.stdout.readline()
                    if not line:
                        break
                    sys.stdout.write(line)
                    sys.stdout.flush()
                except Exception:
                    break

        self.reader_thread = threading.Thread(target=reader, daemon=True)
        self.reader_thread.start()

    def transition_to_attached(self):
        """Switch from headless to attached GUI mode on the first tool call."""
        with self.lock:
            if self.is_attached:
                return

            self.stop_reader = True
            if self.proc:
                try:
                    self.proc.terminate()
                    self.proc.wait(timeout=2)
                except Exception:
                    pass

            log_debug("Switching to attached mode (tools/call detected)")
            # Launch FigCraft GUI on demand
            gui_ready = ensure_figcraft_running(self.gui_path, self.port)

            if gui_ready:
                cmd = [str(self.cli_path), "mcp", "--attach", str(self.port)]
                self.is_attached = True
            else:
                cmd = [str(self.cli_path), "mcp"]
                self.is_attached = False

            self.proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
            )
            self.stop_reader = False

            # Internal handshake with attached engine
            init_params = self.last_init_params or {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "figcraft-bridge", "version": "1.0"},
            }
            handshake = json.dumps({
                "jsonrpc": "2.0",
                "id": "bridge-init-handshake",
                "method": "initialize",
                "params": init_params,
            }) + "\n"
            self.proc.stdin.write(handshake)
            self.proc.stdin.flush()
            # Consume the internal init response so it doesn't leak to client
            self.proc.stdout.readline()

            notify = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
            self.proc.stdin.write(notify)
            self.proc.stdin.flush()

            self._start_reader_thread()

    def run(self):
        self.start_headless()

        for line in sys.stdin:
            if not line:
                break

            # Parse method to detect tool calls
            try:
                msg = json.loads(line)
                method = msg.get("method", "")
                if method == "initialize":
                    self.last_init_params = msg.get("params")
                elif method == "tools/call" and not self.is_attached:
                    self.transition_to_attached()
            except Exception:
                pass

            if self.proc and self.proc.stdin:
                try:
                    self.proc.stdin.write(line if line.endswith("\n") else line + "\n")
                    self.proc.stdin.flush()
                except Exception:
                    break

        # Cleanup on exit
        self.stop_reader = True
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass


def main():
    gui_path, cli_path = find_figcraft_binaries()

    if not cli_path or not cli_path.exists():
        sys.stderr.write("[FigCraft Bridge] Error: figcraft-cli executable not found.\n")
        sys.stderr.flush()
        sys.exit(1)

    bridge = LazyMcpBridge(gui_path, cli_path, DEFAULT_PORT)
    try:
        bridge.run()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
