"""Direct LLM Provider Integration for Noode.

Supports: OpenAI, Anthropic, Google (Gemini), OpenRouter
No LiteLLM wrapper - direct API calls.
"""

import os
import json
import structlog
from typing import Optional, List, Dict, Any, Generator
from dataclasses import dataclass
from pathlib import Path
import yaml

# Provider SDKs
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import google.generativeai as genai
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False

import requests

logger = structlog.get_logger()


@dataclass
class LLMMessage:
    """A message in the conversation."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """Response from an LLM provider."""
    content: str
    model: str
    provider: str
    usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None


class ProviderConfig:
    """Manages LLM provider configurations and API keys."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "noode"
        self.config_file = self.config_dir / "providers.yaml"
        self._config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load provider configuration from YAML."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.error("Failed to load provider config", error=str(e))
        
        # Default config
        return {
            "active_provider": "openai",
            "providers": {
                "openai": {
                    "enabled": False,
                    "model": "gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 4000,
                },
                "anthropic": {
                    "enabled": False,
                    "model": "claude-3-opus-20240229",
                    "temperature": 0.7,
                    "max_tokens": 4000,
                },
                "google": {
                    "enabled": False,
                    "model": "gemini-pro",
                    "temperature": 0.7,
                    "max_tokens": 4000,
                },
                "openrouter": {
                    "enabled": False,
                    "model": "openai/gpt-4",
                    "temperature": 0.7,
                    "max_tokens": 4000,
                },
            }
        }
    
    def save_config(self):
        """Save configuration to YAML."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)
        except Exception as e:
            logger.error("Failed to save provider config", error=str(e))
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider."""
        # Check environment variable first
        env_var = f"NOODE_{provider.upper()}_API_KEY"
        if os.environ.get(env_var):
            return os.environ[env_var]
        
        # Check key file
        key_file = self.config_dir / f"{provider}.key"
        if key_file.exists():
            try:
                with open(key_file, 'r') as f:
                    return f.read().strip()
            except Exception as e:
                logger.error(f"Failed to read {provider} API key", error=str(e))
        
        return None
    
    def set_api_key(self, provider: str, api_key: str):
        """Save API key for a provider (encrypted storage)."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        key_file = self.config_dir / f"{provider}.key"
        try:
            with open(key_file, 'w') as f:
                f.write(api_key)
            # Secure the file (Unix only)
            os.chmod(key_file, 0o600)
            logger.info(f"API key saved for {provider}")
        except Exception as e:
            logger.error(f"Failed to save {provider} API key", error=str(e))
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get configuration for a specific provider."""
        return self._config.get("providers", {}).get(provider, {})
    
    def set_active_provider(self, provider: str):
        """Set the active provider."""
        self._config["active_provider"] = provider
        self.save_config()
    
    def get_active_provider(self) -> str:
        """Get the currently active provider."""
        return self._config.get("active_provider", "openai")


class LLMProvider:
    """Base class for LLM providers."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
    
    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        """Send chat completion request."""
        raise NotImplementedError
    
    def is_available(self) -> bool:
        """Check if provider is available (API key set)."""
        raise NotImplementedError


class OpenAIProvider(LLMProvider):
    """OpenAI API integration."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.api_key = config.get_api_key("openai")
        if self.api_key and OPENAI_AVAILABLE:
            openai.api_key = self.api_key
    
    def is_available(self) -> bool:
        return OPENAI_AVAILABLE and self.api_key is not None
    
    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        if not self.is_available():
            return LLMResponse(
                content="",
                model="",
                provider="openai",
                error="OpenAI not available. Check API key."
            )
        
        try:
            provider_config = self.config.get_provider_config("openai")
            model = kwargs.get("model", provider_config.get("model", "gpt-4"))
            temperature = kwargs.get("temperature", provider_config.get("temperature", 0.7))
            max_tokens = kwargs.get("max_tokens", provider_config.get("max_tokens", 4000))
            
            # Convert messages to OpenAI format
            openai_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            response = openai.chat.completions.create(
                model=model,
                messages=openai_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=response.model,
                provider="openai",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }
            )
            
        except openai.AuthenticationError:
            logger.error("OpenAI authentication failed")
            return LLMResponse(
                content="",
                model="",
                provider="openai",
                error="Invalid API key"
            )
        except openai.RateLimitError:
            logger.error("OpenAI rate limit exceeded")
            return LLMResponse(
                content="",
                model="",
                provider="openai",
                error="Rate limit exceeded. Please try again later."
            )
        except Exception as e:
            logger.error("OpenAI API error", error=str(e))
            return LLMResponse(
                content="",
                model="",
                provider="openai",
                error=f"API error: {str(e)}"
            )


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API integration."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.api_key = config.get_api_key("anthropic")
        self.client = None
        if self.api_key and ANTHROPIC_AVAILABLE:
            self.client = anthropic.Anthropic(api_key=self.api_key)
    
    def is_available(self) -> bool:
        return ANTHROPIC_AVAILABLE and self.api_key is not None and self.client is not None
    
    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        if not self.is_available():
            return LLMResponse(
                content="",
                model="",
                provider="anthropic",
                error="Anthropic not available. Check API key."
            )
        
        try:
            provider_config = self.config.get_provider_config("anthropic")
            model = kwargs.get("model", provider_config.get("model", "claude-3-opus-20240229"))
            max_tokens = kwargs.get("max_tokens", provider_config.get("max_tokens", 4000))
            
            # Convert messages to Anthropic format
            system_msg = ""
            user_messages = []
            
            for msg in messages:
                if msg.role == "system":
                    system_msg = msg.content
                else:
                    user_messages.append({
                        "role": msg.role,
                        "content": msg.content
                    })
            
            response = self.client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system_msg if system_msg else None,
                messages=user_messages,
            )
            
            return LLMResponse(
                content=response.content[0].text,
                model=response.model,
                provider="anthropic",
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                }
            )
            
        except anthropic.AuthenticationError:
            logger.error("Anthropic authentication failed")
            return LLMResponse(
                content="",
                model="",
                provider="anthropic",
                error="Invalid API key"
            )
        except Exception as e:
            logger.error("Anthropic API error", error=str(e))
            return LLMResponse(
                content="",
                model="",
                provider="anthropic",
                error=f"API error: {str(e)}"
            )


class GoogleProvider(LLMProvider):
    """Google Gemini API integration."""
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.api_key = config.get_api_key("google")
        if self.api_key and GOOGLE_AVAILABLE:
            genai.configure(api_key=self.api_key)
    
    def is_available(self) -> bool:
        return GOOGLE_AVAILABLE and self.api_key is not None
    
    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        if not self.is_available():
            return LLMResponse(
                content="",
                model="",
                provider="google",
                error="Google Gemini not available. Check API key."
            )
        
        try:
            provider_config = self.config.get_provider_config("google")
            model_name = kwargs.get("model", provider_config.get("model", "gemini-pro"))
            
            model = genai.GenerativeModel(model_name)
            
            # Build conversation history
            chat = model.start_chat(history=[])
            
            # Send last user message
            last_message = messages[-1] if messages else None
            if last_message and last_message.role == "user":
                response = chat.send_message(last_message.content)
                
                return LLMResponse(
                    content=response.text,
                    model=model_name,
                    provider="google",
                )
            else:
                return LLMResponse(
                    content="",
                    model="",
                    provider="google",
                    error="No user message found"
                )
                
        except Exception as e:
            logger.error("Google API error", error=str(e))
            return LLMResponse(
                content="",
                model="",
                provider="google",
                error=f"API error: {str(e)}"
            )


class OpenRouterProvider(LLMProvider):
    """OpenRouter API integration (multi-provider)."""
    
    API_BASE = "https://openrouter.ai/api/v1"
    
    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self.api_key = config.get_api_key("openrouter")
    
    def is_available(self) -> bool:
        return self.api_key is not None
    
    def chat(self, messages: List[LLMMessage], **kwargs) -> LLMResponse:
        if not self.is_available():
            return LLMResponse(
                content="",
                model="",
                provider="openrouter",
                error="OpenRouter not available. Check API key."
            )
        
        try:
            provider_config = self.config.get_provider_config("openrouter")
            model = kwargs.get("model", provider_config.get("model", "openai/gpt-4"))
            temperature = kwargs.get("temperature", provider_config.get("temperature", 0.7))
            max_tokens = kwargs.get("max_tokens", provider_config.get("max_tokens", 4000))
            
            # Convert messages
            openrouter_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
            ]
            
            response = requests.post(
                f"{self.API_BASE}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://noode.ai",  # Required by OpenRouter
                    "X-Title": "Noode AI Platform",
                },
                json={
                    "model": model,
                    "messages": openrouter_messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
                timeout=120,
            )
            
            response.raise_for_status()
            data = response.json()
            
            return LLMResponse(
                content=data["choices"][0]["message"]["content"],
                model=data["model"],
                provider="openrouter",
                usage=data.get("usage"),
            )
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                logger.error("OpenRouter authentication failed")
                return LLMResponse(
                    content="",
                    model="",
                    provider="openrouter",
                    error="Invalid API key"
                )
            elif e.response.status_code == 429:
                logger.error("OpenRouter rate limit exceeded")
                return LLMResponse(
                    content="",
                    model="",
                    provider="openrouter",
                    error="Rate limit exceeded"
                )
            else:
                logger.error("OpenRouter API error", status=e.response.status_code)
                return LLMResponse(
                    content="",
                    model="",
                    provider="openrouter",
                    error=f"API error: {e.response.status_code}"
                )
        except Exception as e:
            logger.error("OpenRouter error", error=str(e))
            return LLMResponse(
                content="",
                model="",
                provider="openrouter",
                error=f"Error: {str(e)}"
            )


class LLMManager:
    """Manages all LLM providers and handles provider selection."""
    
    def __init__(self):
        self.config = ProviderConfig()
        self.providers = {
            "openai": OpenAIProvider(self.config),
            "anthropic": AnthropicProvider(self.config),
            "google": GoogleProvider(self.config),
            "openrouter": OpenRouterProvider(self.config),
        }
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers (with API keys)."""
        return [
            name for name, provider in self.providers.items()
            if provider.is_available()
        ]
    
    def chat(self, messages: List[LLMMessage], provider: Optional[str] = None, **kwargs) -> LLMResponse:
        """Send chat request to specified or active provider."""
        
        if provider is None:
            provider = self.config.get_active_provider()
        
        if provider not in self.providers:
            return LLMResponse(
                content="",
                model="",
                provider="",
                error=f"Unknown provider: {provider}"
            )
        
        provider_instance = self.providers[provider]
        
        if not provider_instance.is_available():
            # Try fallback providers
            available = self.get_available_providers()
            if available:
                fallback = available[0]
                logger.warning(f"Provider {provider} not available, using fallback: {fallback}")
                provider_instance = self.providers[fallback]
                provider = fallback
            else:
                return LLMResponse(
                    content="",
                    model="",
                    provider=provider,
                    error="No LLM provider available. Please configure an API key in Settings."
                )
        
        return provider_instance.chat(messages, **kwargs)
    
    def test_provider(self, provider: str) -> bool:
        """Test if a provider is working."""
        if provider not in self.providers:
            return False
        
        provider_instance = self.providers[provider]
        if not provider_instance.is_available():
            return False
        
        try:
            response = provider_instance.chat([
                LLMMessage(role="user", content="Hi")
            ])
            return response.error is None
        except Exception as e:
            logger.error(f"Provider {provider} test failed", error=str(e))
            return False


# Global instance
_llm_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """Get or create global LLM manager instance."""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager
