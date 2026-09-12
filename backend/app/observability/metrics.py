import time
import statistics
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import SystemMetricModel
from app.observability.logging import logger

_start_time = time.time()
_recent_latencies: list[float] = []
_request_counter = 0


def get_uptime_seconds() -> float:
    return time.time() - _start_time


def record_request_latency(latency_ms: float):
    global _recent_latencies, _request_counter
    _request_counter += 1
    _recent_latencies.append(latency_ms)
    if len(_recent_latencies) > 200:
        _recent_latencies.pop(0)


def get_p95_latency_ms() -> float:
    if not _recent_latencies:
        return 0.0
    sorted_latencies = sorted(_recent_latencies)
    idx = int(len(sorted_latencies) * 0.95)
    return round(sorted_latencies[min(idx, len(sorted_latencies) - 1)], 2)


def get_total_requests_count() -> int:
    return _request_counter


async def record_metric(
    db: AsyncSession,
    request_id: str,
    endpoint: str,
    provider: str,
    model: str,
    retrieval_count: int = 0,
    retrieval_ms: float = 0.0,
    llm_ms: float = 0.0,
    total_ms: float = 0.0,
    status: str = "success",
    input_tokens: Optional[int] = None,
    output_tokens: Optional[int] = None,
    total_tokens: Optional[int] = None,
):
    try:
        record_request_latency(total_ms)
        metric = SystemMetricModel(
            request_id=request_id,
            endpoint=endpoint,
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            retrieval_count=retrieval_count,
            retrieval_ms=retrieval_ms,
            llm_ms=llm_ms,
            total_ms=total_ms,
            status=status,
        )
        db.add(metric)
        await db.commit()
    except Exception as e:
        logger.warning(f"Failed to record metric to database: {e}")
