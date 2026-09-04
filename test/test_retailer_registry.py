from truecart_ai.retailers.blinkit import BlinkitAdapter
from truecart_ai.retailers.bbnow import BBNowAdapter
from truecart_ai.retailers.flipkart_minutes import FlipkartMinutesAdapter
from truecart_ai.retailers.instamart import InstamartAdapter
from truecart_ai.retailers.registry import RetailerRegistry
from truecart_ai.retailers.zepto import ZeptoAdapter


def test_registry_contains_all_retailers() -> None:
    registry = RetailerRegistry()

    adapters = registry.get_all()

    assert len(adapters) == 5

    assert isinstance(adapters[0], BlinkitAdapter)
    assert isinstance(adapters[1], ZeptoAdapter)
    assert isinstance(adapters[2], InstamartAdapter)
    assert isinstance(adapters[3], FlipkartMinutesAdapter)
    assert isinstance(adapters[4], BBNowAdapter)


def test_registry_can_find_blinkit() -> None:
    registry = RetailerRegistry()

    adapter = registry.get("blinkit")

    assert isinstance(adapter, BlinkitAdapter)


def test_registry_returns_none_for_unknown_retailer() -> None:
    registry = RetailerRegistry()

    adapter = registry.get("unknown")

    assert adapter is None