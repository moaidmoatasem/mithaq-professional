"""
Thin proxy for FE testing:
  - Serves /static/* from packages/cherenkov/api/static/
  - Forwards /api/*, /ws/* to the uvicorn backend on port 8000
  - GET / redirects to /static/index.html
"""
import http.server
import os
import socketserver
import threading
import urllib.request
import urllib.error
from pathlib import Path

BACKEND = "http://localhost:8000"
STATIC_DIR = Path(__file__).parent / "packages" / "cherenkov" / "api" / "static"
PORT = 8001


class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[proxy] {self.address_string()} {fmt % args}")

    def _proxy(self):
        target = BACKEND + self.path
        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in ("host", "content-length")}
        body = None
        length = int(self.headers.get("Content-Length", 0))
        if length:
            body = self.rfile.read(length)

        try:
            req = urllib.request.Request(target, data=body, headers=headers, method=self.command)
            with urllib.request.urlopen(req, timeout=30) as resp:
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ("transfer-encoding",):
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            for k, v in e.headers.items():
                if k.lower() not in ("transfer-encoding",):
                    self.send_header(k, v)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as exc:
            self.send_error(502, str(exc))

    def _serve_static(self):
        # Strip leading /static from path
        rel = self.path.lstrip("/")
        if rel.startswith("static/"):
            rel = rel[len("static/"):]
        file_path = STATIC_DIR / rel
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, f"Not found: {self.path}")
            return
        ext = file_path.suffix.lower()
        mime = {
            ".html": "text/html", ".js": "application/javascript",
            ".css": "text/css", ".svg": "image/svg+xml",
            ".png": "image/png", ".ico": "image/x-icon",
            ".json": "application/json",
        }.get(ext, "application/octet-stream")
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self.send_response(302)
            self.send_header("Location", "/static/index.html")
            self.end_headers()
        elif self.path.startswith("/api/") or self.path.startswith("/health"):
            self._proxy()
        else:
            self._serve_static()

    def do_POST(self):
        self._proxy()

    def do_DELETE(self):
        self._proxy()

    def do_PUT(self):
        self._proxy()

    def do_OPTIONS(self):
        self._proxy()


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Handle each request in a separate thread."""
    daemon_threads = True


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    server = ThreadedHTTPServer(("0.0.0.0", PORT), ProxyHandler)
    print(f"Proxy listening on http://0.0.0.0:{PORT}")
    print(f"Static dir : {STATIC_DIR}")
    print(f"Backend    : {BACKEND}")
    server.serve_forever()
