#!/usr/bin/env python3
import sys
import socket
import ssl
from urllib.parse import urlparse
import shutil
import os

# Configuration
DEFAULT_PORT = 1966
HISTORY = []
LINKS = []

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def style(text, type="text"):
    # ANSI Color codes (Standard on Linux/Mac, works on Win10+)
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    
    if type == "h1": return f"{BOLD}{MAGENTA}{text}{RESET}"
    if type == "h2": return f"{BOLD}{BLUE}{text}{RESET}"
    if type == "h3": return f"{CYAN}{text}{RESET}"
    if type == "link": return f"{GREEN}{text}{RESET}"
    if type == "meta": return f"{DIM}{text}{RESET}"
    if type == "error": return f"{RED}Error: {text}{RESET}"
    if type == "prompt": return f"{YELLOW}{text}{RESET}"
    return text

def fetch_url(url):
    try:
        if "://" not in url:
             url = "sky://" + url
        
        parsed = urlparse(url)
        host = parsed.hostname
        port = parsed.port or DEFAULT_PORT
        
        # Simple blocking socket
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                # Sky Protocol Request: URL + CRLF
                ssock.sendall(f"{url}\r\n".encode('utf-8'))
                
                response_data = b""
                while True:
                    chunk = ssock.recv(4096)
                    if not chunk: break
                    response_data += chunk
        
        return response_data.decode('utf-8', errors='replace')
    except Exception as e:
        return f"Error loading {url}: {e}"

def upload_file(host, port, filepath, token):
    try:
        # 1. Read File
        if not os.path.exists(filepath):
            return "Error: File not found"
        
        with open(filepath, 'rb') as f:
            file_data = f.read() # Read binary
            
        size = len(file_data)
        
        # 2. Connect
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                # 3. Send DRIFT header
                header = f"DRIFT size={size};token={token}\r\n"
                ssock.sendall(header.encode('utf-8'))
                
                # 4. Send Body
                ssock.sendall(file_data)
                
                # 5. Read Response
                response_data = b""
                while True:
                    chunk = ssock.recv(4096)
                    if not chunk: break
                    response_data += chunk
                    
        return response_data.decode('utf-8', errors='replace')

    except Exception as e:
        return f"Upload Error: {e}"


def render_page(url, raw_response):
    global LINKS
    LINKS = []
    
    clear_screen()
    
    if raw_response.startswith("Error"):
        print(style(raw_response, "error"))
        return

    lines = raw_response.splitlines()
    if not lines:
        print(style("Empty response", "meta"))
        return

    status_line = lines[0]
    cols = shutil.get_terminal_size().columns
    print(style(f" {url} ", "meta").center(cols, "─"))
    print(style(f" {status_line} ", "meta").center(cols))
    print("─" * cols)
    
    # Skip headers (find first blank line)
    body_start = 1
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "":
            body_start = i + 1
            break
            
    # Render Body
    link_counter = 1
    
    for line in lines[body_start:]:
        line = line.strip()
        if not line:
            print()
            continue

        if line.startswith("### "):
            print(style(line[4:], "h3"))
        elif line.startswith("## "):
            print(style(line[3:], "h2"))
        elif line.startswith("# "):
            print(style(line[2:], "h1"))
        elif line.startswith("=>"):
            parts = line[2:].strip().split(maxsplit=1)
            target = parts[0]
            label = parts[1] if len(parts) > 1 else target
            
            # Resolve relative URL
            full_target = target
            if "://" not in target:
                 base = urlparse(url)
                 if target.startswith("/"):
                     full_target = f"{base.scheme}://{base.hostname}:{base.port or DEFAULT_PORT}{target}"
                 else:
                     full_target = f"{base.scheme}://{base.hostname}:{base.port or DEFAULT_PORT}/{target}"

            LINKS.append(full_target)
            print(f"[{link_counter}] {style(label, 'link')} ({target})")
            link_counter += 1
        elif line.startswith("* "):
            print(f" • {line[2:]}")
        elif line.startswith(">"):
            print(f"   | {style(line[1:], 'meta')}")
        elif line.startswith("```"):
            print(style(line, "meta"))
        else:
            print(line)
            
    print("─" * cols)

def main():
    if len(sys.argv) > 1:
        current_url = sys.argv[1]
    else:
        current_url = "browser://home"

    while True:
        try:
            # Fetch and Render
            if current_url == "browser://home":
                raw = """20 text/sky
# Welcome to Cumulus Browser
VERSION: 1.0 (Terminal Edition)

Sky Protocol Browser
Enter any sky:// URL to browse the open network.


## Controls
* Type [u] to enter a URL
* Type a number to follow a link
* Type [d] to upload a file (Drift)
* Type [q] to quit
"""
            else:
                raw = fetch_url(current_url)
            
            render_page(current_url, raw)
            
            # Status Bar
            print(f"{style('Controls:', 'meta')} [N]umber, [u]rl, [d]rift, [b]ack, [r]eload, [q]uit")
            cmd = input(style("sky> ", "prompt")).strip()
            
            if cmd.lower() in ['q', 'quit', 'exit']:
                break
            elif cmd.lower() in ['r', 'reload']:
                continue
            elif cmd.lower() in ['b', 'back']:
                if HISTORY:
                    current_url = HISTORY.pop()
                else:
                    input(style("No history. Press Enter.", "error"))
                continue
            elif cmd.lower().startswith('u'):
                parts = cmd.split(' ', 1)
                if len(parts) > 1:
                    new_u = parts[1]
                else:
                    new_u = input("URL: ")
                
                if "://" not in new_u: new_u = "sky://" + new_u
                
                # Push current to history before moving
                HISTORY.append(current_url)
                current_url = new_u
            elif cmd.lower() in ['d', 'drift', 'upload']:
                # Drift Upload Handler
                print(style("\n--- Drift Upload ---", "h2"))
                target_host = input("Target Host (default: localhost): ").strip() or "localhost"
                target_port = input(f"Target Port (default: {DEFAULT_PORT}): ").strip()
                target_port = int(target_port) if target_port else DEFAULT_PORT
                
                fpath = input("File to upload: ").strip()
                token = input("Drift Token: ").strip()
                
                if not fpath or not token:
                     print(style(" cancelled.", "error"))
                     input("Press Enter to continue...")
                     continue

                print(style("Uploading...", "meta"))
                res = upload_file(target_host, target_port, fpath, token)
                
                print(style("\nResponse:", "h3"))
                print(res)
                input(style("Press Enter to continue...", "meta"))
            elif cmd.isdigit():
                idx = int(cmd) - 1
                if 0 <= idx < len(LINKS):
                    # Push current to history
                    HISTORY.append(current_url)
                    current_url = LINKS[idx]
                else:
                    input(style("Invalid link number. Press Enter.", "error"))
            elif cmd:
                # Direct URL entry fallback
                if "://" in cmd:
                    HISTORY.append(current_url)
                    current_url = cmd
                
        except KeyboardInterrupt:
            print("\nBye!")
            break
        except Exception as e:
            input(f"Error: {e}. Press Enter.")

if __name__ == "__main__":
    main()
