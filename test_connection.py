#!/usr/bin/env python3
"""
FigCraft MCP Test Connection Script
-----------------------------------
Verifies that the FigCraft MCP Bridge connects properly and can create elements on the canvas.
"""

import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
BRIDGE_PATH = SCRIPT_DIR / "bridge.py"


def main():
    print("Testing FigCraft MCP Connection...")
    print(f"Bridge Script: {BRIDGE_PATH}")

    proc = subprocess.Popen(
        [sys.executable, str(BRIDGE_PATH)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    def send_rpc(method, params, req_id):
        req = {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params}
        proc.stdin.write(json.dumps(req) + "\n")
        proc.stdin.flush()
        line = proc.stdout.readline()
        return json.loads(line)

    try:
        # 1. Initialize
        print("\n[1/3] Sending MCP Handshake...")
        init_res = send_rpc(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-verifier", "version": "1.0"},
            },
            1,
        )
        server_info = init_res.get("result", {}).get("serverInfo", {})
        print(f"  ✔ Connected to: {server_info.get('title')} v{server_info.get('version')}")

        proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        proc.stdin.flush()

        # 2. Tools List
        print("\n[2/3] Querying MCP Tools...")
        tools_res = send_rpc("tools/list", {}, 2)
        tools = [t["name"] for t in tools_res.get("result", {}).get("tools", [])]
        print(f"  ✔ Total {len(tools)} tools available: {', '.join(tools[:5])}...")

        # 3. Create Demo Badge
        print("\n[3/3] Drawing Test Element in FigCraft...")
        draw_res = send_rpc(
            "tools/call",
            {
                "name": "create_node",
                "arguments": {
                    "type": "frame",
                    "name": "MCP Connection Test Badge",
                    "x": 80,
                    "y": 40,
                    "width": 260,
                    "height": 40,
                    "props": {
                        "fill": "#059669",
                        "cornerRadius": 10,
                        "layout": "horizontal",
                        "mainAlign": "center",
                        "crossAlign": "center",
                    },
                },
            },
            3,
        )

        badge_id = json.loads(draw_res["result"]["content"][0]["text"])["id"]
        send_rpc(
            "tools/call",
            {
                "name": "create_node",
                "arguments": {
                    "parent": badge_id,
                    "type": "text",
                    "name": "Badge Text",
                    "text": "✦ FigCraft MCP Connected! ✦",
                    "props": {"fill": "#FFFFFF", "fontSize": 12},
                },
            },
            4,
        )

        print(f"  ✔ Successfully created Test Badge on FigCraft canvas!")
        print("\n\033[1;32m=== All Tests Passed! FigCraft MCP is 100% Ready! ===\033[0m\n")

    except Exception as e:
        print(f"\n\033[1;31mTest Failed: {e}\033[0m")
        sys.exit(1)
    finally:
        proc.terminate()


if __name__ == "__main__":
    main()
