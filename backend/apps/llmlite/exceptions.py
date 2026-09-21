"""Custom exceptions for LLM/Ollama integration.

Hierarchy:
  LLMLiteError (base)
  ├── OllamaConnectionError   — server unreachable or refused
  ├── OllamaTimeoutError      — request exceeded timeout
  ├── ModelNotFoundError      — requested model not installed
  ├── GenerationError         — generate() call failed
  ├── StreamingError          — streaming response failed
  └── CacheError              — Redis cache read/write failure
"""

from __future__ import annotations


class LLMLiteError(Exception):
    """Base exception for all llmlite errors."""

    def __init__(self, message: str = "", *, details: dict | None = None):
        super().__init__(message)
        self.details = details or {}


class OllamaConnectionError(LLMLiteError):
    """Ollama server unreachable or refused connection."""

    def __init__(self, url: str = "", message: str = ""):
        msg = message or f"Cannot connect to Ollama at {url}"
        super().__init__(msg, details={"url": url})


class OllamaTimeoutError(LLMLiteError):
    """Ollama request exceeded timeout."""

    def __init__(self, timeout: float = 0, model: str = ""):
        super().__init__(
            f"Ollama request timed out after {timeout}s (model={model})",
            details={"timeout": timeout, "model": model},
        )


class ModelNotFoundError(LLMLiteError):
    """Requested model is not available on the Ollama server."""

    def __init__(self, model: str = "", available: list[str] | None = None):
        super().__init__(
            f"Model '{model}' not found"
            + (f". Available: {available}" if available else ""),
            details={"model": model, "available": available or []},
        )


class GenerationError(LLMLiteError):
    """LLM generate() call failed."""

    def __init__(self, model: str = "", reason: str = ""):
        super().__init__(
            f"Generation failed for model '{model}': {reason}"
            if reason
            else f"Generation failed for model '{model}'",
            details={"model": model, "reason": reason},
        )


class StreamingError(LLMLiteError):
    """LLM streaming response failed mid-stream."""

    def __init__(self, model: str = "", reason: str = ""):
        super().__init__(
            f"Streaming failed for model '{model}': {reason}"
            if reason
            else f"Streaming failed for model '{model}'",
            details={"model": model, "reason": reason},
        )


class CacheError(LLMLiteError):
    """Redis cache read/write failure (non-fatal — falls through to uncached)."""

    def __init__(self, operation: str = "", reason: str = ""):
        super().__init__(
            f"Cache {operation} failed: {reason}"
            if reason
            else f"Cache {operation} failed",
            details={"operation": operation, "reason": reason},
        )
