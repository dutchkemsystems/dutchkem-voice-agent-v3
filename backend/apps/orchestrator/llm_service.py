from typing import Dict, Optional, AsyncGenerator
from .ollama_client import OllamaClient
from .prompt_templates import InterviewPromptTemplates
from apps.llmlite.exceptions import (
    LLMLiteError,
    OllamaConnectionError,
    ModelNotFoundError,
    GenerationError,
    CacheError,
)
import hashlib
import json


class LLMService:
    """Unified LLM service with fallback chain."""

    def __init__(self, redis_client=None):
        self.ollama = OllamaClient()
        self.templates = InterviewPromptTemplates()
        self.redis = redis_client
        self.preferred_model = "llama3.1:8b"
        self.fallback_model = "llama3.2:3b"

    async def generate_interview_answer(
        self,
        question: str,
        question_type: str,
        candidate_profile: Dict,
        conversation_history: list = None,
    ) -> str:
        """Generate an interview answer using the appropriate template."""

        # Build prompt from template
        template = self.templates.get_template(question_type)
        prompt = template.format(
            candidate_name=candidate_profile.get("name", "Candidate"),
            position=candidate_profile.get("position", "the position"),
            company=candidate_profile.get("company", "the company"),
            resume_summary=candidate_profile.get("resume_summary", ""),
            achievements=candidate_profile.get("achievements", ""),
            technical_skills=candidate_profile.get("technical_skills", ""),
            management_style=candidate_profile.get("management_style", ""),
            languages=candidate_profile.get("languages", "Python, JavaScript"),
            question=question,
            conversation_history=self._format_history(conversation_history or []),
        )

        # Check cache (non-fatal on failure)
        cache_key = self._cache_key(prompt)
        cached = await self._get_cached(cache_key)
        if cached:
            return cached

        # Generate with fallback
        system_prompt = (
            "You are a professional job candidate. Answer interview questions naturally "
            "and confidently. Be specific with examples. Sound authentic, not robotic."
        )

        try:
            answer = await self.ollama.generate(
                model=self.preferred_model,
                prompt=prompt,
                system=system_prompt,
                temperature=0.7,
            )
        except (OllamaConnectionError, ModelNotFoundError, GenerationError):
            # Fallback to smaller model
            answer = await self.ollama.generate(
                model=self.fallback_model,
                prompt=prompt,
                system=system_prompt,
                temperature=0.7,
            )

        # Cache response (non-fatal)
        await self._cache_response(cache_key, answer)

        return answer

    async def generate_stream(
        self,
        question: str,
        question_type: str,
        candidate_profile: Dict,
    ) -> AsyncGenerator[str, None]:
        """Stream interview answer generation."""
        template = self.templates.get_template(question_type)
        prompt = template.format(
            candidate_name=candidate_profile.get("name", "Candidate"),
            position=candidate_profile.get("position", "the position"),
            company=candidate_profile.get("company", "the company"),
            resume_summary=candidate_profile.get("resume_summary", ""),
            achievements=candidate_profile.get("achievements", ""),
            technical_skills=candidate_profile.get("technical_skills", ""),
            management_style=candidate_profile.get("management_style", ""),
            languages=candidate_profile.get("languages", "Python, JavaScript"),
            question=question,
            conversation_history="",
        )

        system_prompt = (
            "You are a professional job candidate. Answer interview questions naturally "
            "and confidently. Be specific with examples."
        )

        async for token in self.ollama.generate_stream(
            model=self.preferred_model,
            prompt=prompt,
            system=system_prompt,
        ):
            yield token

    def _format_history(self, history: list) -> str:
        if not history:
            return "No previous conversation."
        return "\n".join([f"Q: {h['question']}\nA: {h['answer']}" for h in history])

    def _cache_key(self, prompt: str) -> str:
        return f"llm:cache:{hashlib.md5(prompt.encode()).hexdigest()}"

    async def _get_cached(self, key: str) -> Optional[str]:
        if not self.redis:
            return None
        try:
            return await self.redis.get(key)
        except Exception as exc:
            raise CacheError(operation="get", reason=str(exc)) from exc

    async def _cache_response(self, key: str, response: str):
        if not self.redis:
            return
        try:
            await self.redis.setex(key, 3600, response)  # Cache 1 hour
        except Exception as exc:
            raise CacheError(operation="set", reason=str(exc)) from exc
