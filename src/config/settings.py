"""Configuration management module."""

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


class Config:
    """Configuration manager for AutoStockAnalyzer."""
    
    def __init__(self, config_path: str = None):
        """Initialize configuration.
        
        Args:
            config_path: Path to config.yaml file
        """
        load_dotenv()
        
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
        
        self.config = self._load_config(config_path)
        self._resolve_env_vars()
    
    def _load_config(self, config_path: Path) -> dict:
        """Load configuration from YAML file."""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _resolve_env_vars(self) -> None:
        """Resolve environment variables in configuration."""
        self._resolve_dict(self.config)
    
    def _resolve_dict(self, d: dict) -> None:
        """Recursively resolve env vars in dict."""
        for key, value in d.items():
            if isinstance(value, dict):
                self._resolve_dict(value)
            elif isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                d[key] = os.getenv(env_var, "")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get configuration value by dot-separated path.
        
        Args:
            key_path: Dot-separated path (e.g., "ai.model")
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key_path.split(".")
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    @property
    def market(self) -> dict:
        """Get market configuration."""
        return self.config.get("market", {})
    
    @property
    def capital(self) -> dict:
        """Get capital configuration."""
        return self.config.get("capital", {})
    
    @property
    def risk(self) -> dict:
        """Get risk management configuration."""
        return self.config.get("risk", {})
    
    @property
    def ai(self) -> dict:
        """Get AI model configuration."""
        return self.config.get("ai", {})
    
    @property
    def data_sources(self) -> dict:
        """Get data sources configuration."""
        return self.config.get("data_sources", {})
    
    @property
    def report(self) -> dict:
        """Get report configuration."""
        return self.config.get("report", {})
    
    @property
    def scheduler(self) -> dict:
        """Get scheduler configuration."""
        return self.config.get("scheduler", {})


# Global config instance
_config = None


def get_config(config_path: str = None) -> Config:
    """Get global configuration instance.
    
    Args:
        config_path: Optional path to config file
        
    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
