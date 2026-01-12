# Sky Protocol Terminal Browser

A lightweight, dependency-free terminal browser for the Sky Protocol.

## Requirements
*   **Python 3.6+** (Standard on most Linux distributions)
*   **OpenSSL** support in Python (Standard)

## Installation (Linux/Debian/Ubuntu/Arch)
No external libraries required! Just ensure you have Python 3.

```bash
# Verify Python is installed
python3 --version
```

## Usage

1.  **Mark executable** (Optional but recommended):
    ```bash
    chmod +x terminal_browser.py
    ```

2.  **Run**:
    ```bash
    ./terminal_browser.py [URL]
    ```
    Or:
    ```bash
    python3 terminal_browser.py [URL]
    ```

    *Example*:
    ```bash
    ./terminal_browser.py sky://localhost:1966/test.sky
    ```

## Controls
*   **Numbers [1-9]**: Type the number next to a link to navigate to it.
*   **u [url]**: Type `u` to enter a new URL, or `u sky://...` to jump directly.
*   **r**: Reload current page.
*   **q**: Quit.

## Troubleshooting
*   If you see connection errors, ensure your Sky Server is running on the target host/port (Default 1966).
*   On remote servers (headless), this works perfectly over SSH.
