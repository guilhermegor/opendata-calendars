# **Examples**

Task-oriented, self-contained snippets for common uses of this library. Each recipe stands
alone — copy it and adjust.

> **See also:** [Usage](usage.md) for the basics · [API Reference](api/index.md) for every public
> symbol.

---

## Recipe: business days from the ANBIMA calendar

Count the working days between two dates with the table ANBIMA publishes.

```python
from datetime import date

from opendata_calendars.br import DatesBRAnbimaWeb

cls_calendar = DatesBRAnbimaWeb()
print(cls_calendar.holidays()[0])
print(cls_calendar.is_working_day(date(2026, 4, 21)))
```

## Recipe: keep the fetch in memory

Skip the disk cache, for example in a short-lived job.

```python
from opendata_calendars.us import DatesUSNasdaq

cls_calendar = DatesUSNasdaq(bool_persist_cache=False)
print(cls_calendar.holidays()[0])
```

## Recipe: read the installed version

```python
import opendata_calendars

print(opendata_calendars.__version__)
```
