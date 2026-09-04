import pytest

from truecart_ai.domain.models import Location


def test_location_for_pune() -> None:
    location = Location(pincode="411028")

    assert location.pincode == "411028"
    assert location.country == "IN"


def test_location_rejects_invalid_pincode() -> None:
    with pytest.raises(ValueError):
        Location(pincode="41102")


def test_location_rejects_non_numeric_pincode() -> None:
    with pytest.raises(ValueError):
        Location(pincode="ABCDEF")