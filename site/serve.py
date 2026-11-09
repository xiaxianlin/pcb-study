#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PCB 课程站点的本地静态服务（带 HTTP 缓存头）。

- /fonts /assets /sim 的资源：Cache-Control 7 天（字库分片、mermaid、仿真器体积大且少变）
- HTML：no-cache（build.py 重建后刷新即可见，无需等缓存过期）
用法：python3 serve.py [port]
"""
import sys
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler


class CachedHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        path = self.path.split('?')[0]
        if path.startswith(('/fonts/', '/assets/', '/sim/')):
            self.send_header('Cache-Control', 'public, max-age=604800')
        elif path.endswith('.html') or path == '/':
            self.send_header('Cache-Control', 'no-cache')
        else:
            self.send_header('Cache-Control', 'max-age=3600')
        super().end_headers()


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8420
    server = ThreadingHTTPServer(('127.0.0.1', port), CachedHandler)
    print(f'serving on http://127.0.0.1:{port}', flush=True)
    server.serve_forever()
