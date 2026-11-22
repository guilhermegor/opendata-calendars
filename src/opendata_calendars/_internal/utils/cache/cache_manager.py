"""Cache manager for caching expensive data fetches.

This module provides a class for caching method results in memory and optionally persisting
them to a JSON file (data only, never pickle). Cache files written by older
versions as ``.pkl`` are ignored and never unpickled.

Example
-------
```python
from logging import Logger
from typing import Optional
import pandas as pd
from opendata_calendars._internal.utils.cache.cache_manager import CacheManager

class DataProcessor:
    def __init__(self, cache_dir: Optional[str] = None, logger: Optional[Logger] = None):
        self.cls_cache_manager = CacheManager(
            bool_persist_cache=True,
            bool_reuse_cache=True,
            int_days_cache_expiration=1,
            int_cache_ttl_days=30,
            path_cache_dir=cache_dir,
            logger=logger
        )

    @CacheManager.cache_df(key="raw_data_fetched")
    def fetch_data(self) -> pd.DataFrame:
        return pd.DataFrame({"data": [1, 2, 3]})

processor = DataProcessor()
df_ = processor.fetch_data()
df_cached = processor.fetch_data()
```
"""

from collections.abc import Callable
from datetime import UTC, datetime, timedelta
from functools import wraps
import json
from logging import Logger
import os
from pathlib import Path
import platform
from typing import Any

import pandas as pd

from opendata_calendars._internal.utils.logs_emitter import LogsEmitter
from opendata_calendars._internal.utils.retry import LogEmitter
from opendata_calendars._internal.utils.typing import TypeChecker, type_checker


@type_checker
def _current_timestamp_string() -> str:
    """Return the current UTC timestamp as a ``YYYYMMDD_HHMMSS`` string.

    Returns
    -------
    str
            The current UTC timestamp, used to build timestamped cache keys.
    """
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


class CacheManager(metaclass=TypeChecker):
    """A class for caching method results in memory and optionally persisting them to a file."""

    def __init__(
        self,
        bool_persist_cache: bool = True,
        bool_reuse_cache: bool = True,
        int_days_cache_expiration: int = 1,
        int_cache_ttl_days: int = 30,
        path_cache_dir: str | os.PathLike[str] | None = None,
        logger: Logger | None = None,
        cls_log_emitter: LogEmitter | None = None,
    ) -> None:
        """Initialize the CacheManager class.

        Parameters
        ----------
        bool_persist_cache : bool
                If True, saves cache to disk; if False, uses in-memory cache only (default: True)
        bool_reuse_cache : bool
                If True, caches in-memory; if False, does not cache in-memory (default: True)
        int_days_cache_expiration : int
                Number of days after which the cache expires (default: 1)
        int_cache_ttl_days : int
                Number of days after which the cache is considered expired (default: 30)
        path_cache_dir : str | os.PathLike[str] | None
                Path to the cache directory (default: None)
        logger : Optional[Logger]
                The stdlib logger to back the default log emitter (default: None)
        cls_log_emitter : Optional[LogEmitter]
                Injectable log sink; defaults to a rich ``LogsEmitter`` over ``logger`` (timestamp,
                level, and reconstructed ``{Class} [method]`` caller context). When ``logger`` is
                None the rich line is printed to the screen (default: None)

        Returns
        -------
        None

        Notes
        -----
        [1] The cache directory is created if it does not exist, but only when
            ``bool_persist_cache`` is True; an in-memory manager touches no disk
        [2] TTL stands for time-to-live, or retention time period for a given resource
        """
        self.bool_persist_cache = bool_persist_cache
        self.bool_reuse_cache = bool_reuse_cache
        self.logger = logger
        self.cls_log_emitter = (
            cls_log_emitter if cls_log_emitter is not None else LogsEmitter(logger)
        )
        self._cache: dict[str, pd.DataFrame] = {}
        self._cache_created: dict[str, datetime] = {}
        self._path_cache_dir = self._get_cache_dir_path(path_cache_dir, bool_persist_cache)
        self.timedelta_cache_expiry = timedelta(days=int_days_cache_expiration)
        self.timedelta_cache_ttl_days = timedelta(days=int_cache_ttl_days)

    def _get_cache_dir_path(
        self, path_cache_dir: str | os.PathLike[str] | None, bool_create: bool = True
    ) -> Path:  # complexity-ok: ported verbatim
        """Get the path to the cache directory.

        Parameters
        ----------
        path_cache_dir : str | os.PathLike[str] | None
                Path to the cache directory
        bool_create : bool
                If True, create the directory when missing (default: True)

        Returns
        -------
        Path
                Path to the cache directory
        """
        if path_cache_dir:
            path_resolved = Path(path_cache_dir)
        elif platform.system() == "Windows":
            path_appdata = Path(os.getenv("APPDATA") or Path.home() / "AppData" / "Roaming")
            path_resolved = path_appdata / "opendata_calendars_cache"
        else:
            path_resolved = Path.home() / ".cache" / "opendata_calendars_cache"
        if bool_create:
            path_resolved.mkdir(mode=0o700, parents=True, exist_ok=True)
        return path_resolved

    @staticmethod
    def cache_df(  # complexity-ok: ported verbatim
        key: str | Callable,
    ) -> Callable:
        """Decorate a function to cache its output as a DataFrame.

        Parameters
        ----------
        key : str | Callable
                Key to use for caching, either a literal string or a callable taking the
                decorated method's instance — use the callable form whenever the cached frame
                depends on constructor arguments, so two differently-configured instances do
                not share one entry.

        Returns
        -------
        Callable
                Decorated function

        Raises
        ------
        ValueError
                If there is an error generating the cache key from callable.
        AttributeError
                If the instance does not have a 'cls_cache_manager' attribute
        """

        @type_checker
        def decorator(  # complexity-ok: ported verbatim
            func: Callable,
        ) -> Callable:
            """Decorate a function to cache its output as a DataFrame.

            Parameters
            ----------
            func : Callable
                    The function to decorate

            Returns
            -------
            Callable
                    Decorated function

            Raises
            ------
            ValueError
                    If there is an error generating the cache key from callable.
            AttributeError
                    If the instance does not have a 'cls_cache_manager' attribute
            """

            @type_checker
            @wraps(func)
            def wrapper(  # type: ignore[explicit-any]  # complexity-ok: ported verbatim
                self: Any,  # noqa: ANN401
                *args: Any,  # noqa: ANN401
                **kwargs: Any,  # noqa: ANN401
            ) -> pd.DataFrame:
                """Wrap the function to cache its output as a DataFrame.

                Parameters
                ----------
                self : Any
                        Instance of the class
                *args : Any
                        Variable-length argument list
                **kwargs : Any
                        Arbitrary keyword arguments

                Returns
                -------
                pd.DataFrame
                        Cached DataFrame

                Raises
                ------
                ValueError
                        If there is an error generating the cache key from callable.
                AttributeError
                        If the instance does not have a 'cls_cache_manager' attribute
                """
                cls_cache_manager = getattr(self, "cls_cache_manager", None)
                if cls_cache_manager is None:
                    raise AttributeError("Instance must have 'cls_cache_manager' attribute")

                if callable(key):
                    try:
                        cache_key = key(self)
                    except Exception as e:
                        raise ValueError(f"Error generating cache key from callable: {e}") from e
                else:
                    cache_key = key

                df_cached = cls_cache_manager._load_cache(key=cache_key)
                if (
                    df_cached is not None
                    and not df_cached.empty
                    and cls_cache_manager.bool_reuse_cache
                ):
                    cls_cache_manager.cls_log_emitter.log_message(
                        f"Using cached holidays from {cache_key}. "
                        f"Path: {cls_cache_manager._path_cache_dir}",
                        "info",
                    )
                    return df_cached
                cls_cache_manager.cls_log_emitter.log_message(
                    f"Fetching holidays from {cache_key}", "info"
                )
                df_ = func(self, *args, **kwargs)
                cls_cache_manager._save_cache(key=cache_key, df_=df_)
                cls_cache_manager._save_cache(
                    key=f"{cache_key}_{_current_timestamp_string()}",
                    df_=df_,
                )
                cls_cache_manager._clean_old_cache()
                return df_

            return wrapper

        return decorator

    def _load_cache(self, key: str) -> pd.DataFrame | None:  # complexity-ok: ported verbatim
        """Load a DataFrame from the cache file for a given key.

        Parameters
        ----------
        key : str
                Key for the cache file

        Returns
        -------
        Optional[pd.DataFrame]
                DataFrame loaded from the cache file, or None on a cache miss or an
                unreadable cache file
        """
        if self.bool_reuse_cache:
            df_cached = self._cache.get(key)
            datetime_created = self._cache_created.get(key)
            bool_fresh = (
                datetime_created is None
                or datetime.now() - datetime_created < self.timedelta_cache_expiry
            )
            if bool_fresh and df_cached is not None and self._validate_cached_dataframe(df_cached):
                return df_cached

        if not self.bool_persist_cache:
            return None

        path_cache_file = self._get_cache_file_path(key)
        if path_cache_file.exists():  # complexity-ok: ported verbatim
            try:
                datetime_creation, df_ = self._read_cache_file(path_cache_file)
                if datetime.now() - datetime_creation < self.timedelta_cache_expiry:
                    if self._validate_cached_dataframe(df_):
                        return df_
                else:
                    path_cache_file.unlink()
            except (EOFError, ValueError, TypeError, KeyError, OSError) as err:
                self.cls_log_emitter.log_message(
                    f"Discarding unreadable cache file {path_cache_file}: {err}",
                    "warning",
                )
                path_cache_file.unlink(missing_ok=True)

        return None

    def _get_cache_file_path(self, key: str) -> Path:
        """Get the path to the cache file for a given key.

        Parameters
        ----------
        key : str
                Key for the cache file

        Returns
        -------
        Path
                Path to the cache file
        """
        safe_key = "".join(c if c.isalnum() else "_" for c in key)
        return self._path_cache_dir / f"{safe_key}.json"

    @staticmethod
    def _write_cache_file(
        path_cache_file: Path, datetime_creation: datetime, df_: pd.DataFrame
    ) -> None:
        """Write a DataFrame and its creation timestamp to one JSON file.

        Parameters
        ----------
        path_cache_file : Path
                Destination file
        datetime_creation : datetime
                Creation timestamp stored alongside the frame
        df_ : pd.DataFrame
                DataFrame to store

        Returns
        -------
        None
        """
        payload = {
            "created": datetime_creation.isoformat(),
            "dtypes": [str(dtype) for dtype in df_.dtypes],
            "index_dtype": str(df_.index.dtype),
            "index_name": df_.index.name,
            "frame": json.loads(df_.to_json(orient="split", date_format="iso", date_unit="ns")),
        }
        path_cache_file.write_text(json.dumps(payload), encoding="utf-8")

    @staticmethod
    def _read_cache_file(path_cache_file: Path) -> tuple[datetime, pd.DataFrame]:
        """Read the creation timestamp and DataFrame from a JSON cache file.

        Parameters
        ----------
        path_cache_file : Path
                Source file

        Returns
        -------
        tuple[datetime, pd.DataFrame]
                Creation timestamp and the stored frame
        """
        payload = json.loads(path_cache_file.read_text(encoding="utf-8"))
        frame = payload["frame"]
        index_ = pd.Index(frame["index"], name=payload["index_name"]).astype(
            payload["index_dtype"]
        )
        df_ = pd.DataFrame(frame["data"], index=index_, columns=frame["columns"])
        df_ = df_.astype(dict(zip(df_.columns, payload["dtypes"], strict=True)))
        return datetime.fromisoformat(payload["created"]), df_

    def _validate_cached_dataframe(
        self, df_: pd.DataFrame
    ) -> bool:  # complexity-ok: ported verbatim
        """Validate a cached DataFrame.

        Parameters
        ----------
        df_ : pd.DataFrame
                DataFrame to validate

        Returns
        -------
        bool
                True if the DataFrame is valid, False otherwise

        Raises
        ------
        ValueError
                If the DataFrame is invalid
        """
        try:
            if df_ is None or not isinstance(df_, pd.DataFrame) or df_.empty:
                return False
            return not len(df_) < 1
        except Exception as err:
            raise ValueError(f"Warning: cache validation failed. Error: {err}") from err

    def _save_cache(self, key: str, df_: pd.DataFrame) -> None:  # complexity-ok: ported verbatim
        """Save a DataFrame to the cache (in-memory and disk).

        Parameters
        ----------
        key : str
                Key for the cache file
        df_ : pd.DataFrame
                DataFrame to save to the cache file

        Returns
        -------
        None

        Notes
        -----
        A failed disk write is logged and swallowed: the cache is an optimisation, and the
        caller already holds the fetched frame.
        """
        if self._validate_cached_dataframe(df_):  # complexity-ok: ported verbatim
            datetime_now = datetime.now()
            self._cache[key] = df_
            self._cache_created[key] = datetime_now
            if self.bool_persist_cache:
                path_cache_file = self._get_cache_file_path(key)
                try:
                    path_cache_file.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
                    self._write_cache_file(path_cache_file, datetime_now, df_)
                except OSError as err:
                    self.cls_log_emitter.log_message(
                        f"Failed to save cache to {path_cache_file}: {err}", "warning"
                    )

    def _clean_old_cache(  # complexity-ok: ported verbatim
        self,
    ) -> None:
        """Clean old cache files.

        Returns
        -------
        None

        Notes
        -----
        An unreadable file is logged and removed, never raised: cleaning runs after a
        successful fetch and must not discard its result.
        """
        if not self.bool_persist_cache:
            return
        datetime_now = datetime.now()
        for cache_file in self._path_cache_dir.glob("*.json"):
            try:
                datetime_creation, _ = self._read_cache_file(cache_file)
                if datetime_now - datetime_creation > self.timedelta_cache_ttl_days:
                    cache_file.unlink()
            except (ValueError, TypeError, KeyError, OSError) as err:
                self.cls_log_emitter.log_message(
                    f"Removing unreadable cache file {cache_file}: {err}", "warning"
                )
                cache_file.unlink(missing_ok=True)

    def clear_caches(  # complexity-ok: ported verbatim
        self,
    ) -> None:
        """Clear the in-memory and disk caches.

        Returns
        -------
        None

        Raises
        ------
        ValueError
                If there is an error clearing the cache
        """
        self._cache.clear()
        self._cache_created.clear()
        if self.bool_persist_cache:
            for cache_file in self._path_cache_dir.glob("*.json"):
                try:
                    cache_file.unlink()
                except Exception as err:
                    raise ValueError(
                        f"Warning: Failed to clear cache file {cache_file}: {err}"
                    ) from err
