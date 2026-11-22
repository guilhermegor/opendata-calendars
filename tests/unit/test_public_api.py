"""Pin the frozen 1.x public API and run the README usage snippet."""

import importlib
import re

import pytest

import opendata_calendars


def test_public_api_is_frozen() -> None:
    """Adding or removing a public name must be a deliberate edit of this list."""
    assert opendata_calendars.__all__ == ["__version__"]


def test_every_public_name_resolves() -> None:
    """Each name in ``__all__`` exists on the package."""
    assert all(hasattr(opendata_calendars, name) for name in opendata_calendars.__all__)


def test_version_is_a_dotted_string() -> None:
    """The README snippet ``print(opendata_calendars.__version__)`` prints a version string."""
    assert re.match(r"^\d+\.\d+\.\d+", opendata_calendars.__version__)


@pytest.mark.parametrize(
    ("str_module", "list_expected"),
    [
        ("opendata_calendars.br", ["DatesBRAnbimaWeb", "DatesBRB3Web", "DatesBRFebrabanWeb"]),
        ("opendata_calendars.us", ["DatesUSFederalHolidaysWeb", "DatesUSNasdaq"]),
    ],
)
def test_provider_packages_export_the_web_classes(
    str_module: str, list_expected: list[str]
) -> None:
    """Adding or removing a provider must be a deliberate edit of this list."""
    assert importlib.import_module(str_module).__all__ == list_expected
