"""
Master Orchestrator for Ayushman Bharat Healthtech Platform
Runs all FastAPI microservices (Ports 8000-8004) and Web App Static File Server (Port 3000)
"""
import sys
import os
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler
import uvicorn

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

from shared.config import (
    GATEWAY_PORT, AUTH_PORT, CORE_PORT, AIML_PORT, AUDIT_PORT, PORTAL_PORT
)
from shared.db import init_database

init_database()

def run_uvicorn_service(app_path: str, port: int, name: str):
    print(f"[{name}] Starting FastAPI on http://localhost:{port}")
    uvicorn.run(app_path, host="0.0.0.0", port=port, log_level="warning")

def make_static_handler(root_dir: str):
    class StaticHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=root_dir, **kwargs)
        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            super().end_headers()
        def log_message(self, format, *args):
            pass
    return StaticHandler

def run_static_server(directory: str, port: int, name: str):
    handler = make_static_handler(directory)
    server = HTTPServer(("0.0.0.0", port), handler)
    print(f"[{name}] Serving at http://localhost:{port}")
    server.serve_forever()

def start_thread(target, args=()):
    t = threading.Thread(target=target, args=args, daemon=True)
    t.start()
    return t

def start_all_services():
    print("=" * 80)
    print("[INIT] Starting Ayushman Bharat Modernized Healthtech Microservices...")
    print("=" * 80)

    start_thread(run_uvicorn_service, ("services.auth_service.main:app", AUTH_PORT, "Auth Service"))
    start_thread(run_uvicorn_service, ("services.core_backend.main:app", CORE_PORT, "Core Clinical Backend"))
    start_thread(run_uvicorn_service, ("ai_ml.monitoring.app:app", AIML_PORT, "AI/ML Fairness Service"))
    start_thread(run_uvicorn_service, ("services.audit_logging.main:app", AUDIT_PORT, "Audit Logging Service"))
    time.sleep(0.5)

    start_thread(run_uvicorn_service, ("services.api_gateway.main:app", GATEWAY_PORT, "API Gateway"))

    start_thread(
        run_static_server,
        (os.path.join(BASE_DIR, "apps", "unified-portal"), PORTAL_PORT, "Unified Portal")
    )

    print("\n[OK] All Platform Services Online & Modernized:")
    print(f"  * Central API Gateway: http://localhost:{GATEWAY_PORT} (Docs: /docs)")
    print(f"  * Auth Service:        http://localhost:{AUTH_PORT} (Docs: /docs)")
    print(f"  * Core Clinical Backend: http://localhost:{CORE_PORT} (Docs: /docs)")
    print(f"  * AI/ML Fairness Layer: http://localhost:{AIML_PORT} (Docs: /docs)")
    print(f"  * Tamper-Evident Audit: http://localhost:{AUDIT_PORT} (Docs: /docs)")
    print(f"  * Unified Portal:      http://localhost:{PORTAL_PORT}")
    print("=" * 80)

if __name__ == "__main__":
    start_all_services()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping platform services.")
