#!/usr/bin/env python3
"""Локальный сервер макетов: python3 serve.py  ->  http://localhost:8000/Today.dc.html
Подменяет адреса /_blob/<id> на PNG из silhouettes/ (по blob-map.json)."""
import http.server, json, os, re
root = os.path.dirname(os.path.abspath(__file__))
bm = json.load(open(os.path.join(root, "blob-map.json")))
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s, *a, **k): super().__init__(*a, directory=root, **k)
    def translate_path(s, p):
        m = re.match(r"/_blob/([0-9a-f]{32})", p)
        if m and m.group(1) in bm: return os.path.join(root, bm[m.group(1)])
        return super().translate_path(p)
http.server.ThreadingHTTPServer(("", 8000), H).serve_forever()
