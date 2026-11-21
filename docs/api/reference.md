# **API Reference**

Public interface for this library.

> **See also:** [Usage](../usage.md)

---

## Package: `opendata_calendars`

The public surface is the `__all__` of `opendata_calendars`, `opendata_calendars.br` and
`opendata_calendars.us`.

### `__version__: str`

The installed distribution's version, or `"0.0.0"` when running from a source tree without an
installed distribution.

---

## Package: `opendata_calendars.br`

| Class | Source |
|-------|--------|
| `DatesBRAnbimaWeb` | ANBIMA national holidays workbook |
| `DatesBRB3Web` | B3 trading calendar page |
| `DatesBRFebrabanWeb` | FEBRABAN banking holidays endpoint |

## Package: `opendata_calendars.us`

| Class | Source |
|-------|--------|
| `DatesUSFederalHolidaysWeb` | federalholidays.net, scraped with Playwright (`web` extra) |
| `DatesUSNasdaq` | Nasdaq market holidays page |

Each class is a `purecalendars` calendar: `holidays()`, `is_working_day()` and the rest of the
business-day arithmetic come from that package. The constructors take `bool_persist_cache`,
`bool_reuse_cache`, `int_days_cache_expiration`, `int_cache_ttl_days`, `path_cache_dir` and
`logger`.

---

## Adding new modules

Place new modules under `src/opendata_calendars/`. Export public symbols from `src/opendata_calendars/__init__.py` and add them to `__all__`, so callers can do `from opendata_calendars import <name>`.

Follow the one-class-per-file convention: utility functions with no shared state belong at module level, not wrapped in a class.

---

## Conventions

| Convention | Rule |
|------------|------|
| Type hints | Required on all public functions, including `-> None` return types |
| Docstrings | NumPy style; explain *why*, not *what* |
| Variable names | Type-prefixed (`str_`, `list_`, `cls_`, `dict_`, …) |
| Testing | `unittest`; one assertion per test; name as `test_<unit>_<scenario>_<expected>` |
