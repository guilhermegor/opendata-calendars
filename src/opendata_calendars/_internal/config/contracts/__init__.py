"""Data contracts for the project's input files (config layer).

A contract is **declarative configuration** of an input's expected shape — which columns a
source must carry, which must hold valid CNPJs — *not* data access, so contracts live in
``config`` beside the other declarative config (``inputs.yaml``, ``connection_db``), imported
by the model loaders and the controller boundary.

Convention: **one file per source** under this package (``cadastro.py``, ``orders.py``, …),
each defining a single ``FileContract`` instance; this aggregator re-exports them (plus the
machinery from ``utils.tabular_reader``) so callers import from one place:
``from config.contracts import FileContract, find_file_problems``.
"""

from __future__ import annotations

from opendata_calendars._internal.utils.tabular_reader import (
    ContractError,
    FileContract,
    find_file_problems,
)


__all__ = [
    "ContractError",
    "FileContract",
    "find_file_problems",
]
