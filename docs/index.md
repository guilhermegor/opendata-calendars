# **opendata-calendars** <img src="assets/logo.png" align="right" width="200" style="border-radius: 15px;" alt="opendata-calendars">

Fetch exchange and bank holiday calendars from their publishers (B3, ANBIMA, FEBRABAN, NASDAQ, US federal), with cache and provenance, returned as purecalendars calendars.

---

## Contents

| Section | Description |
|---------|-------------|
| [Usage](usage.md) | Installation, imports, and usage examples |
| [API Reference](api/index.md) | Module-level functions and public interface |

---

## Quick start

```bash
bash bin/venv.sh   # bootstrap the venv (poe lives inside it, so bootstrap is shell)
poe unit_tests    # run the test suite
poe docs_serve   # serve this documentation at http://0.0.0.0:8000
```

---

Generated from the **lib-minimal** template via [BlueprintX](https://github.com/guilhermegor/BlueprintX).
