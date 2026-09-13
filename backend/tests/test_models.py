import pytest
from unittest.mock import AsyncMock, patch
from app.agent.models import model_router, OllamaAdapter, ClaudeAdapter, OpenAIAdapter, GroqAdapter, GenerationResult


@pytest.mark.asyncio
async def test_provider_adapter_switching():
    # Test router defaults and switching
    adapter_ollama = model_router.get_adapter("ollama")
    assert isinstance(adapter_ollama, OllamaAdapter)

    adapter_groq = model_router.get_adapter("groq")
    assert isinstance(adapter_groq, GroqAdapter)

    adapter_claude = model_router.get_adapter("anthropic")
    assert isinstance(adapter_claude, ClaudeAdapter)

    adapter_openai = model_router.get_adapter("openai")
    assert isinstance(adapter_openai, OpenAIAdapter)


@pytest.mark.asyncio
async def test_generation_result_token_normalization():
    # Mock adapter generation with token usage
    mock_result = GenerationResult(
        text="Sample grounded answer with citation [[Shreyas Doshi]](src_shreyas_doshi_01)",
        input_tokens=150,
        output_tokens=65,
        total_tokens=215,
        latency_ms=120.5,
        provider="ollama",
        model="llama3"
    )

    assert mock_result.input_tokens == 150
    assert mock_result.output_tokens == 65
    assert mock_result.total_tokens == 215
    assert mock_result.provider == "ollama"


@pytest.mark.asyncio
async def test_missing_api_key_diagnostics():
    # Claude with no key should report clean error rather than crash
    claude_no_key = ClaudeAdapter(api_key=None)
    is_ok, msg = await claude_no_key.check_health()
    assert is_ok is False
    assert "ANTHROPIC_API_KEY" in msg

    # Calling generate without key should raise ValueError with actionable message
    with pytest.raises(ValueError) as exc:
        await claude_no_key.generate("Hello", "System")
    assert "ANTHROPIC_API_KEY" in str(exc.value)

    # Groq with no key should report clean error
    groq_no_key = GroqAdapter(api_key=None)
    g_ok, g_msg = await groq_no_key.check_health()
    assert g_ok is False
    assert "GROQ_API_KEY" in g_msg

    with pytest.raises(ValueError) as exc_g:
        await groq_no_key.generate("Hello", "System")
    assert "GROQ_API_KEY" in str(exc_g.value)
