"""Logging configuration for the LLMOps demo."""

from __future__ import annotations

import logging
import sys

from llmops_demo.config import LOG_LEVEL


def setup_logging() -> None:
    """Configure root logger with a readable console format."""
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
        force=True,
    )
