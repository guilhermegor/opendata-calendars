# **Examples**

Task-oriented, self-contained snippets for common uses of this library. Each recipe stands
alone — copy it and adjust.

> **See also:** [Usage](usage.md) for the basics · [API Reference](api/index.md) for every public
> symbol.

---

## Recipe: read the installed version

Log which release of the library is running, for example in a bug report.

```python
import opendata_calendars

print(opendata_calendars.__version__)
```

`tests/unit/test_public_api.py` covers this snippet. Add one `##` section per recipe as the public
API grows.
