#!/usr/bin/env python3
"""
FigCraft Universal MCP Bridge - Environment Self-Diagnosis Tool
---------------------------------------------------------------
Performs non-destructive health checks to verify that Python, FigCraft,
network ports, and AI assistant configurations are properly set up.
"""

import json
import os
import platform
import shutil
import socket
import subprocess
import sys
from pathlib import Path

# ANSI Color Codes
GREEN = "\033[32m"
RED = "\033[31m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
BOLD = "\033[1m"
RESET = "\033[0m"

PASS_TAG = f"{GREEN}[OK]{RESET}"
FAIL_TAG = f"{RED}[FAIL]{RESET}"
WARN_TAG = f"{YELLOW}[WARN]{RESET}"
INFO_TAG = f"{CYAN}[INFO]{RESET}"

SCRIPT_DIR = Path(__file__).resolve().parent
BRIDGE_PATH = SCRIPT_DIR / "bridge.py"


class DiagnosisReport:
    def __init__(self):
        self.passed = 0
        self.warnings = 0
        self.failures = 0
        self.remedies = []

    def add_pass(self, title: str, detail: str = ""):
        self.passed += 1
        msg = f"  {PASS_TAG} {title}"
        if detail:
            msg += f" ({detail})"
        print(msg)

    def add_warn(self, title: str, remedy: str = ""):
        self.warnings += 1
        print(f"  {WARN_TAG} {title}")
        if remedy:
            self.remedies.append(f"Warning: {title}\n    Action: {remedy}")

    def add_fail(self, title: str, remedy: str = ""):
        self.failures += 1
        print(f"  {FAIL_TAG} {title}")
        if remedy:
            self.remedies.append(f"Critical: {title}\n    Action: {remedy}")


def check_python(report: DiagnosisReport):
    print(f"\n{BOLD}1. Checking Python Environment...{RESET}")
    v = sys.version_info
    v_str = f"{v.major}.{v.minor}.{v.micro}"
    if v >= (3, 8):
        report.add_pass(f"Python runtime version: {v_str}", sys.executable)
    else:
        report.add_fail(
            f"Python runtime version {v_str} is below the 3.8 minimum requirement",
            "Please install Python 3.8 or higher from https://www.python.org/downloads/."
        )


def find_figcraft_binaries() -> tuple[Path | None, Path | None]:
    cli_path = None
    gui_path = None

    # 1. Environment variables
    if os.environ.get("FIGCRAFT_CLI_PATH"):
        p = Path(os.environ["FIGCRAFT_CLI_PATH"])
        if p.is_file():
            cli_path = p
    if os.environ.get("FIGCRAFT_PATH"):
        p = Path(os.environ["FIGCRAFT_PATH"])
        if p.is_file():
            gui_path = p

    # 2. PATH resolution
    if not cli_path:
        w = shutil.which("figcraft-cli") or shutil.which("figcraft-cli.exe")
        if w:
            cli_path = Path(w)
    if not gui_path:
        w = shutil.which("figcraft") or shutil.which("figcraft.exe")
        if w:
            gui_path = Path(w)

    # 3. Standard paths on Windows
    if platform.system() == "Windows":
        base = Path(os.environ.get("PROGRAMFILES", r"C:\Program Files")) / "ArtCraft" / "FigCraft"
        if not cli_path and (base / "figcraft-cli.exe").is_file():
            cli_path = base / "figcraft-cli.exe"
        if not gui_path and (base / "figcraft.exe").is_file():
            gui_path = base / "figcraft.exe"

    return cli_path, gui_path


def check_figcraft(report: DiagnosisReport) -> tuple[Path | None, Path | None]:
    print(f"\n{BOLD}2. Checking FigCraft Binaries...{RESET}")
    cli_path, gui_path = find_figcraft_binaries()

    if cli_path and cli_path.is_file():
        report.add_pass("Found FigCraft CLI executable", str(cli_path))
    else:
        report.add_fail(
            "FigCraft CLI binary not found",
            "Ensure FigCraft is installed or set environment variable $env:FIGCRAFT_CLI_PATH."
        )

    if gui_path and gui_path.is_file():
        report.add_pass("Found FigCraft GUI executable", str(gui_path))
    else:
        report.add_warn(
            "FigCraft GUI binary not found in standard location",
            "Set environment variable $env:FIGCRAFT_PATH if FigCraft is in a custom path."
        )

    return cli_path, gui_path


def check_port(report: DiagnosisReport):
    print(f"\n{BOLD}3. Checking Loopback Port 1984...{RESET}")
    port = int(os.environ.get("FIGCRAFT_PORT", 1984))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.5)

    try:
        sock.connect(("127.0.0.1", port))
        sock.close()
        report.add_pass(
            f"Port {port} is active and listening",
            "FigCraft GUI with --control 1984 is currently running."
        )
    except (ConnectionRefusedError, socket.timeout, OSError):
        report.add_pass(
            f"Port {port} is free and ready",
            "Bridge will launch FigCraft GUI automatically on-demand."
        )


def check_windows_shortcuts(report: DiagnosisReport, gui_path: Path | None):
    if platform.system() != "Windows":
        return

    print(f"\n{BOLD}4. Checking Windows Desktop & Start Menu Shortcuts...{RESET}")
    desktop_lnk = Path(os.environ.get("USERPROFILE", "")) / "Desktop" / "FigCraft.lnk"
    start_lnk = (
        Path(os.environ.get("APPDATA", ""))
        / "Microsoft"
        / "Windows"
        / "Start Menu"
        / "Programs"
        / "ArtCraft"
        / "FigCraft.lnk"
    )

    found_any = False
    for p in [desktop_lnk, start_lnk]:
        if p.is_file():
            found_any = True
            # Read binary content to check if argument '--control 1984' is present
            try:
                raw = p.read_bytes()
                if b"--control" in raw and b"1984" in raw:
                    report.add_pass(f"Shortcut configured with --control 1984: {p.name}")
                else:
                    report.add_warn(
                        f"Shortcut {p.name} does not contain '--control 1984'",
                        f"Run install.bat or add --control 1984 to Target field in {p}."
                    )
            except Exception as e:
                report.add_warn(f"Could not inspect {p.name} ({e})")

    if not found_any:
        report.add_warn(
            "FigCraft desktop shortcut not found in standard locations",
            "If launching manually, run: figcraft.exe --control 1984"
        )


def check_ai_configs(report: DiagnosisReport):
    print(f"\n{BOLD}5. Checking AI Assistant MCP Configurations...{RESET}")

    home = Path.home()
    configs = [
        ("Google AntiGravity", home / ".gemini" / "config" / "mcp_config.json", "mcpServers"),
        ("OpenCode CLI", home / ".config" / "opencode" / "opencode.json", "mcp"),
        ("Cursor IDE", home / ".cursor" / "mcp.json", "mcpServers"),
    ]

    if platform.system() == "Windows":
        configs.append(
            ("Claude Desktop", Path(os.environ.get("APPDATA", "")) / "Claude" / "claude_desktop_config.json", "mcpServers")
        )
    elif platform.system() == "Darwin":
        configs.append(
            ("Claude Desktop", home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json", "mcpServers")
        )

    registered_count = 0
    for name, path, root_key in configs:
        if not path.is_file():
            continue

        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            servers = data.get(root_key, {})
            if "FigCraft" in servers:
                report.add_pass(f"{name} is configured", str(path))
                registered_count += 1
            else:
                report.add_warn(
                    f"{name} config found, but 'FigCraft' is not registered",
                    f"Run python install.py to register FigCraft in {name}."
                )
        except Exception as e:
            report.add_warn(f"Failed to parse {name} configuration: {e}")

    if registered_count == 0:
        report.add_warn(
            "No AI assistants currently have FigCraft registered",
            "Run install.bat or 'python install.py' to register FigCraft automatically."
        )


def check_headless_handshake(report: DiagnosisReport, cli_path: Path | None):
    print(f"\n{BOLD}6. Testing MCP Headless Protocol Handshake...{RESET}")
    if not cli_path or not cli_path.is_file():
        report.add_fail("Skipping handshake test: FigCraft CLI not found")
        return

    req = json.dumps({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "figcraft-check", "version": "1.0.0"}
        }
    }) + "\n"

    try:
        proc = subprocess.Popen(
            [str(cli_path), "mcp"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        stdout, _ = proc.communicate(input=req, timeout=5)
        if not stdout:
            report.add_fail("FigCraft CLI did not return response to initialize handshake")
            return

        res = json.loads(stdout.strip())
        if "result" in res and res["result"].get("serverInfo", {}).get("name") == "figcraft":
            server_title = res["result"].get("serverInfo", {}).get("title", "FigCraft")
            report.add_pass("Headless MCP handshake responded with valid JSON-RPC 2.0", f"Server: {server_title}")
        else:
            report.add_fail("FigCraft CLI returned invalid handshake response", stdout)
    except subprocess.TimeoutExpired:
        proc.kill()
        report.add_fail("Handshake timed out after 5 seconds")
    except Exception as e:
        report.add_fail(f"Handshake error: {e}")


def main():
    print(f"{BOLD}{'=' * 65}{RESET}")
    print(f"{BOLD}   FigCraft Universal MCP Bridge - Environment Health Check   {RESET}")
    print(f"{BOLD}{'=' * 65}{RESET}")

    report = DiagnosisReport()

    check_python(report)
    cli_path, gui_path = check_figcraft(report)
    check_port(report)
    check_windows_shortcuts(report, gui_path)
    check_ai_configs(report)
    check_headless_handshake(report, cli_path)

    print(f"\n{BOLD}{'=' * 65}{RESET}")
    print(f"{BOLD}Diagnosis Summary:{RESET}")
    print(f"  Passed Checks   : {report.passed}")
    print(f"  Warnings        : {report.warnings}")
    print(f"  Critical Errors : {report.failures}")

    if report.remedies:
        print(f"\n{BOLD}Recommended Remediation Steps:{RESET}")
        for idx, item in enumerate(report.remedies, 1):
            print(f"  [{idx}] {item}")

    if report.failures == 0:
        print(f"\n{BOLD}{GREEN}Result: Your environment is healthy and ready for FigCraft MCP!{RESET}\n")
        sys.exit(0)
    else:
        print(f"\n{BOLD}{RED}Result: Critical issues detected. Please review recommendations above.{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
