"""
Master Orchestrator for Ayushman Bharat Healthtech Platform
Runs all microservices (Ports 8000-8004) and Web App Static File Servers (Ports 3000-3002)
"""
import sys
import os
import threading
import time
import importlib.util
from http.server import HTTPServer, SimpleHTTPRequestHandler

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, BASE_DIR)

def load_module_from_path(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module

auth_svc = load_module_from_path("auth_svc", os.path.join(BASE_DIR, "services", "auth-service", "main.py"))
core_svc = load_module_from_path("core_svc", os.path.join(BASE_DIR, "services", "core-backend", "main.py"))
audit_svc = load_module_from_path("audit_svc", os.path.join(BASE_DIR, "services", "audit-logging", "main.py"))
gateway_svc = load_module_from_path("gateway_svc", os.path.join(BASE_DIR, "services", "api-gateway", "main.py"))
aiml_svc = load_module_from_path("aiml_svc", os.path.join(BASE_DIR, "ai-ml", "monitoring", "app.py"))

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
    print("=" * 75)
    print("[INIT] Starting Ayushman Bharat Healthtech Platform Services & Apps...")
    print("=" * 75)

    start_thread(auth_svc.run_server, (8001,))
    start_thread(core_svc.run_server, (8002,))
    start_thread(aiml_svc.run_server, (8003,))
    start_thread(audit_svc.run_server, (8004,))
    time.sleep(0.3)

    start_thread(gateway_svc.run_server, (8000,))

    start_thread(
        run_static_server, 
        (os.path.join(BASE_DIR, "apps", "patient-frontend"), 3000, "Patient Frontend")
    )
    start_thread(
        run_static_server, 
        (os.path.join(BASE_DIR, "apps", "clinician-frontend"), 3001, "Clinician Frontend")
    )
    start_thread(
        run_static_server, 
        (os.path.join(BASE_DIR, "apps", "admin-dashboard"), 3002, "Admin Governance Console")
    )

    print("\n[OK] All Platform Services Online:")
    print("  * API Gateway:                http://localhost:8000")
    print("  * Patient App (Multilingual): http://localhost:3000")
    print("  * Clinician Triage Portal:    http://localhost:3001")
    print("  * Governance & AI Console:    http://localhost:3002")
    print("=" * 75)

if __name__ == "__main__":
    start_all_services()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping platform services.")
