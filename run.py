"""
FinPulse AI - Startup Launcher
Runs the local web server and advisor studio.
"""

import socket
import sys
import uvicorn

# Ensure utf-8 encoding on Windows standard out
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

def find_available_port(start_port=8000, max_attempts=20):
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', port)) != 0:
                return port
    return start_port

def main():
    port = find_available_port(8000)
    print("=" * 65)
    print(">> FinPulse AI - Intelligent Financial Planning Suite")
    print(f">> Server running at: http://127.0.0.1:{port}")
    print(">> Dual Modes: 24/7 Client Advisory Chatbot & Advisor Studio")
    print("=" * 65)
    uvicorn.run("app:app", host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    main()
