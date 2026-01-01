"""
API Key Management for RAG-Based SOP Assistant
Centralized handling of API keys and environment variables
"""

import os
import yaml
from typing import Dict, Optional

class APIKeyManager:
    """Manages API keys for the RAG-Based SOP Assistant"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize API Key Manager

        Args:
            config_path: Path to config.yaml file. If None, uses default path.
        """
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), "config.yaml")

        self.config_path = config_path
        self.config = None
        self._load_config()

    def _load_config(self):
        """Load configuration from YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"⚠️  Warning: Config file not found at {self.config_path}")
            self.config = {}
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            self.config = {}

    def initialize_api_keys(self):
        """Set API keys as environment variables"""
        api_keys = {
            'HF_TOKEN': self.config.get('huggingface_token'),
            'OPENAI_API_KEY': self.config.get('openai_api_key'),
            'ANTHROPIC_API_KEY': self.config.get('anthropic_api_key')
        }

        keys_set = 0
        for env_var, key_value in api_keys.items():
            if key_value and key_value.strip():
                os.environ[env_var] = key_value.strip()
                keys_set += 1
                print(f"✅ Set {env_var}")
            else:
                # Don't override existing environment variables
                if env_var not in os.environ:
                    os.environ[env_var] = ""

        if keys_set > 0:
            print(f"🔑 Initialized {keys_set} API key(s)")
        else:
            print("🔓 No API keys configured (using free models)")

    def get_api_key_status(self) -> Dict[str, bool]:
        """Get status of API keys (whether they are set)"""
        return {
            'huggingface': bool(os.environ.get('HF_TOKEN')),
            'openai': bool(os.environ.get('OPENAI_API_KEY')),
            'anthropic': bool(os.environ.get('ANTHROPIC_API_KEY'))
        }

    def has_api_key(self, service: str) -> bool:
        """Check if API key is available for a specific service"""
        service_map = {
            'huggingface': 'HF_TOKEN',
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY'
        }

        env_var = service_map.get(service.lower())
        if env_var:
            return bool(os.environ.get(env_var))
        return False

    def reload_config(self):
        """Reload configuration from file"""
        self._load_config()
        self.initialize_api_keys()

# Global instance for easy access
api_manager = APIKeyManager()

def init_api_keys():
    """Convenience function to initialize API keys"""
    api_manager.initialize_api_keys()

def get_api_key_status():
    """Convenience function to get API key status"""
    return api_manager.get_api_key_status()

def has_api_key(service: str) -> bool:
    """Convenience function to check if API key is available"""
    return api_manager.has_api_key(service)

# Initialize API keys when module is imported
if __name__ != "__main__":
    init_api_keys()