"""Data contract for the ANBIMA national-holidays workbook.

The ANBIMA ``.xls`` carries its header on the first row, in Portuguese (``Data``,
``Dia da Semana``, ``Feriado``), followed by the holiday rows and a block of footnotes.
``tabular_reader.read_table`` asserts these three published columns are present before the
provider renames them to ``DATE``, ``WEEKDAY`` and ``NAME`` and transforms them, so a publisher
that renames a column fails loudly instead of yielding an empty calendar.
"""

from __future__ import annotations

from opendata_calendars._internal.utils.tabular_reader import FileContract


ANBIMA_HOLIDAYS = FileContract(
    "ANBIMA National Holidays",
    "anbima_holidays",
    ("Data", "Dia da Semana", "Feriado"),
    (),
)
