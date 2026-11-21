#!/usr/bin/env python3
"""
FigCraft MCP Security & Boundary Validation Controls
----------------------------------------------------
Implements STRIDE-aligned input validation, path traversal / UNC blocking,
hex color sanitization, JSON-RPC resource caps, and log sanitization.

Zero external dependencies: 100% Python standard library.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

MAX_RPC_LINE_BYTES = 2 * 1024 * 1024  # 2 MiB per JSON-RPC message
MAX_JSON_DEPTH = 48
MAX_BATCH_COMMANDS = 500
MIN_UNPRIVILEGED_PORT = 1024
MAX_PORT = 65535

_HEX_COLOR_RE = re.compile(r"^#(?:[0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$")
_CONTROL_CHARS_RE = re.compile(r"[\x00-\x1f\x7f]")

_FILE_TOOLS = {"open_file", "save_file", "export", "screenshot"}
_PATH_PARAM_KEYS = ("path", "file", "filePath", "output", "outputPath", "destination")


def validate_port(raw_port: Any) -> int:
    """Validate that TCP loopback port is an unprivileged integer in [1024, 65535]."""
    if isinstance(raw_port, bool) or raw_port is None:
        raise ValueError(f"Invalid TCP port '{raw_port}': expected integer in {MIN_UNPRIVILEGED_PORT}..{MAX_PORT}.")
    try:
        port = int(raw_port)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid TCP port '{raw_port}': expected integer in {MIN_UNPRIVILEGED_PORT}..{MAX_PORT}."
        ) from exc

    if not (MIN_UNPRIVILEGED_PORT <= port <= MAX_PORT):
        raise ValueError(
            f"TCP port {port} out of allowed unprivileged range ({MIN_UNPRIVILEGED_PORT}..{MAX_PORT})."
        )
    return port


def validate_hex_color(value: Any) -> str | None:
    """Return stripped hex color string if strictly valid (#RGB, #RRGGBB, #RRGGBBAA), else None."""
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    if _HEX_COLOR_RE.match(cleaned):
        return cleaned
    return None


def get_configured_allowed_roots() -> list[Path] | None:
    """Read optional FIGCRAFT_ALLOWED_ROOTS env var (os.pathsep separated) into resolved Paths."""
    raw = os.environ.get("FIGCRAFT_ALLOWED_ROOTS", "").strip()
    if not raw:
        return None
    roots: list[Path] = []
    for entry in raw.split(os.pathsep):
        item = entry.strip()
        if item:
            roots.append(Path(item).expanduser().resolve())
    return roots or None


def validate_file_path(raw_path: Any, allowed_roots: list[Path] | None = None) -> Path:
    """
    Validate file path against null bytes, UNC network shares (NTLM leak),
    parent directory traversal ('..'), and optional allowlisted roots.
    """
    if not isinstance(raw_path, str):
        raise ValueError("File path must be a non-empty string.")

    stripped = raw_path.strip()
    if not stripped:
        raise ValueError("File path cannot be empty.")

    if "\x00" in stripped or _CONTROL_CHARS_RE.search(stripped):
        raise ValueError("File path contains forbidden null or control characters.")

    # Block UNC / SMB network share paths (\\host\share or //host/share)
    if stripped.startswith("\\\\") or stripped.startswith("//"):
        raise ValueError("UNC network share paths are blocked for security.")

    # Reject explicit traversal segments before resolution
    normalized_parts = stripped.replace("\\", "/").split("/")
    if ".." in normalized_parts:
        raise ValueError("Path traversal ('..') segments are not allowed.")

    resolved = Path(stripped).expanduser().resolve()

    effective_roots = allowed_roots if allowed_roots is not None else get_configured_allowed_roots()
    if effective_roots:
        resolved_roots = [r.expanduser().resolve() for r in effective_roots]
        if not any(resolved.is_relative_to(root) for root in resolved_roots):
            raise ValueError(
                "Target path is outside configured FIGCRAFT_ALLOWED_ROOTS."
            )

    return resolved


def validate_raw_line_size(line: str, max_bytes: int = MAX_RPC_LINE_BYTES) -> None:
    """Reject oversized JSON-RPC input frames before parsing."""
    size = len(line.encode("utf-8", errors="ignore"))
    if size > max_bytes:
        raise ValueError(f"JSON-RPC message size ({size} bytes) exceeds limit of {max_bytes} bytes.")


def validate_json_depth(obj: Any, max_depth: int = MAX_JSON_DEPTH) -> None:
    """Iteratively verify JSON nesting depth does not exceed max_depth."""
    stack: list[tuple[Any, int]] = [(obj, 0)]
    while stack:
        current, depth = stack.pop()
        if depth > max_depth:
            raise ValueError(f"JSON nesting depth exceeds maximum allowed depth ({max_depth}).")
        if isinstance(current, dict):
            for val in current.values():
                if isinstance(val, (dict, list)):
                    stack.append((val, depth + 1))
        elif isinstance(current, list):
            for item in current:
                if isinstance(item, (dict, list)):
                    stack.append((item, depth + 1))


def _audit_path_arguments(args: dict[str, Any]) -> None:
    for key in _PATH_PARAM_KEYS:
        if key in args and args[key] is not None:
            validate_file_path(args[key])


def validate_tool_call_security(params: dict[str, Any]) -> None:
    """Enforce boundary security rules on incoming MCP tools/call payloads."""
    tool_name = str(params.get("name", "")).strip()
    arguments = params.get("arguments")
    if arguments is None:
        return
    if not isinstance(arguments, dict):
        raise ValueError("Tool arguments must be a JSON object.")

    if tool_name in _FILE_TOOLS:
        _audit_path_arguments(arguments)
        return

    if tool_name == "run_command":
        cmd = str(arguments.get("command", "")).strip().lower()
        cmd_params = arguments.get("params")
        if isinstance(cmd_params, dict) and (
            cmd.startswith("file.") or cmd.startswith("doc.") or "export" in cmd
        ):
            _audit_path_arguments(cmd_params)
        return

    if tool_name == "batch":
        commands = arguments.get("commands")
        if isinstance(commands, list):
            if len(commands) > MAX_BATCH_COMMANDS:
                raise ValueError(
                    f"Batch contains {len(commands)} commands, exceeding limit of {MAX_BATCH_COMMANDS}."
                )
            for step in commands:
                if not isinstance(step, dict):
                    continue
                cmd = str(step.get("command", "")).strip().lower()
                step_params = step.get("params")
                if isinstance(step_params, dict) and (
                    cmd.startswith("file.") or cmd.startswith("doc.") or "export" in cmd
                ):
                    _audit_path_arguments(step_params)


def sanitize_log_message(msg: str) -> str:
    """Strip CR/LF and control characters to prevent log forging/injection."""
    return _CONTROL_CHARS_RE.sub(" ", str(msg)).strip()
