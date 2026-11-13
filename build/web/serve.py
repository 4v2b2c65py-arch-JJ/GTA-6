#!/usr/bin/env python3
"""
Executable web-based game client & player server for Spatial Avy.
Serves build/web (client UI + packaged codebase snapshot in ./data).
"""

import argparse
import contextlib
import functools
import http.server
import os
import socket
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def find_port(start=8787):
    for p in range(start, start + 50):
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    return start


def main():
    ap = argparse.ArgumentParser(description="Spatial Avy web game client & player")
    ap.add_argument("--port", type=int, default=0, help="Port (default: auto from 8787)")
    ap.add_argument("--no-open", action="store_true", help="Do not open browser")
    args = ap.parse_args()
    port = args.port or find_port()
    os.chdir(ROOT)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))
    with http.server.ThreadingHTTPServer(("127.0.0.1", port), handler) as httpd:
        url = f"http://127.0.0.1:{port}/"
        print(f"Spatial Avy Web Client & Player: {url}")
        print(f"Serving: {ROOT}")
        if not args.no_open:
            try:
                webbrowser.open(url)
            except Exception:
                pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
