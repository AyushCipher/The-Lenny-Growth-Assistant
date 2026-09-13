import time
import httpx
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, AsyncGenerator
from app.config import settings
from app.observability.logging import logger

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import openai
except ImportError:
    openai = None


@dataclass
class GenerationResult:
    text: str
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]
    latency_ms: float
    provider: str
    model: str


class BaseModelAdapter(ABC):
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str) -> GenerationResult:
        pass

    @abstractmethod
    async def check_health(self) -> tuple[bool, str]:
        pass


class OllamaAdapter(BaseModelAdapter):
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT_SECONDS

    async def check_health(self) -> tuple[bool, str]:
        try:
            async with httpx.AsyncClient(timeout=1.5) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                if res.status_code == 200:
                    models = [m.get("name") for m in res.json().get("models", [])]
                    if not models:
                        return False, "Ollama running, but no models downloaded (Run: ollama pull llama3)"
                    return True, f"Ollama ready ({len(models)} model{'s' if len(models)>1 else ''}: {', '.join(models[:3])})"
                return False, f"Ollama returned status {res.status_code}"
        except Exception as e:
            return False, f"Ollama offline ({self.base_url})"

    async def generate(self, prompt: str, system_prompt: str) -> GenerationResult:
        start_time = time.time()
        
        # 1. Resolve available model name if default is missing
        active_model = self.model
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                tags_res = await client.get(f"{self.base_url}/api/tags")
                if tags_res.status_code == 200:
                    models = [m.get("name") for m in tags_res.json().get("models", [])]
                    if models:
                        # Match exact or prefix (e.g. llama3 matches llama3:latest or llama3.2)
                        matched = next((m for m in models if self.model in m or m in self.model), None)
                        active_model = matched or models[0]
        except Exception:
            pass

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": active_model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.9,
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(url, json=payload)
                if res.status_code == 404:
                    raise RuntimeError(
                        f"Ollama model '{active_model}' was not found. Please run `ollama pull {self.model}` in your terminal to download it, or switch to Groq Cloud in the top-right model dropdown."
                    )
                res.raise_for_status()
                data = res.json()
                latency_ms = (time.time() - start_time) * 1000.0

                text = data.get("response", "")
                input_tokens = data.get("prompt_eval_count")
                output_tokens = data.get("eval_count")
                total_tokens = (input_tokens or 0) + (output_tokens or 0) if (input_tokens or output_tokens) else None

                return GenerationResult(
                    text=text,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    latency_ms=latency_ms,
                    provider="ollama",
                    model=active_model
                )
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000.0
            logger.error(f"Ollama generation failed: {e}")
            if "model" in str(e).lower() and "not found" in str(e).lower():
                raise RuntimeError(str(e))
            raise RuntimeError(
                f"Ollama generation failed: {str(e)}. "
                f"Ensure Ollama is running and model '{self.model}' is downloaded (`ollama pull {self.model}`). "
                "Alternatively, select Groq Cloud in the top-right model menu."
            )


class ClaudeAdapter(BaseModelAdapter):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self._api_key = api_key
        self.model = model or settings.ANTHROPIC_MODEL

    @property
    def api_key(self) -> Optional[str]:
        return self._api_key if self._api_key is not None else settings.ANTHROPIC_API_KEY

    async def check_health(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "ANTHROPIC_API_KEY is not configured in .env"
        if not anthropic:
            return False, "Anthropic SDK is not installed"
        return True, f"Anthropic Claude ready ({self.model})"

    async def generate(self, prompt: str, system_prompt: str) -> GenerationResult:
        if not self.api_key or not anthropic:
            raise ValueError("Anthropic API key is not configured. Add ANTHROPIC_API_KEY to your .env file.")

        start_time = time.time()
        client = anthropic.AsyncAnthropic(api_key=self.api_key)
        try:
            message = await client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}]
            )
            latency_ms = (time.time() - start_time) * 1000.0
            text = message.content[0].text if message.content else ""
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            total_tokens = input_tokens + output_tokens

            return GenerationResult(
                text=text,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                latency_ms=latency_ms,
                provider="anthropic",
                model=self.model
            )
        except Exception as e:
            logger.error(f"Claude API generation failed: {e}")
            raise RuntimeError(f"Anthropic Claude generation failed: {str(e)}")


class OpenAIAdapter(BaseModelAdapter):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self._api_key = api_key
        self.model = model or settings.OPENAI_MODEL

    @property
    def api_key(self) -> Optional[str]:
        return self._api_key if self._api_key is not None else settings.OPENAI_API_KEY

    async def check_health(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "OPENAI_API_KEY is not configured in .env"
        if not openai:
            return False, "OpenAI SDK is not installed"
        return True, f"OpenAI ready ({self.model})"

    async def generate(self, prompt: str, system_prompt: str) -> GenerationResult:
        if not self.api_key or not openai:
            raise ValueError("OpenAI API key is not configured. Add OPENAI_API_KEY to your .env file.")

        start_time = time.time()
        client = openai.AsyncOpenAI(api_key=self.api_key)
        try:
            response = await client.chat.completions.create(
                model=self.model,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            latency_ms = (time.time() - start_time) * 1000.0
            choice = response.choices[0]
            text = choice.message.content or ""
            usage = response.usage

            return GenerationResult(
                text=text,
                input_tokens=usage.prompt_tokens if usage else None,
                output_tokens=usage.completion_tokens if usage else None,
                total_tokens=usage.total_tokens if usage else None,
                latency_ms=latency_ms,
                provider="openai",
                model=self.model
            )
        except Exception as e:
            logger.error(f"OpenAI API generation failed: {e}")
            raise RuntimeError(f"OpenAI generation failed: {str(e)}")


class GroqAdapter(BaseModelAdapter):
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        self._api_key = api_key
        self.model = model or settings.GROQ_MODEL
        self.base_url = base_url or settings.GROQ_BASE_URL

    @property
    def api_key(self) -> Optional[str]:
        return self._api_key if self._api_key is not None else settings.GROQ_API_KEY

    async def check_health(self) -> tuple[bool, str]:
        if not self.api_key:
            return False, "GROQ_API_KEY is not configured in .env"
        if not openai:
            return False, "OpenAI client library is required for Groq"
        return True, f"Groq Cloud ready ({self.model})"

    async def generate(self, prompt: str, system_prompt: str) -> GenerationResult:
        if not self.api_key:
            raise ValueError("Groq API key is not configured. Add GROQ_API_KEY to your .env file.")

        start_time = time.time()
        client = openai.AsyncOpenAI(api_key=self.api_key, base_url=self.base_url)
        try:
            response = await client.chat.completions.create(
                model=self.model,
                temperature=0.3,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ]
            )
            latency_ms = (time.time() - start_time) * 1000.0
            choice = response.choices[0]
            text = choice.message.content or ""
            usage = response.usage

            return GenerationResult(
                text=text,
                input_tokens=usage.prompt_tokens if usage else None,
                output_tokens=usage.completion_tokens if usage else None,
                total_tokens=usage.total_tokens if usage else None,
                latency_ms=latency_ms,
                provider="groq",
                model=self.model
            )
        except Exception as e:
            logger.error(f"Groq API generation failed: {e}")
            raise RuntimeError(f"Groq Cloud generation failed: {str(e)}")


class ModelRouter:
    def __init__(self):
        self.active_provider: str = settings.DEFAULT_PROVIDER
        self.ollama_adapter = OllamaAdapter()
        self.claude_adapter = ClaudeAdapter()
        self.openai_adapter = OpenAIAdapter()
        self.groq_adapter = GroqAdapter()

    def get_adapter(self, provider_override: Optional[str] = None) -> BaseModelAdapter:
        provider = (provider_override or self.active_provider).lower()
        if provider in ["groq"]:
            return self.groq_adapter
        elif provider in ["anthropic", "claude"]:
            return self.claude_adapter
        elif provider in ["openai"]:
            return self.openai_adapter
        else:
            return self.ollama_adapter

    async def list_model_statuses(self) -> list[dict]:
        ollama_ok, ollama_msg = await self.ollama_adapter.check_health()
        groq_ok, groq_msg = await self.groq_adapter.check_health()
        claude_ok, claude_msg = await self.claude_adapter.check_health()
        openai_ok, openai_msg = await self.openai_adapter.check_health()

        return [
            {
                "provider": "ollama",
                "model_name": self.ollama_adapter.model,
                "display_name": f"Local Ollama ({self.ollama_adapter.model}) [Demo Mandatory]",
                "is_available": ollama_ok,
                "status_message": ollama_msg,
                "is_active": self.active_provider == "ollama"
            },
            {
                "provider": "groq",
                "model_name": self.groq_adapter.model,
                "display_name": f"Groq Cloud ({self.groq_adapter.model}) [Ultra Fast]",
                "is_available": groq_ok,
                "status_message": groq_msg,
                "is_active": self.active_provider == "groq"
            },
            {
                "provider": "anthropic",
                "model_name": self.claude_adapter.model,
                "display_name": f"Anthropic Claude ({self.claude_adapter.model})",
                "is_available": claude_ok,
                "status_message": claude_msg,
                "is_active": self.active_provider == "anthropic"
            },
            {
                "provider": "openai",
                "model_name": self.openai_adapter.model,
                "display_name": f"OpenAI ({self.openai_adapter.model})",
                "is_available": openai_ok,
                "status_message": openai_msg,
                "is_active": self.active_provider == "openai"
            }
        ]


model_router = ModelRouter()
