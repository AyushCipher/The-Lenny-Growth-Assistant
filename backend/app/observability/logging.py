import json
import logging
import sys
from datetime import datetime, timezone
from app.config import settings


class JSONFormatter(logging.Formatter):
    """
    Format logs as structured JSON for production observability.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include custom structured properties if present
        for key in [
            "request_id", "session_id", "provider", "model",
            "input_tokens", "output_tokens", "total_tokens",
            "retrieval_chunks", "retrieval_latency_ms", "llm_latency_ms",
            "total_latency_ms", "artifact_generated", "artifact_type", "error_type"
        ]:
            if hasattr(record, key):
                log_data[key] = getattr(record, key)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


def setup_structured_logging():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    root_logger.handlers = [handler]

    # Adjust third-party loggers
    logging.getLogger("uvicorn.access").handlers = [handler]
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return root_logger


logger = logging.getLogger("lenny_growth")
