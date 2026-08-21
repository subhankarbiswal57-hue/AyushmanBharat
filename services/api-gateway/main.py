"""
API Gateway & Reverse Proxy
Runs on port 8000
Central entry point for frontend apps, routing requests to Auth (8001), Core (8002), AI/ML (8003), and Audit (8004).
"""
import sys
import os
import json
import urllib.request
import urllib.error
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Route targets
SERVICE_MAP = {
    "/api/v1/auth": "http://localhost:8001/auth",
    "/api/v1/clinical": "http://localhost:8002/clinical",
    "/api/v1/ai": "http://localhost:8003/ai",
    "/api/v1/audit": "http://localhost:8004/audit"
}

class GatewayHandler(BaseHTTPRequestHandler):
    def _send_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def _proxy_request(self, method: str):
        parsed = urlparse(self.path)
        path = parsed.path

        target_base = None
        remaining_path = ""
        for prefix, base_url in SERVICE_MAP.items():
            if path.startswith(prefix):
                target_base = base_url
                remaining_path = path[len(prefix):]
                break

        if not target_base:
            if path == "/health" or path == "/api/v1/health":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(json.dumps({
                    "gateway": "healthy",
                    "version": "1.0.0",
                    "routing": list(SERVICE_MAP.keys())
                }).encode())
                return

            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"No route defined for {path}"}).encode())
            return

        target_url = f"{target_base}{remaining_path}"
        if parsed.query:
            target_url += f"?{parsed.query}"

        content_length = int(self.headers.get("Content-Length", 0))
        req_body = self.rfile.read(content_length) if content_length > 0 else None

        req = urllib.request.Request(target_url, data=req_body, method=method)
        for h, v in self.headers.items():
            if h.lower() not in ["host", "content-length"]:
                req.add_header(h, v)

        try:
            with urllib.request.urlopen(req) as resp:
                resp_data = resp.read()
                self.send_response(resp.status)
                for h, v in resp.headers.items():
                    if h.lower() not in ["content-length", "access-control-allow-origin"]:
                        self.send_header(h, v)
                self._send_cors_headers()
                self.end_headers()
                self.wfile.write(resp_data)
        except urllib.error.HTTPError as e:
            err_data = e.read()
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(err_data or json.dumps({"error": str(e)}).encode())
        except Exception as e:
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self._send_cors_headers()
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Bad Gateway: {str(e)}", "target": target_url}).encode())

    def do_GET(self):
        self._proxy_request("GET")

    def do_POST(self):
        self._proxy_request("POST")

def run_server(port=8000):
    server = HTTPServer(("0.0.0.0", port), GatewayHandler)
    print(f"[API Gateway] Running on http://localhost:{port}")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
