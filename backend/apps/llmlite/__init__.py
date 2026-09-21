"""LLMLite — lightweight LLM integration utilities."""

from .exceptions import (
    LLMLiteError,
    OllamaConnectionError,
    OllamaTimeoutError,
    ModelNotFoundError,
    GenerationError,
    StreamingError,
    CacheError,
)

__all__ = [
    "LLMLiteError",
    "OllamaConnectionError",
    "OllamaTimeoutError",
    "ModelNotFoundError",
    "GenerationError",
    "StreamingError",
    "CacheError",
]
