"""Model Proxy Layer - Core service for routing AI requests through multiple providers."""
from typing import Optional, Dict, Any, List, AsyncGenerator
from abc import ABC, abstractmethod
import httpx
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import structlog
from datetime import datetime

from app.core.config import get_settings
from app.core.security import key_encryption_service
from app.models.schemas import ProviderType, AgentType, RequestStatus

logger = structlog.get_logger()
settings = get_settings()


class ProviderAdapter(ABC):
    """Abstract base class for provider API adapters."""
    
    @property
    @abstractmethod
    def provider_type(self) -> ProviderType:
        """Return the provider type this adapter handles."""
        pass
    
    @abstractmethod
    async def translate_request(self, request_body: Dict[str, Any], model: str) -> Dict[str, Any]:
        """Translate standard request format to provider-specific format."""
        pass
    
    @abstractmethod
    async def translate_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Translate provider-specific response to standard format."""
        pass
    
    @abstractmethod
    def get_base_url(self) -> str:
        """Return the base URL for the provider API."""
        pass
    
    @abstractmethod
    def get_auth_headers(self, api_key: str) -> Dict[str, str]:
        """Return authentication headers for the provider."""
        pass


class GroqAdapter(ProviderAdapter):
    """Adapter for Groq API."""
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GROQ
    
    def get_base_url(self) -> str:
        return "https://api.groq.com/openai/v1"
    
    def get_auth_headers(self, api_key: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {api_key}"}
    
    async def translate_request(self, request_body: Dict[str, Any], model: str) -> Dict[str, Any]:
        # Groq uses OpenAI-compatible API
        return {**request_body, "model": model}
    
    async def translate_response(self, response: httpx.Response) -> Dict[str, Any]:
        data = response.json()
        return {
            "id": data.get("id"),
            "choices": data.get("choices", []),
            "usage": data.get("usage"),
            "model": data.get("model"),
            "raw_response": data,
        }


class OpenRouterAdapter(ProviderAdapter):
    """Adapter for OpenRouter API."""
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENROUTER
    
    def get_base_url(self) -> str:
        return "https://openrouter.ai/api/v1"
    
    def get_auth_headers(self, api_key: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {api_key}"}
    
    async def translate_request(self, request_body: Dict[str, Any], model: str) -> Dict[str, Any]:
        return {**request_body, "model": model}
    
    async def translate_response(self, response: httpx.Response) -> Dict[str, Any]:
        data = response.json()
        return {
            "id": data.get("id"),
            "choices": data.get("choices", []),
            "usage": data.get("usage"),
            "model": data.get("model"),
            "raw_response": data,
        }


class GoogleAIAdapter(ProviderAdapter):
    """Adapter for Google AI Studio (Gemini) API."""
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.GOOGLE_AI
    
    def get_base_url(self) -> str:
        return "https://generativelanguage.googleapis.com/v1beta"
    
    def get_auth_headers(self, api_key: str) -> Dict[str, str]:
        return {}  # Google uses query param for API key
    
    def get_api_params(self, api_key: str) -> Dict[str, str]:
        return {"key": api_key}
    
    async def translate_request(self, request_body: Dict[str, Any], model: str) -> Dict[str, Any]:
        # Convert OpenAI-style messages to Gemini format
        messages = request_body.get("messages", [])
        contents = []
        for msg in messages:
            role = "user" if msg["role"] in ["user", "system"] else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })
        
        return {
            "contents": contents,
            "generationConfig": {
                "temperature": request_body.get("temperature", 0.7),
                "maxOutputTokens": request_body.get("max_tokens", 2048),
            }
        }
    
    async def translate_response(self, response: httpx.Response) -> Dict[str, Any]:
        data = response.json()
        candidates = data.get("candidates", [])
        choices = []
        for candidate in candidates:
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            text = parts[0].get("text", "") if parts else ""
            choices.append({
                "message": {"role": "assistant", "content": text},
                "finish_reason": candidate.get("finishReason"),
            })
        
        return {
            "id": data.get("id", ""),
            "choices": choices,
            "usage": None,  # Google doesn't always provide usage
            "model": data.get("modelVersion"),
            "raw_response": data,
        }


class TogetherAIAdapter(ProviderAdapter):
    """Adapter for Together AI API."""
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.TOGETHER_AI
    
    def get_base_url(self) -> str:
        return "https://api.together.xyz/v1"
    
    def get_auth_headers(self, api_key: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {api_key}"}
    
    async def translate_request(self, request_body: Dict[str, Any], model: str) -> Dict[str, Any]:
        return {**request_body, "model": model}
    
    async def translate_response(self, response: httpx.Response) -> Dict[str, Any]:
        data = response.json()
        return {
            "id": data.get("id"),
            "choices": data.get("choices", []),
            "usage": data.get("usage"),
            "model": data.get("model"),
            "raw_response": data,
        }


class CerebrasAdapter(ProviderAdapter):
    """Adapter for Cerebras API."""
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.CEREBRAS
    
    def get_base_url(self) -> str:
        return "https://api.cerebras.ai/v1"
    
    def get_auth_headers(self, api_key: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {api_key}"}
    
    async def translate_request(self, request_body: Dict[str, Any], model: str) -> Dict[str, Any]:
        return {**request_body, "model": model}
    
    async def translate_response(self, response: httpx.Response) -> Dict[str, Any]:
        data = response.json()
        return {
            "id": data.get("id"),
            "choices": data.get("choices", []),
            "usage": data.get("usage"),
            "model": data.get("model"),
            "raw_response": data,
        }


class MistralAdapter(ProviderAdapter):
    """Adapter for Mistral AI API."""
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.MISTRAL
    
    def get_base_url(self) -> str:
        return "https://api.mistral.ai/v1"
    
    def get_auth_headers(self, api_key: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {api_key}"}
    
    async def translate_request(self, request_body: Dict[str, Any], model: str) -> Dict[str, Any]:
        return {**request_body, "model": model}
    
    async def translate_response(self, response: httpx.Response) -> Dict[str, Any]:
        data = response.json()
        return {
            "id": data.get("id"),
            "choices": data.get("choices", []),
            "usage": data.get("usage"),
            "model": data.get("model"),
            "raw_response": data,
        }


class AnthropicAdapter(ProviderAdapter):
    """Adapter for Anthropic API (Claude)."""
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.ANTHROPIC
    
    def get_base_url(self) -> str:
        return "https://api.anthropic.com/v1"
    
    def get_auth_headers(self, api_key: str) -> Dict[str, str]:
        return {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }
    
    async def translate_request(self, request_body: Dict[str, Any], model: str) -> Dict[str, Any]:
        # Convert from OpenAI format to Anthropic format
        messages = request_body.get("messages", [])
        system_message = ""
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)
        
        result = {
            "model": model,
            "messages": user_messages,
            "max_tokens": request_body.get("max_tokens", 2048),
        }
        
        if system_message:
            result["system"] = system_message
        
        return result
    
    async def translate_response(self, response: httpx.Response) -> Dict[str, Any]:
        data = response.json()
        content_list = data.get("content", [])
        text_content = ""
        for content in content_list:
            if content.get("type") == "text":
                text_content += content.get("text", "")
        
        choices = [{
            "message": {"role": "assistant", "content": text_content},
            "finish_reason": data.get("stop_reason"),
        }]
        
        return {
            "id": data.get("id"),
            "choices": choices,
            "usage": data.get("usage"),
            "model": data.get("model"),
            "raw_response": data,
        }


class OpenAIAdapter(ProviderAdapter):
    """Adapter for OpenAI API."""
    
    @property
    def provider_type(self) -> ProviderType:
        return ProviderType.OPENAI
    
    def get_base_url(self) -> str:
        return "https://api.openai.com/v1"
    
    def get_auth_headers(self, api_key: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {api_key}"}
    
    async def translate_request(self, request_body: Dict[str, Any], model: str) -> Dict[str, Any]:
        return {**request_body, "model": model}
    
    async def translate_response(self, response: httpx.Response) -> Dict[str, Any]:
        data = response.json()
        return {
            "id": data.get("id"),
            "choices": data.get("choices", []),
            "usage": data.get("usage"),
            "model": data.get("model"),
            "raw_response": data,
        }


class ModelProxyService:
    """
    Central proxy service for routing AI requests through multiple providers.
    Handles load balancing, fallback, and key rotation.
    """
    
    def __init__(self):
        self.adapters: Dict[ProviderType, ProviderAdapter] = {
            ProviderType.GROQ: GroqAdapter(),
            ProviderType.OPENROUTER: OpenRouterAdapter(),
            ProviderType.GOOGLE_AI: GoogleAIAdapter(),
            ProviderType.TOGETHER_AI: TogetherAIAdapter(),
            ProviderType.CEREBRAS: CerebrasAdapter(),
            ProviderType.MISTRAL: MistralAdapter(),
            ProviderType.ANTHROPIC: AnthropicAdapter(),
            ProviderType.OPENAI: OpenAIAdapter(),
        }
        self._http_client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(settings.DEFAULT_REQUEST_TIMEOUT),
                limits=httpx.Limits(max_keepalive_connections=50),
            )
        return self._http_client
    
    async def close(self):
        """Close the HTTP client."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
    
    @retry(
        stop=stop_after_attempt(settings.MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=settings.RETRY_BACKOFF_SECONDS),
        retry=retry_if_exception_type((httpx.HTTPError, httpx.NetworkError, asyncio.TimeoutError)),
    )
    async def send_request(
        self,
        provider: ProviderType,
        api_key: str,
        request_body: Dict[str, Any],
        model: str,
    ) -> Dict[str, Any]:
        """Send a request to a specific provider with automatic retry."""
        adapter = self.adapters.get(provider)
        if not adapter:
            raise ValueError(f"No adapter found for provider: {provider}")
        
        client = await self._get_client()
        translated_body = await adapter.translate_request(request_body, model)
        base_url = adapter.get_base_url()
        headers = adapter.get_auth_headers(api_key)
        
        # Special handling for Google AI (uses query param)
        if provider == ProviderType.GOOGLE_AI:
            params = adapter.get_api_params(api_key)
            endpoint = f"{base_url}/models/{model}:generateContent"
            response = await client.post(endpoint, json=translated_body, params=params)
        elif provider == ProviderType.ANTHROPIC:
            endpoint = f"{base_url}/messages"
            response = await client.post(endpoint, json=translated_body, headers=headers)
        else:
            endpoint = f"{base_url}/chat/completions"
            response = await client.post(endpoint, json=translated_body, headers=headers)
        
        response.raise_for_status()
        return await adapter.translate_response(response)
    
    async def route_with_fallback(
        self,
        available_keys: List[Dict[str, Any]],
        request_body: Dict[str, Any],
        preferred_model: str,
        agent_type: Optional[AgentType] = None,
    ) -> Dict[str, Any]:
        """
        Route request through available providers with automatic fallback.
        
        Args:
            available_keys: List of dicts with 'provider', 'encrypted_key', 'model' keys
            request_body: Standard chat completion request body
            preferred_model: Preferred model name
            agent_type: Optional agent type for routing rules
        
        Returns:
            Standardized response dict
        """
        errors = []
        
        for key_info in available_keys:
            provider = ProviderType(key_info["provider"])
            encrypted_key = key_info["encrypted_key"]
            model = key_info.get("model", preferred_model)
            
            try:
                api_key = key_encryption_service.decrypt(encrypted_key)
                
                logger.info(
                    "proxy_request",
                    provider=provider.value,
                    model=model,
                    attempt=len(errors) + 1,
                )
                
                start_time = datetime.utcnow()
                response = await self.send_request(provider, api_key, request_body, model)
                latency_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
                
                logger.info(
                    "proxy_success",
                    provider=provider.value,
                    model=model,
                    latency_ms=latency_ms,
                )
                
                response["used_provider"] = provider.value
                response["latency_ms"] = latency_ms
                response["retries"] = len(errors)
                
                return response
                
            except Exception as e:
                error_msg = f"{provider.value}: {str(e)}"
                errors.append(error_msg)
                logger.warning("proxy_fallback", provider=provider.value, error=str(e))
        
        # All providers failed
        logger.error("proxy_all_failed", errors=errors)
        raise Exception(f"All providers failed. Errors: {'; '.join(errors)}")
    
    async def stream_request(
        self,
        provider: ProviderType,
        api_key: str,
        request_body: Dict[str, Any],
        model: str,
    ) -> AsyncGenerator[str, None]:
        """Stream a request response."""
        adapter = self.adapters.get(provider)
        if not adapter:
            raise ValueError(f"No adapter found for provider: {provider}")
        
        client = await self._get_client()
        translated_body = await adapter.translate_request(request_body, model)
        translated_body["stream"] = True
        
        base_url = adapter.get_base_url()
        headers = adapter.get_auth_headers(api_key)
        
        if provider == ProviderType.ANTHROPIC:
            headers["accept"] = "text/event-stream"
            endpoint = f"{base_url}/messages"
        else:
            endpoint = f"{base_url}/chat/completions"
        
        async with client.stream("POST", endpoint, json=translated_body, headers=headers) as response:
            response.raise_for_status()
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    yield line[6:]  # Remove "data: " prefix


# Singleton instance
proxy_service = ModelProxyService()
