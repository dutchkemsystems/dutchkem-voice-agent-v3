import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from apps.orchestrator.llm_service import LLMService
from apps.orchestrator.ollama_client import OllamaClient
from apps.orchestrator.prompt_templates import InterviewPromptTemplates

class TestOllamaClient:
    @pytest.mark.asyncio
    async def test_generate_returns_text(self):
        client = OllamaClient()
        with patch.object(client.client, 'post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {"response": "Test answer"}
            mock_response.raise_for_status = MagicMock()
            mock_post.return_value = mock_response
            
            result = await client.generate(prompt="Test question")
            assert result == "Test answer"
    
    @pytest.mark.asyncio
    async def test_is_available_returns_bool(self):
        client = OllamaClient()
        with patch.object(client.client, 'get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response
            
            result = await client.is_available()
            assert result is True

class TestLLMService:
    @pytest.mark.asyncio
    async def test_generate_interview_answer(self):
        service = LLMService()
        with patch.object(service.ollama, 'generate', new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = "I have 5 years of experience..."
            
            answer = await service.generate_interview_answer(
                question="Tell me about yourself",
                question_type="hr",
                candidate_profile={"name": "John", "position": "Developer"},
            )
            
            assert "experience" in answer.lower()
            mock_gen.assert_called_once()
    
    def test_prompt_template_formatting(self):
        templates = InterviewPromptTemplates()
        prompt = templates.get_template("hr")
        assert "{question}" in prompt
        assert "{candidate_name}" in prompt

class TestPromptTemplates:
    def test_all_templates_exist(self):
        for qt in ["hr", "technical", "scenario", "coding"]:
            template = InterviewPromptTemplates.get_template(qt)
            assert template is not None
            assert len(template) > 100
