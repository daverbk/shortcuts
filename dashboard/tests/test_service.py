from unittest.mock import patch

import pytest

from service.currency_service import CurrencyRatioResolver


def test_resolve_valid_currency_pln():
    resolver = CurrencyRatioResolver()

    with patch.object(resolver, 'get_currency_ratio', return_value=4.23):
        result = resolver.resolve('pln')
        assert result == 4.23


def test_resolve_valid_currency_byn():
    resolver = CurrencyRatioResolver()

    with patch.object(resolver, 'get_byn_ratio', return_value=0.39):
        result = resolver.resolve('byn')
        assert result == 0.39


def test_resolve_valid_currency_eur():
    resolver = CurrencyRatioResolver()

    with patch.object(resolver, 'get_currency_ratio', return_value=1.12):
        result = resolver.resolve('eur')
        assert result == 1.12


def test_resolve_invalid_currency():
    resolver = CurrencyRatioResolver()

    with pytest.raises(ValueError):
        resolver.resolve('usd')
