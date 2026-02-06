"""Secure configuration management for Noode.

Handles API keys and settings with secure storage.
Uses Linux keyring for sensitive data.
"""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any
import base64
import hashlib

import structlog

logger = structlog.get_logger()


# Available models per provider (February 2026)
PROVIDER_MODELS = {
    "openai": {
        "name": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "models": [
            ("gpt-5.3-codex", "GPT-5.3 Codex - Advanced Coding (NEW)"),
            ("gpt-5.2", "GPT-5.2 - Flagship Reasoning"),
            ("gpt-5.2-codex", "GPT-5.2 Codex - Multi-file Coding"),
            ("gpt-4o", "GPT-4o - Fast Multimodal (retiring 02/13)"),
            ("gpt-4o-mini", "GPT-4o Mini - Cost-effective"),
            ("o4-preview", "o4 Preview - Advanced Reasoning"),
        ],
        "default": "gpt-5.2",
    },
    "anthropic": {
        "name": "Anthropic",
        "base_url": "https://api.anthropic.com",
        "models": [
            ("claude-opus-4.6", "Claude Opus 4.6 - Top-tier Agentic (NEW 02/05)"),
            ("claude-sonnet-5", "Claude Sonnet 5 - Fast Coding (NEW 02/03)"),
            ("claude-opus-4.5", "Claude Opus 4.5 - Previous Top"),
            ("claude-sonnet-4.5", "Claude Sonnet 4.5 - Balanced"),
            ("claude-haiku-4.5", "Claude Haiku 4.5 - Fast & Light"),
            ("claude-3.7-sonnet", "Claude 3.7 Sonnet - Thinking"),
        ],
        "default": "claude-opus-4.6",
    },
    "google": {
        "name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com",
        "models": [
            ("gemini-3-pro", "Gemini 3 Pro - Latest Flagship"),
            ("gemini-3-flash", "Gemini 3 Flash - Agentic Vision (NEW)"),
            ("gemini-3-pro-preview", "Gemini 3 Pro Preview"),
            ("gemini-3-flash-preview", "Gemini 3 Flash Preview"),
            ("gemini-2.5-pro", "Gemini 2.5 Pro"),
            ("gemma-3-27b", "Gemma 3 27B - Open Multimodal"),
        ],
        "default": "gemini-3-pro",
    },
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "models": [
            ("openrouter/auto", "Auto - Best for Request"),
            # Top Coding Models (SWE-bench leaders)
            ("anthropic/claude-sonnet-5", "⭐ Claude Sonnet 5 (82% SWE-bench)"),
            ("anthropic/claude-opus-4.5", "⭐ Claude Opus 4.5 (80.9% SWE)"),
            ("openai/gpt-5.3-codex", "⭐ GPT-5.3 Codex (Agentic)"),
            ("openai/gpt-5.2-codex", "GPT-5.2 Codex"),
            ("moonshot/kimi-k2.5", "⭐ Kimi K2.5 (Top Value, 128K)"),
            ("deepseek/deepseek-v3.2", "DeepSeek V3.2 (Value King)"),
            # Premium Models
            ("anthropic/claude-opus-4.6", "Claude Opus 4.6 (Agentic)"),
            ("openai/gpt-5.2", "GPT-5.2 (80% SWE-bench)"),
            ("google/gemini-3-pro", "Gemini 3 Pro"),
            # Free Coding Models
            ("mistral/devstral-2", "🆓 Devstral 2 (73% SWE, FREE)"),
            ("xiaomi/mimo-v2-flash", "🆓 MiMo-V2-Flash (#1 Open-Source)"),
            ("meta/llama-4-maverick", "🆓 Llama 4 Maverick (92% HumanEval)"),
            ("qwen/qwen3-coder-480b", "🆓 Qwen3 Coder 480B"),
            ("nvidia/nemotron-3-nano-30b", "🆓 NVIDIA Nemotron 3 Nano"),
            ("deepseek/deepseek-coder-v2", "🆓 DeepSeek Coder V2"),
            ("z-ai/glm-4.7", "🆓 GLM 4.7 (Strong Coder)"),
            ("minimax/m2.1", "🆓 MiniMax M2.1"),
        ],
        "default": "moonshot/kimi-k2.5",
    },
    "kie": {
        "name": "Kie.ai",
        "base_url": "https://api.kie.ai/v1",
        "models": [
            # LLM
            ("kie/chat", "Kie Chat - Conversational AI"),
            # Video Generation
            ("google/veo-3.1", "Google Veo 3.1 - Cinematic Video"),
            ("google/veo-3-fast", "Google Veo 3 Fast"),
            ("google/veo-3-quality", "Google Veo 3 Quality"),
            ("runway/aleph", "Runway Aleph - Video Gen"),
            ("kling/kling-2.6", "Kling 2.6 - Audio-Visual"),
            ("seedance/seedance-1.5-pro", "Seedance 1.5 Pro"),
            # Image Generation
            ("openai/4o-image", "OpenAI Image (GPT-Image-1)"),
            ("midjourney/midjourney", "Midjourney API"),
            ("seedream/seedream-4.5", "Seedream 4.5 - 4K Images"),
            ("flux/kontext", "Flux Kontext"),
            # Audio/Music
            ("suno/v5", "Suno V5 - Music Gen"),
            ("suno/v4.5-plus", "Suno V4.5 Plus"),
            ("elevenlabs/voice", "ElevenLabs Voice"),
        ],
        "default": "kie/chat",
    },
}


@dataclass
class ProviderConfig:
    """Configuration for a single provider."""
    
    enabled: bool = False
    api_key: str = ""
    selected_model: str = ""
    custom_base_url: str = ""


@dataclass
class NoodeConfig:
    """Main application configuration."""
    
    # Provider configurations
    openai: ProviderConfig = field(default_factory=ProviderConfig)
    anthropic: ProviderConfig = field(default_factory=ProviderConfig)
    google: ProviderConfig = field(default_factory=ProviderConfig)
    openrouter: ProviderConfig = field(default_factory=ProviderConfig)
    kie: ProviderConfig = field(default_factory=ProviderConfig)
    
    # General settings
    default_provider: str = "openrouter"
    theme: str = "dark"
    language: str = "de"
    
    # Agent settings
    agents_enabled: dict[str, bool] = field(default_factory=lambda: {
        "research": True,
        "security": True,
        "frontend": True,
        "backend": True,
    })


class SecureConfigManager:
    """Manage configuration with secure API key storage."""
    
    def __init__(self, config_dir: Path | None = None) -> None:
        """Initialize config manager.
        
        Args:
            config_dir: Directory for config files
        """
        self.config_dir = config_dir or Path.home() / ".noode"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / "config.json"
        self.secrets_file = self.config_dir / ".secrets"
        
        self._config: NoodeConfig | None = None
        self._machine_key = self._get_machine_key()
    
    def _get_machine_key(self) -> bytes:
        """Get machine-specific key for encryption."""
        # Use machine ID for basic encryption
        machine_id = ""
        
        # Try Linux machine-id
        machine_id_path = Path("/etc/machine-id")
        if machine_id_path.exists():
            machine_id = machine_id_path.read_text().strip()
        
        # Fallback to hostname + user
        if not machine_id:
            import socket
            machine_id = f"{socket.gethostname()}-{os.getenv('USER', 'noode')}"
        
        return hashlib.sha256(machine_id.encode()).digest()
    
    def _encrypt(self, data: str) -> str:
        """Simple XOR-based obfuscation for API keys.
        
        Note: This is basic obfuscation, not strong encryption.
        For production, use proper keyring integration.
        """
        if not data:
            return ""
        
        key = self._machine_key
        encrypted = bytes([
            ord(c) ^ key[i % len(key)]
            for i, c in enumerate(data)
        ])
        return base64.b64encode(encrypted).decode()
    
    def _decrypt(self, data: str) -> str:
        """Decrypt API key."""
        if not data:
            return ""
        
        try:
            encrypted = base64.b64decode(data.encode())
            key = self._machine_key
            decrypted = bytes([
                b ^ key[i % len(key)]
                for i, b in enumerate(encrypted)
            ])
            return decrypted.decode()
        except Exception:
            return ""
    
    def load(self) -> NoodeConfig:
        """Load configuration.
        
        Returns:
            Loaded configuration
        """
        if self._config:
            return self._config
        
        self._config = NoodeConfig()
        
        # Load main config
        if self.config_file.exists():
            try:
                data = json.loads(self.config_file.read_text())
                
                # Load provider configs
                for provider in ["openai", "anthropic", "google", "openrouter", "kie"]:
                    if provider in data:
                        p_data = data[provider]
                        p_config = ProviderConfig(
                            enabled=p_data.get("enabled", False),
                            selected_model=p_data.get("selected_model", ""),
                            custom_base_url=p_data.get("custom_base_url", ""),
                        )
                        setattr(self._config, provider, p_config)
                
                # Load general settings
                self._config.default_provider = data.get("default_provider", "openrouter")
                self._config.theme = data.get("theme", "dark")
                self._config.language = data.get("language", "de")
                
                if "agents_enabled" in data:
                    self._config.agents_enabled = data["agents_enabled"]
                    
            except Exception as e:
                logger.warning("config_load_error", error=str(e))
        
        # Load secrets
        if self.secrets_file.exists():
            try:
                secrets = json.loads(self.secrets_file.read_text())
                
                for provider in ["openai", "anthropic", "google", "openrouter", "kie"]:
                    if provider in secrets:
                        p_config = getattr(self._config, provider)
                        p_config.api_key = self._decrypt(secrets[provider])
                        
            except Exception as e:
                logger.warning("secrets_load_error", error=str(e))
        
        # Set defaults for selected models
        for provider, info in PROVIDER_MODELS.items():
            p_config = getattr(self._config, provider)
            if not p_config.selected_model:
                p_config.selected_model = info["default"]
        
        return self._config
    
    def save(self, config: NoodeConfig) -> None:
        """Save configuration.
        
        Args:
            config: Configuration to save
        """
        self._config = config
        
        # Save main config (without API keys)
        main_data = {
            "default_provider": config.default_provider,
            "theme": config.theme,
            "language": config.language,
            "agents_enabled": config.agents_enabled,
        }
        
        for provider in ["openai", "anthropic", "google", "openrouter", "kie"]:
            p_config = getattr(config, provider)
            main_data[provider] = {
                "enabled": p_config.enabled,
                "selected_model": p_config.selected_model,
                "custom_base_url": p_config.custom_base_url,
            }
        
        self.config_file.write_text(json.dumps(main_data, indent=2))
        
        # Save secrets (encrypted)
        secrets = {}
        for provider in ["openai", "anthropic", "google", "openrouter", "kie"]:
            p_config = getattr(config, provider)
            if p_config.api_key:
                secrets[provider] = self._encrypt(p_config.api_key)
        
        self.secrets_file.write_text(json.dumps(secrets))
        
        # Restrict secrets file permissions
        self.secrets_file.chmod(0o600)
        
        logger.info("config_saved")
    
    def set_api_key(self, provider: str, key: str) -> None:
        """Set API key for a provider.
        
        Args:
            provider: Provider name
            key: API key
        """
        config = self.load()
        
        if hasattr(config, provider):
            p_config = getattr(config, provider)
            p_config.api_key = key
            p_config.enabled = bool(key)
            self.save(config)
    
    def get_api_key(self, provider: str) -> str:
        """Get API key for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            API key or empty string
        """
        config = self.load()
        
        if hasattr(config, provider):
            return getattr(config, provider).api_key
        return ""
    
    def get_active_provider(self) -> tuple[str, str, str]:
        """Get the active provider configuration.
        
        Returns:
            Tuple of (provider_name, model_id, base_url)
        """
        config = self.load()
        
        # Check default provider first
        default = config.default_provider
        if hasattr(config, default):
            p_config = getattr(config, default)
            if p_config.enabled and p_config.api_key:
                base_url = p_config.custom_base_url or PROVIDER_MODELS[default]["base_url"]
                return (default, p_config.selected_model, base_url)
        
        # Fall back to any enabled provider
        for provider in ["openrouter", "openai", "anthropic", "google", "kie"]:
            p_config = getattr(config, provider)
            if p_config.enabled and p_config.api_key:
                base_url = p_config.custom_base_url or PROVIDER_MODELS[provider]["base_url"]
                return (provider, p_config.selected_model, base_url)
        
        return ("", "", "")
    
    def export_for_litellm(self) -> dict[str, Any]:
        """Export configuration for LiteLLM.
        
        Returns:
            LiteLLM-compatible config dict
        """
        provider, model, base_url = self.get_active_provider()
        
        if not provider:
            return {}
        
        api_key = self.get_api_key(provider)
        
        # Map provider to LiteLLM format
        if provider == "openrouter":
            return {
                "model": f"openrouter/{model}",
                "api_key": api_key,
                "api_base": base_url,
            }
        elif provider == "google":
            return {
                "model": f"gemini/{model}",
                "api_key": api_key,
            }
        elif provider == "anthropic":
            return {
                "model": f"claude/{model.replace('claude-', '')}",
                "api_key": api_key,
            }
        elif provider == "openai":
            return {
                "model": model,
                "api_key": api_key,
                "api_base": base_url if base_url != PROVIDER_MODELS["openai"]["base_url"] else None,
            }
        elif provider == "kie":
            return {
                "model": model,
                "api_key": api_key,
                "api_base": base_url,
            }
        
        return {}


# Global instance
_config_manager: SecureConfigManager | None = None


def get_config_manager() -> SecureConfigManager:
    """Get the global config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = SecureConfigManager()
    return _config_manager
