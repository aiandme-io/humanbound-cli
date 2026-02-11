"""Humanbound CLI - command line interface for AI agent security testing."""

from importlib.metadata import version as _v

try:
    __version__ = _v("humanbound-cli")
except Exception:
    __version__ = "dev"
