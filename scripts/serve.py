#!/usr/bin/env python3
"""Local development server with auto-rebuild."""

import functools
import http.server
import os
import socketserver
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"
WATCH_DIRS = [ROOT / "content", ROOT / "templates", ROOT / "static"]


def get_mtimes():
    """Get modification times for all source files."""
    mtimes = {}
    for watch_dir in WATCH_DIRS:
        if watch_dir.exists():
            for f in watch_dir.rglob("*"):
                if f.is_file():
                    mtimes[str(f)] = f.stat().st_mtime
    return mtimes


def rebuild():
    """Run the build script."""
    os.system(f"{sys.executable} {ROOT / 'scripts' / 'build.py'}")


def watcher():
    """Watch for file changes and rebuild."""
    last_mtimes = get_mtimes()
    while True:
        time.sleep(1)
        current = get_mtimes()
        if current != last_mtimes:
            print("\nChange detected, rebuilding...")
            rebuild()
            last_mtimes = get_mtimes()


def serve(port=8000):
    """Serve the site directory."""
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SITE_DIR))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at http://localhost:{port}")
        print("Watching for changes... (Ctrl+C to stop)")
        httpd.serve_forever()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000

    # Initial build
    rebuild()

    # Start file watcher in background
    t = threading.Thread(target=watcher, daemon=True)
    t.start()

    # Serve
    serve(port)
