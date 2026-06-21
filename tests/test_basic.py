"""Basic tests for AutoStockAnalyzer."""

import pytest
from src.config.settings import get_config


def test_config_loading():
    """Test configuration loading."""
    config = get_config()
    assert config.market.get('name') == 'A股'
    assert config.capital.get('initial') == 1000


def test_config_get_method():
    """Test config get method with dot notation."""
    config = get_config()
    assert config.get('ai.model') == 'mimo-v2.5'
    assert config.get('risk.level') == 'dynamic'
    assert config.get('nonexistent.key', 'default') == 'default'


def test_market_config():
    """Test market configuration."""
    config = get_config()
    market = config.market
    assert 'name' in market
    assert 'exchanges' in market
    assert len(market['exchanges']) == 2


def test_risk_config():
    """Test risk configuration."""
    config = get_config()
    risk = config.risk
    assert risk['max_position'] == 0.2
    assert risk['stop_loss'] == 0.08
    assert risk['min_stocks'] == 3
    assert risk['max_stocks'] == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
