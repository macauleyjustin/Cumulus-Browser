# Cumulus Browser

A terminal-based browser for the **Sky Protocol**.

## Features
- Browsing `sky://` sites.
- Rendering Gemini/Sky gemtext format.
- **Drift Support**: Upload files to Sky Servers using authenticated Drift tokens.
- History navigation (Back/Forward).

## Usage
Run the browser from the terminal:
```bash
python3 terminal_browser.py [url]
```
If no URL is provided, it opens the Home Page.

### Controls
- `[number]`: Follow a link by index.
- `u`: Enter a new URL.
- `d`: **Drift Upload** - Upload a file to a server.
- `b`: Go Back.
- `r`: Reload.
- `q`: Quit.

### Drift Uploads
1. Press `d`.
2. Enter the Target Host (e.g., `localhost` or `example.com`).
3. Enter the Port (Default: 1966).
4. Enter the path to the file you want to upload.
5. Enter your **Drift Token** (provided by the server administrator).

## Requirements
- Python 3.6+
- No external pip packages required (uses standard library `socket`, `ssl`, `urllib`).
