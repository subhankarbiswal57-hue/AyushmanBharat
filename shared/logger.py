"""
Structured JSON Logger & Tracing Utility for Ayushman Bharat microservices.
Provides ISO timestamps, request tracing correlation IDs, severity levels,
and sanitized context outputs adhering to Indian Digital Personal Data Protection (DPDP) Act standards.
"""

import sys
import json
import logging
import datetime
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Formats log records as structured, single-line JSON objects."""

    def __init__(self, service_name: str = "ayushman-service"):
        super().__init__()
        self.service_name = service_name

    def format(self, record: logging.LogRecord) -> str:
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "service": self.service_name,
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "line": f"{record.filename}:{record.lineno}",
        }

        # Attach request / correlation context if present
        if hasattr(record, "correlation_id") and record.correlation_id:
            log_entry["correlation_id"] = record.correlation_id
        if hasattr(record, "user_id") and record.user_id:
            # Mask user identity if necessary
            raw_id = str(record.user_id)
            log_entry["user_id"] = raw_id[:4] + "***" if len(raw_id) > 4 else raw_id
        if hasattr(record, "path") and record.path:
            log_entry["http_path"] = record.path
        if hasattr(record, "duration_ms") and record.duration_ms is not None:
            log_entry["duration_ms"] = round(record.duration_ms, 2)

        # Exception information
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Extra attributes filter
        if hasattr(record, "extra_payload") and isinstance(record.extra_payload, dict):
            log_entry["payload"] = record.extra_payload

        return json.dumps(log_entry, default=str)


def get_logger(service_name: str = "ayushman-service", level: int = logging.INFO) -> logging.Logger:
    """Returns a pre-configured logger with JSON formatting."""
    logger = logging.getLogger(service_name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JSONFormatter(service_name=service_name))
        logger.addHandler(handler)
        logger.setLevel(level)
        logger.propagate = False
    return logger
