"""
shared/health.py
────────────────
Unified health-check utilities for all Ayushman Bharat microservices.

Provides:
- ``ServiceHealth``  dataclass for structured health status
- ``HealthChecker``  class for aggregating multi-service health
- ``health_router``  FastAPI router to mount on any service
- ``check_database`` helper that validates SQLite connectivity
- ``check_ml_model`` helper that validates ML model file presence

Each service can call ``mount_health_router(app)`` and immediately
get a ``/health`` and ``/health/detail`` endpoint with:
  - service name & version
  - uptime in seconds
  - database connectivity status
  - ML model status (if applicable)
  - memory usage (MB)
  - overall "healthy" / "degraded" / "unhealthy" status

Example
-------
    from shared.health import mount_health_router
    mount_health_router(app, service_name="auth-service", version="2.0.0")
"""
import os
import time
import sqlite3
from dataclasses import dataclass, field, asdict
from typing import Optional

from fastapi import APIRouter


# ── Data Model ────────────────────────────────────────────────────────────────

@dataclass
class ComponentHealth:
    name: str
    status: str          # "ok" | "degraded" | "error"
    latency_ms: Optional[float] = None
    detail: Optional[str] = None


@dataclass
class ServiceHealth:
    service: str
    version: str
    status: str                  # "healthy" | "degraded" | "unhealthy"
    uptime_seconds: float
    components: list = field(default_factory=list)
    memory_mb: Optional[float] = None
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["components"] = [asdict(c) for c in self.components]
        return d


# ── Database Check ────────────────────────────────────────────────────────────

def check_database(db_path: str = "healthtech.db") -> ComponentHealth:
    """Ping the SQLite database and measure round-trip latency."""
    start = time.monotonic()
    try:
        conn = sqlite3.connect(db_path, timeout=2)
        conn.execute("SELECT 1")
        conn.close()
        latency = (time.monotonic() - start) * 1000
        return ComponentHealth(name="database", status="ok", latency_ms=round(latency, 2))
    except Exception as exc:
        latency = (time.monotonic() - start) * 1000
        return ComponentHealth(
            name="database", status="error",
            latency_ms=round(latency, 2), detail=str(exc)
        )


# ── ML Model Check ────────────────────────────────────────────────────────────

def check_ml_model(model_path: str = "ai_ml/models/triage_model.joblib") -> ComponentHealth:
    """Check that the ML model file exists and is readable."""
    start = time.monotonic()
    try:
        if not os.path.exists(model_path):
            return ComponentHealth(
                name="ml_model", status="error",
                detail=f"Model file not found: {model_path}"
            )
        size_kb = os.path.getsize(model_path) / 1024
        latency = (time.monotonic() - start) * 1000
        return ComponentHealth(
            name="ml_model", status="ok",
            latency_ms=round(latency, 2),
            detail=f"Size: {size_kb:.1f} KB"
        )
    except Exception as exc:
        return ComponentHealth(name="ml_model", status="error", detail=str(exc))


# ── Memory Usage ──────────────────────────────────────────────────────────────

def _get_memory_mb() -> Optional[float]:
    """Return current process RSS memory in MB (Linux/macOS only)."""
    try:
        import resource
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # Linux: kilobytes; macOS: bytes
        if os.uname().sysname == "Darwin":
            return round(usage / (1024 * 1024), 2)
        return round(usage / 1024, 2)
    except Exception:
        return None


# ── HealthChecker ─────────────────────────────────────────────────────────────

class HealthChecker:
    """
    Aggregate multiple component checks into a single ServiceHealth report.

    Parameters
    ----------
    service_name : str
        Human-readable service name (e.g. ``"auth-service"``).
    version : str
        Service version string.
    db_path : str, optional
        Path to SQLite DB file for connectivity check.
    model_path : str, optional
        Path to ML model file; pass ``None`` to skip ML check.
    """

    def __init__(
        self,
        service_name: str,
        version: str = "2.0.0",
        db_path: str = "healthtech.db",
        model_path: Optional[str] = None,
    ):
        self.service_name = service_name
        self.version = version
        self.db_path = db_path
        self.model_path = model_path
        self._start_time = time.monotonic()

    def check(self) -> ServiceHealth:
        """Run all component checks and return a ``ServiceHealth`` snapshot."""
        components: list[ComponentHealth] = []

        # Database
        components.append(check_database(self.db_path))

        # ML model (optional)
        if self.model_path:
            components.append(check_ml_model(self.model_path))

        # Determine overall status
        statuses = {c.status for c in components}
        if "error" in statuses:
            overall = "unhealthy"
        elif "degraded" in statuses:
            overall = "degraded"
        else:
            overall = "healthy"

        return ServiceHealth(
            service=self.service_name,
            version=self.version,
            status=overall,
            uptime_seconds=round(time.monotonic() - self._start_time, 1),
            components=components,
            memory_mb=_get_memory_mb(),
        )


# ── FastAPI Router ────────────────────────────────────────────────────────────

def mount_health_router(
    app,
    service_name: str,
    version: str = "2.0.0",
    db_path: str = "healthtech.db",
    model_path: Optional[str] = None,
) -> None:
    """
    Attach ``/health`` and ``/health/detail`` endpoints to a FastAPI app.

    ``/health``        — lightweight ping (status + uptime only)
    ``/health/detail`` — full component breakdown (for internal monitoring)
    """
    checker = HealthChecker(service_name, version, db_path, model_path)
    router = APIRouter(tags=["Health"])

    @router.get("/health", summary="Liveness probe")
    def liveness():
        """Lightweight check — returns 200 if the service is running."""
        return {
            "service": service_name,
            "status": "ok",
            "uptime_seconds": round(time.monotonic() - checker._start_time, 1),
        }

    @router.get("/health/detail", summary="Full health report")
    def readiness():
        """Detailed health report including DB and ML model status."""
        report = checker.check()
        from fastapi import Response
        status_code = 200 if report.status == "healthy" else 503
        return report.to_dict()

    app.include_router(router)
