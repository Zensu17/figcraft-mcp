# FigCraft MCP Installation Guide / Panduan Pemasangan

[English](#english) | [Bahasa Indonesia](#bahasa-indonesia)

---

<a name="english"></a>
## English

Comprehensive step-by-step installation guide for **FigCraft Universal MCP Bridge**.

### Table of Contents
1. [Prerequisites](#1-prerequisites)
2. [Download / Clone Repository](#2-download--clone)
3. [Method 1: Automatic 1-Click Install (Recommended)](#3-method-1-automatic-1-click-install)
4. [Method 2: Manual Setup per AI Client](#4-method-2-manual-setup)
5. [Windows Desktop Shortcut Setup](#5-windows-desktop-shortcut)
6. [Testing & Verification](#6-testing--verification)
7. [Troubleshooting & FAQ](#7-troubleshooting--faq)
8. [Available MCP Tools Reference](#8-mcp-tools-reference)

---

### 1. Prerequisites

Before installing, ensure the following are installed on your computer:

#### A. Python 3.8 or Higher
- Download from the official website [python.org](https://www.python.org/downloads/).
- **IMPORTANT (Windows only)**: During installation, check the box: **"Add python.exe to PATH"**.
- Verify in terminal:
  ```bash
  python --version
  ```

#### B. FigCraft Desktop App & CLI
- Download and install FigCraft. On Windows, the default installation directory is:  
  `C:\Program Files\ArtCraft\FigCraft\` (containing `figcraft.exe` and `figcraft-cli.exe`).
- If installed in a custom location, ensure it is added to your system `PATH` or set the environment variables `FIGCRAFT_PATH` and `FIGCRAFT_CLI_PATH`.

---

### 2. Download / Clone

#### Option A: Using Git (Recommended)
```bash
git clone https://github.com/Zensu17/figcraft-mcp.git
cd figcraft-mcp
```

#### Option B: Download ZIP
1. Go to the repository page on GitHub.
2. Click **Code** > **Download ZIP**.
3. Extract the ZIP archive to your desired directory (e.g., `D:\Code\figcraft-mcp`).
4. Open a terminal inside that folder.

---

### 3. Method 1: Automatic 1-Click Install

The installer detects your Python executable, locates FigCraft, and writes the configuration to all installed AI assistants.

#### On Windows:
Double-click **`install.bat`**, or run:
```powershell
python install.py
```

#### On macOS / Linux:
```bash
chmod +x install.sh
./install.sh
```

**What the installer does automatically:**
1. Verifies `figcraft.exe` and `figcraft-cli.exe` locations.
2. Registers FigCraft in Google AntiGravity: `~/.gemini/config/mcp_config.json`.
3. Registers FigCraft in OpenCode CLI: `~/.config/opencode/opencode.json`.
4. Registers FigCraft in Cursor IDE: `~/.cursor/mcp.json`.
5. Registers FigCraft in Claude Desktop (if installed).
6. Updates Windows Start Menu and Desktop shortcuts to include `--control 1984`.

---

### 4. Method 2: Manual Setup

If you prefer to configure each AI assistant manually:

> Replace `<REPO_PATH>` with the absolute path to this folder (e.g. `D:\\Code\\figcraft-mcp` on Windows or `/home/user/figcraft-mcp` on macOS/Linux).

#### A. Google AntiGravity (CLI & IDE)
Config file: `~/.gemini/config/mcp_config.json`
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

#### B. OpenCode CLI
Run command:
```bash
opencode mcp add --global FigCraft -- python <REPO_PATH>/bridge.py
```
Or edit `~/.config/opencode/opencode.json`:
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

#### C. Cursor IDE
Config file: `~/.cursor/mcp.json`
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

#### D. Claude Desktop
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
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

### 5. Windows Desktop Shortcut

To ensure FigCraft is always ready when opened manually:
1. Right-click the **FigCraft** shortcut > **Properties**.
2. In the **Target** field, append: `--control 1984`
   - Example: `"C:\Program Files\ArtCraft\FigCraft\figcraft.exe" --control 1984`
3. Click **Apply** > **OK**.

*(Note: `install.bat` does this automatically).*

---

### 6. Testing & Verification

Run the test suite:
```bash
# Verify handshake and canvas drawing
python test_connection.py

# Verify Design-to-Code pipeline
python test_design_to_code.py
```

Look at your FigCraft window: you should see the test element drawn live on your canvas!

---

### 7. Troubleshooting & FAQ

- **Error: `python is not recognized`**: Python is not in your system PATH. Re-run Python installer and check "Add python.exe to PATH".
- **Error: `figcraft-cli not found`**: FigCraft is in a custom path. Set environment variable:
  ```powershell
  $env:FIGCRAFT_CLI_PATH = "D:\Path\To\figcraft-cli.exe"
  $env:FIGCRAFT_PATH = "D:\Path\To\figcraft.exe"
  ```
- **Port Conflict**: Change the default port by setting `FIGCRAFT_PORT`:
  ```powershell
  $env:FIGCRAFT_PORT = "2000"
  ```

---

### 8. MCP Tools Reference

When connected, AI agents have access to **19 native FigCraft tools**:

| Tool | Description |
| :--- | :--- |
| `create_node` | Creates frames, text, shapes, vectors, or components |
| `set_properties` | Modifies properties (fills, corner radius, layout, padding, font) |
| `batch` | Runs multiple canvas commands in 1 single undo step |
| `inspect_document` | Returns the entire document layer tree as JSON |
| `get_node` | Fetches details of a specific node ID |
| `screenshot` | Captures visual PNG crop of the page or specific layers |
| `export` | Exports frames to PNG, SVG, JPG, PDF |
| `run_command` | Executes any command from FigCraft's 400+ command registry |
| `undo` / `redo` | Steps forward or backward through document history |
| `open_file` / `save_file` | Opens or saves `.figcraft` document files |
| `select` | Updates the active canvas selection |
| `pointer` / `key` / `type_text` | Simulates canvas gestures, keystrokes, and text typing |

---

<a name="bahasa-indonesia"></a>
## Bahasa Indonesia

Panduan langkah demi langkah untuk memasang dan menghubungkan **FigCraft Universal MCP Bridge** ke berbagai AI Coding Assistant di komputer Anda.

### 1. Prasyarat Sistem
- **Python 3.8+**: Unduh dari [python.org](https://www.python.org/downloads/) dan pastikan centang opsi **"Add python.exe to PATH"**.
- **Aplikasi FigCraft**: Terpasang di lokasi standar (`C:\Program Files\ArtCraft\FigCraft\`).

### 2. Cara Pemasangan Otomatis (1-Klik)
- **Windows**: Klik ganda file **`install.bat`**.
- **macOS / Linux**: Jalankan `./install.sh`.

### 3. Pengujian Koneksi
Jalankan verifikasi:
```bash
python test_connection.py
python test_design_to_code.py
```
Periksa kanvas FigCraft Anda untuk memastikan badge uji coba berhasil dibuat.

### 4. Menghapus Instalasi (Uninstaller)
Cukup klik ganda **`uninstall.bat`** atau jalankan:
```bash
python install.py --uninstall
```
