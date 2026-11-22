"""Brazilian holiday calendars fetched live from their publishers (ANBIMA, FEBRABAN, B3).

Each class subclasses the ``purecalendars`` calendar core, so the business-day arithmetic is the
same as for the offline ``purecalendars.br`` providers; only the holiday source differs.
"""

from opendata_calendars.br.anbima_web import DatesBRAnbimaWeb
from opendata_calendars.br.b3_web import DatesBRB3Web
from opendata_calendars.br.febraban_web import DatesBRFebrabanWeb


__all__ = [
    "DatesBRAnbimaWeb",
    "DatesBRB3Web",
    "DatesBRFebrabanWeb",
]
