"""Pin the frozen 1.x public API and run the README usage snippet."""

import re

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
