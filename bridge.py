#!/usr/bin/env python3
"""
FigCraft Universal MCP Smart Bridge (Lazy / On-Demand Launch + MCP Primitives Middleware)
----------------------------------------------------------------------------------------
Connects AI clients (AntiGravity, OpenCode, Cursor, Claude Desktop, etc.)
to FigCraft via Model Context Protocol (MCP).

Key Behavior:
- Startup / Discovery: Runs headless figcraft-cli (NO GUI window opens on CLI boot).
- On-Demand Launch: FigCraft GUI opens ONLY when a live canvas tool or resource is invoked.
- MCP Primitives Middleware: Augments native FigCraft MCP with design token resources,
  semantic AST extraction, reusable prompts, and automatic property guardrails.
- 100% dynamic & portable: zero hardcoded user paths, Python standard library only.
"""

from __future__ import annotations

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
from typing import Any, Callable

import mcp_primitives

DEFAULT_PORT = int(os.environ.get("FIGCRAFT_PORT", "1984"))
HOST = "127.0.0.1"
LOG_FILE = Path(__file__).resolve().parent / "figcraft_bridge.log"


def log_debug(msg: str) -> None:
    if os.environ.get("FIGCRAFT_DEBUG"):
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%X')}] {msg}\n")


def find_figcraft_binaries() -> tuple[Path | None, Path | None]:
    """Dynamically locate figcraft and figcraft-cli executables."""
    system = platform.system()

    # 1. Environment variable override
    env_gui = os.environ.get("FIGCRAFT_PATH")
    env_cli = os.environ.get("FIGCRAFT_CLI_PATH")
    if env_gui and env_cli and Path(env_gui).exists() and Path(env_cli).exists():
        return Path(env_gui), Path(env_cli)

    gui_path: Path | None = None
    cli_path: Path | None = None

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


def ensure_figcraft_running(gui_path: Path | None, port: int) -> bool:
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


def _rpc_id_key(req_id: Any) -> tuple[str, Any]:
    return (type(req_id).__name__, req_id)


def _jsonrpc_result(req_id: Any, result: dict[str, Any]) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "result": result}


def _jsonrpc_error(req_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


class LazyMcpBridge:
    def __init__(self, gui_path: Path | None, cli_path: Path, port: int):
        self.gui_path = gui_path
        self.cli_path = cli_path
        self.port = port
        self.proc: subprocess.Popen[str] | None = None
        self.is_attached = False
        self.reader_stop_event: threading.Event | None = None
        self.reader_thread: threading.Thread | None = None
        self.last_init_params: dict[str, Any] | None = None

        self.transition_lock = threading.Lock()
        self.stdout_lock = threading.Lock()
        self.stdin_lock = threading.Lock()
        self.state_lock = threading.Lock()

        self.internal_seq = 0
        self.internal_waiters: dict[str, tuple[threading.Event, list[dict[str, Any]]]] = {}
        self.intercept_callbacks: dict[tuple[str, Any], Callable[[dict[str, Any]], dict[str, Any]]] = {}

    def _write_client(self, payload: dict[str, Any] | str) -> None:
        line = payload if isinstance(payload, str) else json.dumps(payload)
        if not line.endswith("\n"):
            line += "\n"
        with self.stdout_lock:
            sys.stdout.write(line)
            sys.stdout.flush()

    def _write_upstream(self, payload: dict[str, Any] | str) -> None:
        line = payload if isinstance(payload, str) else json.dumps(payload)
        if not line.endswith("\n"):
            line += "\n"
        with self.stdin_lock:
            if not self.proc or not self.proc.stdin:
                raise RuntimeError("Upstream FigCraft MCP process is not running.")
            self.proc.stdin.write(line)
            self.proc.stdin.flush()

    def start_headless(self) -> None:
        """Start headless instance for lightweight startup/discovery."""
        self.proc = subprocess.Popen(
            [str(self.cli_path), "mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            text=True,
        )
        self.is_attached = False
        self._start_reader_thread(self.proc)

    def _start_reader_thread(self, proc: subprocess.Popen[str]) -> None:
        stop_event = threading.Event()
        self.reader_stop_event = stop_event

        def reader() -> None:
            while not stop_event.is_set() and proc.stdout:
                try:
                    line = proc.stdout.readline()
                    if not line:
                        break
                    self._handle_upstream_line(line)
                except Exception as exc:
                    log_debug(f"Reader error: {exc}")
                    break

        self.reader_thread = threading.Thread(target=reader, daemon=True)
        self.reader_thread.start()

    def _handle_upstream_line(self, line: str) -> None:
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            self._write_client(line)
            return

        if isinstance(msg, dict) and "id" in msg:
            msg_id = msg["id"]
            if isinstance(msg_id, str):
                with self.state_lock:
                    waiter = self.internal_waiters.get(msg_id)
                if waiter is not None:
                    event, result_box = waiter
                    result_box.append(msg)
                    event.set()
                    return

            key = _rpc_id_key(msg_id)
            with self.state_lock:
                callback = self.intercept_callbacks.pop(key, None)

            if callback is not None and "result" in msg and isinstance(msg["result"], dict):
                try:
                    msg["result"] = callback(msg["result"])
                except Exception as exc:
                    log_debug(f"Transform callback error for id={msg_id}: {exc}")
                self._write_client(msg)
                return

        self._write_client(line)

    def call_upstream(self, method: str, params: dict[str, Any], timeout: float = 15.0) -> dict[str, Any]:
        """Perform a synchronous internal JSON-RPC request against the active upstream FigCraft process."""
        with self.state_lock:
            self.internal_seq += 1
            req_id = f"__bridge_internal_{self.internal_seq}"
            event = threading.Event()
            result_box: list[dict[str, Any]] = []
            self.internal_waiters[req_id] = (event, result_box)

        try:
            self._write_upstream({"jsonrpc": "2.0", "id": req_id, "method": method, "params": params})
            if not event.wait(timeout=timeout):
                raise TimeoutError(f"Upstream FigCraft request '{method}' timed out after {timeout}s.")
            return result_box[0]
        finally:
            with self.state_lock:
                self.internal_waiters.pop(req_id, None)

    def transition_to_attached(self) -> None:
        """Switch from headless to attached GUI mode on the first live canvas interaction."""
        with self.transition_lock:
            if self.is_attached:
                return

            if self.reader_stop_event:
                self.reader_stop_event.set()

            if self.proc:
                try:
                    self.proc.terminate()
                    self.proc.wait(timeout=2)
                except Exception:
                    pass

            log_debug("Switching to attached mode (live canvas request detected)")
            gui_ready = ensure_figcraft_running(self.gui_path, self.port)

            if gui_ready:
                cmd = [str(self.cli_path), "mcp", "--attach", str(self.port)]
                self.is_attached = True
            else:
                cmd = [str(self.cli_path), "mcp"]
                self.is_attached = False

            new_proc = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                text=True,
            )
            self.proc = new_proc

            # Synchronous internal handshake before starting reader thread so init response never leaks
            init_params = self.last_init_params or {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "figcraft-bridge", "version": "1.1"},
            }
            handshake = json.dumps({
                "jsonrpc": "2.0",
                "id": "bridge-init-handshake",
                "method": "initialize",
                "params": init_params,
            }) + "\n"
            assert new_proc.stdin and new_proc.stdout
            new_proc.stdin.write(handshake)
            new_proc.stdin.flush()
            new_proc.stdout.readline()

            notify = json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n"
            new_proc.stdin.write(notify)
            new_proc.stdin.flush()

            self._start_reader_thread(new_proc)

    def _register_intercept(
        self, req_id: Any, callback: Callable[[dict[str, Any]], dict[str, Any]]
    ) -> None:
        if req_id is None:
            return
        with self.state_lock:
            self.intercept_callbacks[_rpc_id_key(req_id)] = callback

    def _handle_client_message(self, raw_line: str) -> None:
        try:
            msg = json.loads(raw_line)
        except json.JSONDecodeError:
            self._write_upstream(raw_line)
            return

        if not isinstance(msg, dict):
            self._write_upstream(raw_line)
            return

        method = msg.get("method", "")
        params = msg.get("params") if isinstance(msg.get("params"), dict) else {}
        req_id = msg.get("id")
        has_id = "id" in msg

        # 1. Protocol discovery & capability enrichment (stays headless)
        if method == "initialize":
            self.last_init_params = params
            if has_id:
                self._register_intercept(req_id, mcp_primitives.merge_initialize_result)
            self._write_upstream(msg)
            return

        if method == "tools/list":
            if has_id:
                self._register_intercept(req_id, mcp_primitives.merge_tools_list)
            self._write_upstream(msg)
            return

        if method == "resources/list":
            if has_id:
                self._register_intercept(req_id, mcp_primitives.merge_resources_list)
            self._write_upstream(msg)
            return

        if method == "resources/templates/list":
            if has_id:
                self._register_intercept(req_id, mcp_primitives.merge_resource_templates_list)
            self._write_upstream(msg)
            return

        if method == "prompts/list":
            if has_id:
                self._register_intercept(req_id, mcp_primitives.merge_prompts_list)
            self._write_upstream(msg)
            return

        # 2. Custom & Live Resources
        if method == "resources/read":
            uri = str(params.get("uri", ""))
            if mcp_primitives.is_live_canvas_uri(uri) and not self.is_attached:
                self.transition_to_attached()

            if mcp_primitives.is_custom_resource_uri(uri):
                if not has_id:
                    return
                try:
                    result = mcp_primitives.handle_custom_resource_read(uri, self.call_upstream)
                    self._write_client(_jsonrpc_result(req_id, result))
                except ValueError as exc:
                    self._write_client(_jsonrpc_error(req_id, -32602, str(exc)))
                except Exception as exc:
                    self._write_client(_jsonrpc_error(req_id, -32603, str(exc)))
                return

            self._write_upstream(msg)
            return

        # 3. Custom Prompts
        if method == "prompts/get":
            prompt_name = str(params.get("name", ""))
            if mcp_primitives.is_custom_prompt(prompt_name):
                if not has_id:
                    return
                try:
                    result = mcp_primitives.handle_custom_prompt_get(
                        prompt_name, params.get("arguments")
                    )
                    self._write_client(_jsonrpc_result(req_id, result))
                except ValueError as exc:
                    self._write_client(_jsonrpc_error(req_id, -32602, str(exc)))
                except Exception as exc:
                    self._write_client(_jsonrpc_error(req_id, -32603, str(exc)))
                return

            self._write_upstream(msg)
            return

        # 4. Tools Call (custom workflow tools + input normalization + lazy attach)
        if method == "tools/call":
            tool_name = str(params.get("name", ""))

            if mcp_primitives.is_custom_tool(tool_name):
                tool_args = params.get("arguments") if isinstance(params.get("arguments"), dict) else {}
                is_dry_run = tool_name == "figcraft_render_template" and tool_args.get("dry_run") is True
                if not mcp_primitives.is_local_only_tool(tool_name) and not is_dry_run and not self.is_attached:
                    self.transition_to_attached()
                if not has_id:
                    return
                try:
                    result = mcp_primitives.handle_custom_tool_call(
                        tool_name, params.get("arguments"), self.call_upstream
                    )
                    self._write_client(_jsonrpc_result(req_id, result))
                except Exception as exc:
                    self._write_client(_jsonrpc_error(req_id, -32603, str(exc)))
                return

            if not self.is_attached:
                self.transition_to_attached()

            msg["params"] = mcp_primitives.normalize_tool_call_params(params)
            self._write_upstream(msg)
            return

        # 5. Default pass-through (notifications, ping, etc.)
        self._write_upstream(raw_line)

    def run(self) -> None:
        self.start_headless()

        for line in sys.stdin:
            if not line:
                break
            try:
                self._handle_client_message(line)
            except Exception as exc:
                log_debug(f"Dispatch error: {exc}")
                break

        # Cleanup on exit
        if self.reader_stop_event:
            self.reader_stop_event.set()
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass


def main() -> None:
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
