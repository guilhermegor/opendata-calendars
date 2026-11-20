"""opendata-calendars package."""

from importlib.metadata import PackageNotFoundError, version

from .main import main


try:
    __version__ = version("opendata-calendars")
except PackageNotFoundError:  # pragma: no cover - source tree without an installed dist
    __version__ = "0.0.0"


__all__ = [
    "__version__",
    "main",
]
