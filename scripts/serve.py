"""Local preview that behaves like the deployed site (see DEPLOY.md): gzip for text, cache headers.

Usage: py -3 scripts/serve.py [--port 5408] [--dir site]

Plain `python -m http.server` sends no compression and no cache headers, so Lighthouse numbers
taken against it are worse than what visitors get from a configured nginx / CDN.
"""
import argparse
import gzip
import http.server
import io
import os

TEXT = {".html", ".css", ".js", ".svg", ".json", ".txt", ".xml", ".webmanifest"}


class Handler(http.server.SimpleHTTPRequestHandler):
    def cache_control(self, path):
        p = path.replace("\\", "/")
        if "/assets/fonts/" in p or "/assets/img/" in p:
            return "public, max-age=2592000"
        return "no-cache"

    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            index = os.path.join(path, "index.html")
            if not self.path.split("?", 1)[0].endswith("/") or not os.path.exists(index):
                return super().send_head()
            path = index
        ext = os.path.splitext(path)[1].lower()
        if not os.path.isfile(path):
            return super().send_head()
        with open(path, "rb") as f:
            body = f.read()
        gz = ext in TEXT and "gzip" in self.headers.get("Accept-Encoding", "")
        if gz:
            body = gzip.compress(body, 6)
        self.send_response(200)
        self.send_header("Content-Type", self.guess_type(path))
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", self.cache_control(path))
        if ext in TEXT:
            self.send_header("Vary", "Accept-Encoding")
        if gz:
            self.send_header("Content-Encoding", "gzip")
        self.end_headers()
        return io.BytesIO(body)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=5408)
    ap.add_argument("--dir", default=os.path.join(os.path.dirname(__file__), "..", "site"))
    a = ap.parse_args()
    handler = lambda *args, **kw: Handler(*args, directory=os.path.abspath(a.dir), **kw)
    with http.server.ThreadingHTTPServer(("127.0.0.1", a.port), handler) as srv:
        print(f"http://127.0.0.1:{a.port}/", flush=True)
        srv.serve_forever()


if __name__ == "__main__":
    main()
