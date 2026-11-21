# **API Reference**

Public interface for this library.

> **See also:** [Usage](../usage.md)

---

## Package: `opendata_calendars`

`opendata_calendars.__all__` is the whole public surface.

### `__version__: str`

The installed distribution's version, or `"0.0.0"` when running from a source tree without an
installed distribution.

```python
import opendata_calendars

print(opendata_calendars.__version__)
```

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
