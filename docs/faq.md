# **FAQ**

Answers to common questions about using and developing this library. Add project-specific
entries as they come up in issues.

> **See also:** [Usage](usage.md) · [Examples](examples.md) · [Contributing](contributing.md).

---

## How do I install it?

```bash
pip install opendata-calendars
```

## How do I add or update a dependency?

Use Poetry so the lock file stays authoritative:

```bash
poetry add <package>          # runtime dependency
poetry add --group dev <package>   # dev-only tool
```

Every package the code imports must be a **direct** dependency — never rely on it arriving
transitively through another package.

## Which Python versions are supported?

See the `python = "..."` constraint in `pyproject.toml`; CI runs the test matrix against each.

## How is the version determined?

The version comes from the latest git tag `vX.Y.Z`, through `poetry-dynamic-versioning`;
`pyproject.toml` keeps only a placeholder. See [Contributing](contributing.md#releasing).

## Where do the offline calendars live?

In `purecalendars`, which computes holidays without any network access. This package is the
live counterpart: it fetches the publisher pages and `bin/check_calendar_drift.py` compares the
two.
