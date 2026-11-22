# **Usage**

Examples for installing and using this library.

> **See also:** [API Reference](api/index.md)

---

## Installation

```bash
pip install opendata-calendars
```

Or with Poetry:

```bash
poetry add opendata-calendars
```

The federal-holidays scrape drives a browser, so it needs the `web` extra:

```bash
pip install "opendata-calendars[web]"
playwright install chromium
```

---

## Basic usage

```python
from datetime import date

from opendata_calendars.br import DatesBRB3Web

cls_calendar = DatesBRB3Web()
print(cls_calendar.holidays()[:3])
print(cls_calendar.is_working_day(date(2026, 12, 24)))
```

Every provider is a `purecalendars` calendar whose holiday list comes from the publisher's own
page: B3, ANBIMA and FEBRABAN in `opendata_calendars.br`, Nasdaq and the US federal holidays in
`opendata_calendars.us`. The page is cached on disk under `opendata_calendars_cache` (the home
cache directory, or `%APPDATA%` on Windows); pass `path_cache_dir` to choose another one and
`bool_persist_cache=False` to keep it in memory only.

The providers build on the public calendar base of `purecalendars` (4.1.0 and later), so the
dependency is pinned below its next major version.

---

## Running tests

```bash
poe unit_tests         # unit tests only
poe integration_tests  # integration tests only
poe test_cov           # unit tests + coverage report + badge
```

---

## Linting and formatting

```bash
poe lint          # ruff check + ruff format + codespell + pydocstyle
```

---

## Publishing to PyPI

Two GitHub Actions workflows handle releases (present when the repo has a GitHub remote):

- **`release-test-pypi.yaml`** — publish to [Test PyPI](https://test.pypi.org) first.
- **`release-pypi.yaml`** — publish to [PyPI](https://pypi.org) and cut a GitHub release.

Trigger either from the **Actions** tab (`workflow_dispatch`) with the version to release.
Both gate on the new version being greater than the latest already published, build with
Poetry, and publish through OIDC trusted publishing, so no token secrets are needed.

Configure once, on each index (pypi.org and test.pypi.org), a pending publisher:

- PyPI: workflow `release-pypi.yaml`, environment `release-pypi`.
- Test PyPI: workflow `release-test-pypi.yaml`, environment `release-test-pypi`.

After the first `release-pypi.yaml` run creates the `gh-pages` branch, run `poe enable_pages`
once to serve the docs.
