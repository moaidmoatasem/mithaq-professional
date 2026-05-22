"""
Threaded HTTP+WebSocket proxy for FE testing:
  - Serves /static/* from packages/cherenkov/api/static/
  - Forwards /api/*, /health to uvicorn backend on port 8000
  - Tunnels WebSocket upgrades (ws://localhost:8001/ws/*) to backend
  - 2-second in-memory cache for GET /api/v1/* to tame polling storm
  - GET / -> redirect to /static/index.html
"""
import http.server
import os
import select
import socket
import socketserver
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path

BACKEND_HOST = "localhost"
BACKEND_PORT = 8000
BACKEND = f"http://{BACKEND_HOST}:{BACKEND_PORT}"
STATIC_DIR = Path(__file__).parent / "packages" / "cherenkov" / "api" / "static"
PORT = 8001

# ── 2-second GET cache to absorb polling storm ───────────────────────────────
_cache: dict[str, tuple[float, int, list, bytes]] = {}  # path -> (ts, status, headers, body)
_cache_lock = threading.Lock()
CACHE_TTL = 2.0  # seconds


def _cache_get(path: str):
    with _cache_lock:
        entry = _cache.get(path)
        if entry and (time.time() - entry[0]) < CACHE_TTL:
            return entry[1], entry[2], entry[3]
    return None


def _cache_set(path: str, status: int, headers: list, body: bytes):
    with _cache_lock:
        _cache[path] = (time.time(), status, headers, body)


# ── Proxy handler ─────────────────────────────────────────────────────────────

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # silence per-request noise; errors still go to stderr

    # ── WebSocket tunnel ──────────────────────────────────────────────────────
    def _is_ws_upgrade(self):
        return (
            self.headers.get("Upgrade", "").lower() == "websocket"
            and "upgrade" in self.headers.get("Connection", "").lower()
        )

    def _tunnel_websocket(self):
        """Forward raw WebSocket bytes between browser and backend."""
        try:
            backend_sock = socket.create_connection((BACKEND_HOST, BACKEND_PORT), timeout=10)
        except OSError as e:
            self.send_error(502, f"WS backend unreachable: {e}")
            return

        # Replay the HTTP upgrade request to the backend
        request_line = f"{self.command} {self.path} HTTP/1.1\r\n"
        headers = f"Host: {BACKEND_HOST}:{BACKEND_PORT}\r\n"
        for k, v in self.headers.items():
            if k.lower() != "host":
                headers += f"{k}: {v}\r\n"
        headers += "\r\n"
        backend_sock.sendall((request_line + headers).encode())

        client_sock = self.connection

        def _relay(src, dst):
            try:
                while True:
                    r, _, _ = select.select([src], [], [], 30)
                    if not r:
                        break
                    data = src.recv(65536)
                    if not data:
                        break
                    dst.sendall(data)
            except Exception:
                pass
            finally:
                try:
                    dst.shutdown(socket.SHUT_WR)
                except Exception:
                    pass

        t1 = threading.Thread(target=_relay, args=(backend_sock, client_sock), daemon=True)
        t2 = threading.Thread(target=_relay, args=(client_sock, backend_sock), daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        try:
            backend_sock.close()
        except Exception:
            pass

    # ── HTTP proxy ────────────────────────────────────────────────────────────
    def _proxy(self, use_cache=False):
        target = BACKEND + self.path

        if use_cache:
            cached = _cache_get(self.path)
            if cached:
                status, hdrs, body = cached
                self.send_response(status)
                for k, v in hdrs:
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(body)
                return

        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in ("host", "content-length")}
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else None

        try:
            req = urllib.request.Request(target, data=body, headers=headers, method=self.command)
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp_body = resp.read()
                hdrs = [(k, v) for k, v in resp.headers.items()
                        if k.lower() not in ("transfer-encoding",)]
                self.send_response(resp.status)
                for k, v in hdrs:
                    self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp_body)
                if use_cache and resp.status == 200:
                    _cache_set(self.path, resp.status, hdrs, resp_body)
        except urllib.error.HTTPError as e:
            resp_body = e.read()
            hdrs = [(k, v) for k, v in e.headers.items()
                    if k.lower() not in ("transfer-encoding",)]
            self.send_response(e.code)
            for k, v in hdrs:
                self.send_header(k, v)
            self.end_headers()
            self.wfile.write(resp_body)
        except Exception as exc:
            self.send_error(502, str(exc))

    # ── Static file server ────────────────────────────────────────────────────
    def _serve_static(self):
        rel = self.path.lstrip("/")
        if rel.startswith("static/"):
            rel = rel[len("static/"):]
        file_path = STATIC_DIR / rel
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, f"Not found: {self.path}")
            return
        mime = {
            ".html": "text/html", ".js": "application/javascript",
            ".css": "text/css", ".svg": "image/svg+xml",
            ".png": "image/png", ".ico": "image/x-icon",
            ".json": "application/json", ".woff2": "font/woff2",
        }.get(file_path.suffix.lower(), "application/octet-stream")
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    # ── Verb handlers ─────────────────────────────────────────────────────────
    def do_GET(self):
        if self._is_ws_upgrade():
            self._tunnel_websocket()
        elif self.path == "/":
            self.send_response(302)
            self.send_header("Location", "/static/index.html")
            self.end_headers()
        elif self.path.startswith("/api/") or self.path.startswith("/health"):
            cacheable = self.path.startswith("/api/v1/")
            self._proxy(use_cache=cacheable)
        else:
            self._serve_static()

    def do_POST(self):   self._proxy()
    def do_DELETE(self): self._proxy()
    def do_PUT(self):    self._proxy()
    def do_OPTIONS(self): self._proxy()


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


if __name__ == "__main__":
    os.chdir(Path(__file__).parent)
    server = ThreadedHTTPServer(("0.0.0.0", PORT), ProxyHandler)
    print(f"Proxy  : http://0.0.0.0:{PORT}")
    print(f"Static : {STATIC_DIR}")
    print(f"Backend: {BACKEND}  (WS tunnel + 2s GET cache enabled)")
    server.serve_forever()
