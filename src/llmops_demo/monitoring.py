"""Local runtime monitoring — log events for demo observability."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from llmops_demo.config import RESULTS_DIR
from llmops_demo.foundry_client import InvocationResult

logger = logging.getLogger(__name__)

MONITOR_LOG = RESULTS_DIR / "monitoring_log.jsonl"


def record_event(
    result: InvocationResult,
    *,
    evaluation_total: int | None = None,
) -> dict[str, Any]:
    """Record a runtime event and append it to the monitoring log."""
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "agent_name": result.agent_name,
        "model": result.model_name,
        "prompt_variant": result.prompt_variant,
        "persona": result.persona,
        "status": result.status,
        "elapsed_seconds": result.elapsed_seconds,
        "evaluation_total": evaluation_total,
        "error": result.error or None,
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(MONITOR_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
    logger.debug("Monitoring event recorded: %s", event)
    return event


def load_events() -> list[dict[str, Any]]:
    """Load all monitoring events from the log file."""
    if not MONITOR_LOG.exists():
        return []
    events = []
    with open(MONITOR_LOG, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def clear_events() -> None:
    """Delete the monitoring log file."""
    if MONITOR_LOG.exists():
        MONITOR_LOG.unlink()
        logger.info("Monitoring log cleared.")


def get_monitoring_summary() -> dict[str, Any]:
    """Generate a summary of recorded monitoring events."""
    events = load_events()
    if not events:
        return {"total_events": 0, "events": []}
    successes = [e for e in events if e.get("status") == "success"]
    avg_latency = (
        round(sum(e["elapsed_seconds"] for e in successes) / len(successes), 3)
        if successes
        else 0.0
    )
    return {
        "total_events": len(events),
        "successes": len(successes),
        "errors": len(events) - len(successes),
        "avg_latency_seconds": avg_latency,
        "events": events,
    }
