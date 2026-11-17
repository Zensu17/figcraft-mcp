# FigCraft MCP Installation Guide

> Comprehensive step-by-step setup guide for connecting FigCraft with AI assistants on your computer.

**English** | [Baca dalam Bahasa Indonesia](INSTALLATION.id.md)

---

## Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Download / Clone Repository](#2-download--clone-repository)
3. [Method 1: Automatic 1-Click Install (Recommended)](#3-method-1-automatic-1-click-install-recommended)
4. [Method 2: Manual Setup per AI Client](#4-method-2-manual-setup-per-ai-client)
5. [Windows Desktop Shortcut Setup](#5-windows-desktop-shortcut-setup)
6. [Testing & Verification](#6-testing--verification)
7. [Troubleshooting & FAQ](#7-troubleshooting--faq)
8. [Available MCP Tools Reference](#8-available-mcp-tools-reference)

---

## 1. Prerequisites

Before installing, ensure the following tools are installed on your computer:

### A. Python 3.8 or Higher
- Download from the official website [python.org](https://www.python.org/downloads/).
- **Important (Windows only)**: During installation, make sure to check the box: **"Add python.exe to PATH"**.
- Verify your installation in a terminal:
  ```bash
  python --version
  ```

### B. FigCraft Desktop App & CLI
- Download and install FigCraft. On Windows, the default installation directory is:
  `C:\Program Files\ArtCraft\FigCraft\` (containing `figcraft.exe` and `figcraft-cli.exe`).
- If you installed FigCraft in a custom directory, make sure that directory is added to your system `PATH`, or set the environment variables `FIGCRAFT_PATH` and `FIGCRAFT_CLI_PATH`.

---

## 2. Download / Clone Repository

### Option A: Using Git (Recommended)
Open your terminal and run:
```bash
git clone https://github.com/Zensu17/figcraft-mcp.git
cd figcraft-mcp
```

### Option B: Download ZIP
1. Open the repository page on GitHub.
2. Click **Code** and select **Download ZIP**.
3. Extract the ZIP archive into your chosen directory (for example, `D:\Code\figcraft-mcp`).
4. Open a terminal inside that folder.

---

## 3. Method 1: Automatic 1-Click Install (Recommended)

The automated installer detects your Python environment and FigCraft binary locations, then registers the bridge across all detected AI assistants.

### On Windows
Double-click **`install.bat`**, or execute in PowerShell:
```powershell
python install.py
```

### On macOS / Linux
Run in your terminal:
```bash
chmod +x install.sh
./install.sh
```

### What the Automated Installer Does
1. Verifies the paths for `figcraft.exe` and `figcraft-cli.exe`.
2. Registers FigCraft in Google AntiGravity: `~/.gemini/config/mcp_config.json`.
3. Registers FigCraft in OpenCode CLI: `~/.config/opencode/opencode.json`.
4. Registers FigCraft in Cursor IDE: `~/.cursor/mcp.json`.
5. Registers FigCraft in Claude Desktop (if installed).
6. Configures Windows Start Menu and Desktop shortcuts to include the `--control 1984` control flag.

---

## 4. Method 2: Manual Setup per AI Client

If you prefer to configure each AI assistant manually, follow the instructions below.

Replace `<REPO_PATH>` with the absolute path to this folder (for example, `D:\\Code\\figcraft-mcp` on Windows or `/home/username/figcraft-mcp` on Linux/macOS).

### A. Google AntiGravity (CLI & IDE)
Configuration file: `~/.gemini/config/mcp_config.json`
```json
{
  "mcpServers": {
    "FigCraft": {
      "command": "python",
      "args": ["<REPO_PATH>\\bridge.py"]
    }
  }
}
```

### B. OpenCode CLI
Run the following terminal command:
```bash
opencode mcp add --global FigCraft -- python <REPO_PATH>/bridge.py
```
Or edit `~/.config/opencode/opencode.json` directly:
```json
{
  "mcp": {
    "FigCraft": {
      "type": "local",
      "command": ["python", "<REPO_PATH>\\bridge.py"],
      "enabled": true
    }
  }
}
```

### C. Cursor IDE
Configuration file: `~/.cursor/mcp.json`
```json
{
  "mcpServers": {
    "FigCraft": {
      "command": "python",
      "args": ["<REPO_PATH>\\bridge.py"]
    }
  }
}
```

### D. Claude Desktop
- Windows path: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS path: `~/Library/Application Support/Claude/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "FigCraft": {
      "command": "python",
      "args": ["<REPO_PATH>\\bridge.py"]
    }
  }
}
```

---

## 5. Windows Desktop Shortcut Setup

To ensure FigCraft is always ready when you launch it manually outside of AI sessions:
1. Right-click the **FigCraft** shortcut on your Desktop or Start Menu, then choose **Properties**.
2. In the **Target** field, add a space followed by `--control 1984` at the very end.
   - Example target: `"C:\Program Files\ArtCraft\FigCraft\figcraft.exe" --control 1984`
3. Click **Apply**, then click **OK**.

Note: If you run `install.bat`, this shortcut configuration is performed automatically.

---

## 6. Testing & Verification

Once installation is finished, run these verification commands to ensure communication works smoothly:

```bash
# 1. Run automated environment health check
python check.py
# (On Windows, double-click check.bat)

# 2. Test MCP handshake and canvas badge drawing
python test_connection.py

# 3. Test Design-to-Code visual token conversion
python test_design_to_code.py
```

Look at your FigCraft window: the test elements will be drawn live on the active canvas.

---

## 7. Troubleshooting & FAQ

Before troubleshooting individual issues, run the diagnostic tool to automatically identify the cause:
```bash
python check.py
```

### Issue 1: Error 'python' is not recognized
- **Cause**: Python is not included in your operating system PATH environment variable.
- **Solution**: Re-run the official Python installer, choose "Modify", and make sure **"Add python.exe to PATH"** is selected.

### Issue 2: Error 'figcraft-cli not found'
- **Cause**: FigCraft is installed in a non-standard directory and could not be detected automatically.
- **Solution**: Explicitly set the binary locations in environment variables:
  ```powershell
  $env:FIGCRAFT_CLI_PATH = "D:\Path\To\figcraft-cli.exe"
  $env:FIGCRAFT_PATH = "D:\Path\To\figcraft.exe"
  ```

### Issue 3: Port conflict on port 1984
- **Cause**: Another service or process is already listening on local port 1984.
- **Solution**: Change the communication port by setting `FIGCRAFT_PORT`:
  ```powershell
  $env:FIGCRAFT_PORT = "2000"
  ```

### Issue 4: FigCraft window opens but canvas commands time out
- **Cause**: The application was launched manually without the `--control 1984` flag.
- **Solution**: Close FigCraft. Either launch it via your configured desktop shortcut with `--control 1984`, or let the bridge launch FigCraft automatically on demand.

---

## 8. Available MCP Tools Reference

When connected, AI agents have access to **19 native FigCraft tools**:

| Tool Name | Purpose and Description |
| :--- | :--- |
| `create_node` | Creates frames, text, geometric shapes, vectors, or components on canvas |
| `set_properties` | Modifies properties (fills, corner radius, layout mode, padding, typography) |
| `batch` | Executes multiple canvas commands within a single undo transaction |
| `inspect_document` | Retrieves the entire document layer tree as structured JSON |
| `get_node` | Fetches details and properties of a specific layer node ID |
| `screenshot` | Captures a visual image (PNG) of the active canvas or specific layers |
| `export` | Exports selected frames to PNG, SVG, JPG, or PDF files |
| `run_command` | Executes internal commands from FigCraft's 400+ command registry |
| `undo` / `redo` | Steps backward or forward in canvas edit history |
| `open_file` / `save_file` | Opens or saves `.figcraft` document files |
| `select` | Selects specific active elements on the canvas |
| `pointer` | Simulates mouse clicks, dragging, and hover interactions on canvas |
| `key` / `type_text` | Simulates keyboard inputs and text string typing |
| `inspect_ui` | Inspects current desktop application UI status |
| `wait_for_changes` | Waits for canvas processing and rendering to finish |
