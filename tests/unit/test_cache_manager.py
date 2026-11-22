"""Unit tests for CacheManager class.

Tests the cache management functionality with various input scenarios including:
- Initialization with valid and invalid inputs
- Cache loading, saving, and cleaning operations
- Decorator functionality and error conditions
- Edge cases and type validation
"""

from datetime import datetime, timedelta
from logging import Logger
from pathlib import Path
import re
from typing import Any
from unittest.mock import Mock, patch

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from opendata_calendars._internal.utils.cache.cache_manager import CacheManager
from opendata_calendars._internal.utils.logs_emitter import LogsEmitter


@pytest.fixture
def cache_manager_default() -> CacheManager:
    """Fixture providing CacheManager with default settings.

    Returns
    -------
    CacheManager
            Instance with default parameters
    """
    return CacheManager()


@pytest.fixture
def cache_manager_custom(tmp_path: Path) -> CacheManager:
    """Fixture providing CacheManager with custom cache directory.

    Parameters
    ----------
    tmp_path : Path
            Temporary directory path for testing

    Returns
    -------
    CacheManager
            Instance with custom cache directory
    """
    return CacheManager(path_cache_dir=str(tmp_path / "cache"))


@pytest.fixture
def mock_logger(mocker: MockerFixture) -> Logger:
    """Fixture providing a mock logger.

    Parameters
    ----------
    mocker : MockerFixture
            Pytest-mock fixture for creating mocks

    Returns
    -------
    Logger
            Mocked logger instance
    """
    return mocker.create_autospec(Logger)


@pytest.fixture
def sample_dataframe() -> pd.DataFrame:
    """Fixture providing a sample DataFrame for testing.

    Returns
    -------
    pd.DataFrame
            Sample DataFrame with test data
    """
    return pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})


def test_init_default_values() -> None:
    """Test initialization with default values.

    Verifies
    --------
    - Default parameters are set correctly
    - Cache directory is created
    - Internal cache is initialized as empty dict

    Returns
    -------
    None
    """
    # one-assert-ok: ported verbatim; facets of one scenario, split tracked in the ledger
    cm = CacheManager()
    assert cm.bool_persist_cache is True
    assert cm.bool_reuse_cache is True
    assert cm.timedelta_cache_expiry == timedelta(days=1)
    assert cm.timedelta_cache_ttl_days == timedelta(days=30)
    assert isinstance(cm._cache, dict)
    assert len(cm._cache) == 0
    assert isinstance(cm._path_cache_dir, Path)
    assert cm._path_cache_dir.exists()


def test_init_custom_values(tmp_path: Path, mock_logger: Logger) -> None:
    """Test initialization with custom values.

    Verifies
    --------
    - Custom parameters are set correctly
    - Custom cache directory is used
    - Logger is set correctly

    Parameters
    ----------
    tmp_path : Path
            Temporary directory path for testing
    mock_logger : Logger
            Mocked logger instance

    Returns
    -------
    None
    """
    # one-assert-ok: ported verbatim; facets of one scenario, split tracked in the ledger
    cache_dir = str(tmp_path / "custom_cache")
    cm = CacheManager(
        bool_persist_cache=False,
        bool_reuse_cache=False,
        int_days_cache_expiration=2,
        int_cache_ttl_days=60,
        path_cache_dir=cache_dir,
        logger=mock_logger,
    )
    assert cm.bool_persist_cache is False
    assert cm.bool_reuse_cache is False
    assert cm.timedelta_cache_expiry == timedelta(days=2)
    assert cm.timedelta_cache_ttl_days == timedelta(days=60)
    assert cm._path_cache_dir == Path(cache_dir)
    assert cm.logger == mock_logger


@pytest.mark.parametrize(
    "invalid_value",
    [None, "1", 1.0],
    ids=["none", "string", "float"],
)
def test_init_invalid_types_int_days_cache_expiration(
    invalid_value: Any,  # noqa ANN401: typing.Any is not allowed
) -> None:
    """Test initialization with invalid types for int_days_cache_expiration.

    Verifies
    --------
    - TypeError is raised with correct message for invalid types

    Parameters
    ----------
    invalid_value : Any
            Invalid values for int_days_cache_expiration

    Returns
    -------
    None
    """
    with pytest.raises(TypeError, match="violates type hint"):
        CacheManager(int_days_cache_expiration=invalid_value)


@pytest.mark.parametrize(
    "invalid_value",
    [None, "1", 1.0],
    ids=["none", "string", "float"],
)
def test_init_invalid_types_int_cache_ttl_days(
    invalid_value: Any,  # noqa ANN401: typing.Any is not allowed
) -> None:
    """Test initialization with invalid types for int_cache_ttl_days.

    Verifies
    --------
    - TypeError is raised with correct message for invalid types

    Parameters
    ----------
    invalid_value : Any
            Invalid values for int_cache_ttl_days

    Returns
    -------
    None
    """
    with pytest.raises(TypeError, match="violates type hint"):
        CacheManager(int_cache_ttl_days=invalid_value)


def test_get_cache_dir_path_custom(tmp_path: Path) -> None:
    """Test _get_cache_dir_path with custom path.

    Verifies
    --------
    - Custom path is returned as Path object
    - Directory is created if it doesn't exist

    Parameters
    ----------
    tmp_path : Path
            Temporary directory path for testing

    Returns
    -------
    None
    """
    # one-assert-ok: ported verbatim; facets of one scenario, split tracked in the ledger
    cache_dir = str(tmp_path / "test_cache")
    cm = CacheManager(path_cache_dir=cache_dir)
    result = cm._get_cache_dir_path(cache_dir)
    assert result == Path(cache_dir)
    assert result.exists()


@patch("platform.system")
def test_get_cache_dir_path_default_windows(mock_platform: Mock, tmp_path: Path) -> None:
    """Test _get_cache_dir_path with default path on Windows.

    Verifies
    --------
    - Default Windows path is used
    - Directory is created

    Parameters
    ----------
    mock_platform : Mock
            Mock for platform.system
    tmp_path : Path
            Temporary directory path for testing

    Returns
    -------
    None
    """
    # one-assert-ok: ported verbatim; facets of one scenario, split tracked in the ledger
    mock_platform.return_value = "Windows"
    with patch("os.getenv", return_value=str(tmp_path)):
        cm = CacheManager()
        result = cm._get_cache_dir_path(None)
        assert result == tmp_path / "opendata_calendars_cache"
        assert result.exists()


@patch("platform.system")
def test_get_cache_dir_path_default_non_windows(mock_platform: Mock, tmp_path: Path) -> None:
    """Test _get_cache_dir_path with default path on non-Windows.

    Verifies
    --------
    - Default non-Windows path is used
    - Directory is created

    Parameters
    ----------
    mock_platform : Mock
            Mock for platform.system
    tmp_path : Path
            Temporary directory path for testing

    Returns
    -------
    None
    """
    # one-assert-ok: ported verbatim; facets of one scenario, split tracked in the ledger
    mock_platform.return_value = "Linux"
    with patch("pathlib.Path.home", return_value=tmp_path):
        cm = CacheManager()
        result = cm._get_cache_dir_path(None)
        assert result == tmp_path / ".cache" / "opendata_calendars_cache"
        assert result.exists()


def test_cache_df_decorator_hit(  # complexity-ok: ported verbatim
    cache_manager_custom: CacheManager, sample_dataframe: pd.DataFrame, mocker: MockerFixture
) -> None:
    """Test cache_df decorator with cache hit.

    Verifies
    --------
    - Cached DataFrame is returned
    - Function is not called
    - Log message is recorded

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing
    mocker : MockerFixture
            Pytest-mock fixture for creating mocks

    Returns
    -------
    None
    """
    # one-assert-ok: ported verbatim; facets of one scenario, split tracked in the ledger
    mock_func = mocker.Mock(return_value=sample_dataframe)
    mock_log = mocker.patch.object(cache_manager_custom.cls_log_emitter, "log_message")

    class TestClass:
        """TestClass for testing cache_df decorator."""

        def __init__(self, cache_manager: CacheManager) -> None:
            """Initialize TestClass.

            Parameters
            ----------
            cache_manager : CacheManager
                    CacheManager instance

            Returns
            -------
            None
            """
            self.cls_cache_manager = cache_manager

        @CacheManager.cache_df("test_key")
        def dummy_func(
            self,
            *args: Any,  # noqa ANN401: typing.Any is not allowed
            **kwargs: Any,  # noqa ANN401: typing.Any is not allowed
        ) -> pd.DataFrame:
            """Implement dummy function for testing.

            Parameters
            ----------
            *args : Any
                    Variable-length argument list
            **kwargs : Any
                    Arbitrary keyword arguments

            Returns
            -------
            pd.DataFrame
                    Dummy DataFrame
            """
            return mock_func(self, *args, **kwargs)

    test_instance = TestClass(cache_manager_custom)
    cache_manager_custom._cache["test_key"] = sample_dataframe
    cache_manager_custom.bool_reuse_cache = True

    assert cache_manager_custom._load_cache("test_key") is not None
    assert cache_manager_custom._load_cache("test_key").equals(sample_dataframe)

    result = test_instance.dummy_func()
    assert result.equals(sample_dataframe)
    mock_func.assert_not_called()
    mock_log.assert_called_once_with(
        f"Using cached holidays from test_key. Path: {cache_manager_custom._path_cache_dir}",
        "info",
    )


def test_cache_df_decorator_miss(  # complexity-ok: ported verbatim
    cache_manager_custom: CacheManager, sample_dataframe: pd.DataFrame, mocker: MockerFixture
) -> None:
    """Test cache_df decorator with cache miss.

    Verifies
    --------
    - Function is called
    - Result is cached
    - Log message is recorded

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing
    mocker : MockerFixture
            Pytest-mock fixture for creating mocks

    Returns
    -------
    None
    """
    # one-assert-ok: ported verbatim; facets of one scenario, split tracked in the ledger
    mock_func = mocker.Mock(return_value=sample_dataframe)
    mock_log = mocker.patch.object(cache_manager_custom.cls_log_emitter, "log_message")

    class TestClass:
        """TestClass for testing cache_df decorator."""

        def __init__(self, cache_manager: CacheManager) -> None:
            """Initialize TestClass.

            Parameters
            ----------
            cache_manager : CacheManager
                    CacheManager instance

            Returns
            -------
            None
            """
            self.cls_cache_manager = cache_manager

        @CacheManager.cache_df("test_key")
        def dummy_func(
            self,
            *args: Any,  # noqa ANN401: typing.Any is not allowed
            **kwargs: Any,  # noqa ANN401: typing.Any is not allowed
        ) -> pd.DataFrame:
            """Implement dummy function for testing.

            Parameters
            ----------
            *args : Any
                    Variable-length argument list
            **kwargs : Any
                    Arbitrary keyword arguments

            Returns
            -------
            pd.DataFrame
                    Dummy DataFrame
            """
            return mock_func(self, *args, **kwargs)

    test_instance = TestClass(cache_manager_custom)
    cache_manager_custom.bool_reuse_cache = True
    result = test_instance.dummy_func()
    assert result.equals(sample_dataframe)
    mock_func.assert_called_once()
    mock_log.assert_called()


def test_cache_df_no_cls_cache_manager() -> None:  # complexity-ok: ported verbatim
    """Test cache_df decorator without cls_cache_manager attribute.

    Verifies
    --------
    - AttributeError is raised when cls_cache_manager is missing

    Returns
    -------
    None
    """

    class DummyClass:
        """Dummy class for testing."""

        pass

    dummy = DummyClass()

    @CacheManager.cache_df("test_key")
    def dummy_func(
        self: Any,  # noqa ANN401: typing.Any is not allowed
        *args: Any,  # noqa ANN401: typing.Any is not allowed
        **kwargs: Any,  # noqa ANN401: typing.Any is not allowed
    ) -> pd.DataFrame:
        """Implement dummy function for testing.

        Parameters
        ----------
        *args : Any
                Variable-length argument list
        **kwargs : Any
                Arbitrary keyword arguments

        Returns
        -------
        pd.DataFrame
                Dummy DataFrame
        """
        return pd.DataFrame()

    with pytest.raises(AttributeError, match="Instance must have 'cls_cache_manager' attribute"):
        dummy_func(dummy)


def test_load_cache_in_memory(
    cache_manager_default: CacheManager, sample_dataframe: pd.DataFrame
) -> None:
    """Test _load_cache from in-memory cache.

    Verifies
    --------
    - In-memory cache returns correct DataFrame
    - Persist cache is disabled

    Parameters
    ----------
    cache_manager_default : CacheManager
            CacheManager instance with default settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing

    Returns
    -------
    None
    """
    cache_manager_default.bool_persist_cache = False
    cache_manager_default._cache["test_key"] = sample_dataframe
    result = cache_manager_default._load_cache("test_key")
    assert result.equals(sample_dataframe)


def test_load_cache_from_file(
    cache_manager_custom: CacheManager, sample_dataframe: pd.DataFrame, tmp_path: Path
) -> None:
    """Test _load_cache from disk file.

    Verifies
    --------
    - DataFrame is loaded from file
    - File timestamp is valid
    - Valid DataFrame is returned

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing
    tmp_path : Path
            Temporary directory path for testing

    Returns
    -------
    None
    """
    cache_file = cache_manager_custom._get_cache_file_path("test_key")
    CacheManager._write_cache_file(cache_file, datetime.now(), sample_dataframe)

    result = cache_manager_custom._load_cache("test_key")
    assert result.equals(sample_dataframe)


def test_load_cache_expired(
    cache_manager_custom: CacheManager, sample_dataframe: pd.DataFrame, mocker: MockerFixture
) -> None:
    """Test _load_cache with expired cache file.

    Verifies
    --------
    - Expired cache file is deleted
    - None is returned

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing
    mocker : MockerFixture
            Pytest-mock fixture for creating mocks

    Returns
    -------
    None
    """
    # one-assert-ok: ported verbatim; facets of one scenario, split tracked in the ledger
    cache_file = cache_manager_custom._get_cache_file_path("test_key")
    past_time = datetime.now() - timedelta(days=2)
    CacheManager._write_cache_file(cache_file, past_time, sample_dataframe)

    cache_manager_custom.timedelta_cache_expiry = timedelta(days=1)
    result = cache_manager_custom._load_cache("test_key")
    assert result is None
    assert not cache_file.exists()


def test_load_cache_invalid_file(
    cache_manager_custom: CacheManager, mocker: MockerFixture
) -> None:
    """Test _load_cache with invalid cache file.

    Verifies
    --------
    - An unreadable cache file is treated as a miss (returns None), not a crash
    - The unreadable file is discarded

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    mocker : MockerFixture
            Pytest-mock fixture for creating mocks

    Returns
    -------
    None
    """
    # one-assert-ok: ported verbatim; facets of one scenario, split tracked in the ledger
    cache_file = cache_manager_custom._get_cache_file_path("test_key")
    with open(cache_file, "wb") as f:
        f.write(b"not json")

    assert cache_manager_custom._load_cache("test_key") is None
    assert not cache_file.exists()


def test_get_cache_file_path_sanitization(cache_manager_default: CacheManager) -> None:
    """Test _get_cache_file_path with special characters in key.

    Verifies
    --------
    - Special characters are replaced with underscores
    - Valid Path object is returned

    Parameters
    ----------
    cache_manager_default : CacheManager
            CacheManager instance with default settings

    Returns
    -------
    None
    """
    key = "test@#$%^&*key"
    result = cache_manager_default._get_cache_file_path(key)
    assert result.name == "test_______key.json"


@pytest.mark.parametrize(
    "invalid_df",
    [None, "", pd.DataFrame()],
    ids=["none", "string", "empty_df"],
)
def test_validate_cached_dataframe_invalid(  # complexity-ok: ported verbatim
    cache_manager_default: CacheManager,
    invalid_df: Any,  # noqa ANN401: typing.Any is not allowed
) -> None:
    """Test _validate_cached_dataframe with invalid inputs.

    Parameters
    ----------
    cache_manager_default : CacheManager
            CacheManager instance with default settings
    invalid_df : Any
            Invalid DataFrame values

    Verifies
    --------
    - Invalid inputs return False or raise TypeError

    Returns
    -------
    None
    """
    # one-assert-ok: ported verbatim; facets of one scenario, split tracked in the ledger
    if invalid_df is None or isinstance(invalid_df, str):
        with pytest.raises(TypeError, match="violates type hint"):
            cache_manager_default._validate_cached_dataframe(invalid_df)
    else:
        assert cache_manager_default._validate_cached_dataframe(invalid_df) is False


def test_validate_cached_dataframe_valid(
    cache_manager_default: CacheManager, sample_dataframe: pd.DataFrame
) -> None:
    """Test _validate_cached_dataframe with valid DataFrame.

    Verifies
    --------
    - Valid DataFrame returns True

    Parameters
    ----------
    cache_manager_default : CacheManager
            CacheManager instance with default settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing

    Returns
    -------
    None
    """
    assert cache_manager_default._validate_cached_dataframe(sample_dataframe) is True


def test_save_cache_in_memory(
    cache_manager_default: CacheManager, sample_dataframe: pd.DataFrame
) -> None:
    """Test _save_cache to in-memory cache.

    Verifies
    --------
    - DataFrame is saved to in-memory cache
    - No disk operation when persist_cache is False

    Parameters
    ----------
    cache_manager_default : CacheManager
            CacheManager instance with default settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing

    Returns
    -------
    None
    """
    cache_manager_default.bool_persist_cache = False
    cache_manager_default._save_cache("test_key", sample_dataframe)
    assert cache_manager_default._cache["test_key"].equals(sample_dataframe)


def test_save_cache_to_disk(
    cache_manager_custom: CacheManager, sample_dataframe: pd.DataFrame
) -> None:
    """Test _save_cache to disk file.

    Verifies
    --------
    - DataFrame is saved to disk
    - File exists and contains valid data

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing

    Returns
    -------
    None
    """
    # one-assert-ok: ported verbatim; facets of one scenario, split tracked in the ledger
    cache_manager_custom._save_cache("test_key", sample_dataframe)
    cache_file = cache_manager_custom._get_cache_file_path("test_key")
    assert cache_file.exists()
    creation_time, saved_df = CacheManager._read_cache_file(cache_file)
    assert saved_df.equals(sample_dataframe)
    assert isinstance(creation_time, datetime)


def test_save_cache_invalid_df(cache_manager_custom: CacheManager, mocker: MockerFixture) -> None:
    """Test _save_cache with invalid DataFrame.

    Verifies
    --------
    - Invalid DataFrame does not save
    - No file is created

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    mocker : MockerFixture
            Pytest-mock fixture for creating mocks

    Returns
    -------
    None
    """
    # one-assert-ok: ported verbatim; facets of one scenario, split tracked in the ledger
    mocker.patch.object(CacheManager, "_validate_cached_dataframe", return_value=False)
    cache_manager_custom._save_cache("test_key", pd.DataFrame())
    assert "test_key" not in cache_manager_custom._cache
    assert not cache_manager_custom._get_cache_file_path("test_key").exists()


def test_clean_old_cache(
    cache_manager_custom: CacheManager, sample_dataframe: pd.DataFrame, mocker: MockerFixture
) -> None:
    """Test _clean_old_cache removes expired files.

    Verifies
    --------
    - Expired cache files are deleted
    - Valid files remain

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing
    mocker : MockerFixture
            Pytest-mock fixture for creating mocks

    Returns
    -------
    None
    """
    cache_file = cache_manager_custom._get_cache_file_path("test_key")
    CacheManager._write_cache_file(
        cache_file, datetime.now() - timedelta(days=31), sample_dataframe
    )

    cache_manager_custom.timedelta_cache_ttl_days = timedelta(days=30)
    cache_manager_custom._clean_old_cache()
    assert not cache_file.exists()


def test_clean_old_cache_no_persist(
    cache_manager_custom: CacheManager, sample_dataframe: pd.DataFrame
) -> None:
    """Test _clean_old_cache with persist_cache disabled.

    Verifies
    --------
    - An expired cache file is left in place when persist_cache is False

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with a temporary cache directory
    sample_dataframe : pd.DataFrame
            Sample DataFrame to pickle into the expired cache file

    Returns
    -------
    None
    """
    cache_file = cache_manager_custom._get_cache_file_path("old_key")
    CacheManager._write_cache_file(
        cache_file, datetime.now() - timedelta(days=31), sample_dataframe
    )

    cache_manager_custom.bool_persist_cache = False
    cache_manager_custom.timedelta_cache_ttl_days = timedelta(days=30)
    cache_manager_custom._clean_old_cache()
    assert cache_file.exists()


def test_clear_caches_in_memory(
    cache_manager_default: CacheManager, sample_dataframe: pd.DataFrame
) -> None:
    """Test clear_caches clears in-memory cache.

    Verifies
    --------
    - In-memory cache is cleared

    Parameters
    ----------
    cache_manager_default : CacheManager
            CacheManager instance with default settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing

    Returns
    -------
    None
    """
    cache_manager_default._cache["test_key"] = sample_dataframe
    cache_manager_default.clear_caches()
    assert len(cache_manager_default._cache) == 0


def test_clear_caches_disk(
    cache_manager_custom: CacheManager, sample_dataframe: pd.DataFrame
) -> None:
    """Test clear_caches clears disk cache.

    Verifies
    --------
    - Disk cache files are deleted

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing

    Returns
    -------
    None
    """
    cache_file = cache_manager_custom._get_cache_file_path("test_key")
    CacheManager._write_cache_file(cache_file, datetime.now(), sample_dataframe)

    cache_manager_custom.clear_caches()
    assert not cache_file.exists()


def test_clear_caches_file_error(
    cache_manager_custom: CacheManager, mocker: MockerFixture
) -> None:
    """Test clear_caches handles file deletion errors.

    Verifies
    --------
    - ValueError is raised for file deletion errors

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    mocker : MockerFixture
            Pytest-mock fixture for creating mocks

    Returns
    -------
    None
    """
    cache_file = cache_manager_custom._get_cache_file_path("test_key")
    cache_file.touch()
    mocker.patch.object(Path, "unlink", side_effect=OSError("Permission denied"))

    with pytest.raises(ValueError, match="Failed to clear cache file"):
        cache_manager_custom.clear_caches()


def test_empty_key_cache_df(  # complexity-ok: ported verbatim
    cache_manager_custom: CacheManager,
) -> None:
    """Test cache_df decorator with empty key.

    Verifies
    --------
    - Empty key is handled correctly
    - Cache file is created with sanitized name

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings

    Returns
    -------
    None
    """

    @CacheManager.cache_df("")
    # one-assert-ok: ported verbatim; facets of one scenario, split tracked in the ledger
    def dummy_func(
        self: Any,  # noqa ANN401: typing.Any is not allowed
        *args: Any,  # noqa ANN401: typing.Any is not allowed
        **kwargs: Any,  # noqa ANN401: typing.Any is not allowed
    ) -> pd.DataFrame:
        """Implement dummy function for testing.

        Parameters
        ----------
        *args : Any
                Variable-length argument list
        **kwargs : Any
                Arbitrary keyword arguments

        Returns
        -------
        pd.DataFrame
                Dummy DataFrame
        """
        return pd.DataFrame({"A": [1]})

    cache_manager_custom.cls_cache_manager = cache_manager_custom
    result = dummy_func(cache_manager_custom)
    assert not result.empty
    cache_file = cache_manager_custom._get_cache_file_path("")
    assert cache_file.name == ".json"


def test_unicode_key(cache_manager_custom: CacheManager, sample_dataframe: pd.DataFrame) -> None:
    """Test cache operations with Unicode key.

    Verifies
    --------
    - Unicode characters in key are sanitized
    - Cache operations work correctly

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing

    Returns
    -------
    None
    """
    # one-assert-ok: ported verbatim; facets of one scenario, split tracked in the ledger
    key = "test_日本語_🚀"
    cache_manager_custom._save_cache(key, sample_dataframe)
    cache_file = cache_manager_custom._get_cache_file_path(key)
    assert cache_file.exists()
    assert cache_file.name == "test_日本語__.json"


def test_default_emitter_is_rich_and_prints_context(capsys: pytest.CaptureFixture[str]) -> None:
    """Test the default log sink is the rich LogsEmitter and prints a contextual line.

    Guards the shipped default: with no logger injected, CacheManager must default to
    ``LogsEmitter`` (not the bare base ``LogEmitter``) so screen output carries a timestamp,
    the level, and reconstructed ``{Class} [method]`` caller context — rather than the bare
    ``[INFO] message`` of the base seam.

    Parameters
    ----------
    capsys : pytest.CaptureFixture[str]
            Pytest capture fixture for stdout/stderr.

    Returns
    -------
    None
    """
    # one-assert-ok: ported verbatim; facets of one scenario, split tracked in the ledger
    cls_cache_manager = CacheManager(bool_persist_cache=False, bool_reuse_cache=False)
    assert isinstance(cls_cache_manager.cls_log_emitter, LogsEmitter)

    cls_cache_manager.cls_log_emitter.log_message("hello world", "info")
    str_out = capsys.readouterr().out

    assert re.search(r"\d{4}-\d{2}-\d{2},\d{2}:\d{2}:\d{2}\.\d{3} INFO ", str_out)
    assert "{" in str_out
    assert "[" in str_out
    assert "hello world" in str_out
    assert "[INFO] hello world" not in str_out


def test_cache_round_trip_preserves_frame_and_timestamp(
    cache_manager_custom: CacheManager, sample_dataframe: pd.DataFrame
) -> None:
    """Test a DataFrame and its creation timestamp survive a disk round trip.

    Verifies
    --------
    - The frame read back equals the frame written
    - The creation timestamp is preserved exactly

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing

    Returns
    -------
    None
    """
    # one-assert-ok: facets of one round trip
    created = datetime(2026, 1, 2, 3, 4, 5)
    path_file = cache_manager_custom._get_cache_file_path("round_trip")
    df_ = sample_dataframe.assign(day=pd.Timestamp("2026-01-01"))
    CacheManager._write_cache_file(path_file, created, df_)
    created_back, df_back = CacheManager._read_cache_file(path_file)
    assert created_back == created
    pd.testing.assert_frame_equal(df_back, df_)


@pytest.mark.parametrize(
    "df_",
    [
        pd.DataFrame({0: [1, 2], 1: ["a", "b"]}),
        pd.DataFrame({"updated_at": pd.to_datetime(["2026-01-01 10:00:00.123456"], utc=True)}),
        pd.DataFrame({"v": [1]}, index=pd.DatetimeIndex(["2026-01-02"], name="day")),
    ],
    ids=["integer-column-labels", "microsecond-timestamps", "named-datetime-index"],
)
def test_cache_round_trip_preserves_labels_precision_and_index(
    cache_manager_custom: CacheManager, df_: pd.DataFrame
) -> None:
    """Test frames that broke the first JSON format survive a disk round trip.

    Verifies
    --------
    - Integer column labels, microsecond timestamps and a named DatetimeIndex
      read back equal to what was written

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    df_ : pd.DataFrame
            Frame to round-trip

    Returns
    -------
    None
    """
    path_file = cache_manager_custom._get_cache_file_path("round_trip_shapes")
    CacheManager._write_cache_file(path_file, datetime(2026, 1, 2), df_)
    pd.testing.assert_frame_equal(CacheManager._read_cache_file(path_file)[1], df_)


def test_stray_pkl_is_never_loaded(
    cache_manager_custom: CacheManager, sample_dataframe: pd.DataFrame
) -> None:
    """Test a legacy .pkl file is ignored, not unpickled.

    Verifies
    --------
    - The load is a miss even though a .pkl exists for the key
    - The .pkl file is left untouched on disk

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing

    Returns
    -------
    None
    """
    # one-assert-ok: facets of one scenario
    stray = cache_manager_custom._get_cache_file_path("legacy").with_suffix(".pkl")
    stray.write_bytes(b"would execute if unpickled")
    assert cache_manager_custom._load_cache("legacy") is None
    cache_manager_custom._clean_old_cache()
    cache_manager_custom.clear_caches()
    assert stray.exists()


def test_load_cache_in_memory_expired_is_a_miss(
    cache_manager_custom: CacheManager, sample_dataframe: pd.DataFrame
) -> None:
    """Test an in-memory entry older than the expiry is not served.

    Verifies
    --------
    - A stale in-memory entry returns None when persistence is off

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing

    Returns
    -------
    None
    """
    cache_manager_custom.bool_persist_cache = False
    cache_manager_custom._cache["old"] = sample_dataframe
    cache_manager_custom._cache_created["old"] = datetime.now() - timedelta(days=400)
    assert (
        cache_manager_custom._load_cache("old"),
        "old" in cache_manager_custom._cache,
        "old" in cache_manager_custom._cache_created,
    ) == (None, False, False)


def test_save_cache_write_failure_is_logged_not_raised(
    cache_manager_custom: CacheManager,
    sample_dataframe: pd.DataFrame,
    mocker: MockerFixture,
) -> None:
    """Test a failed disk write does not abort the caller.

    Verifies
    --------
    - The failure is logged as a warning and the frame stays in memory

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings
    sample_dataframe : pd.DataFrame
            Sample DataFrame for testing
    mocker : MockerFixture
            Pytest-mock fixture for creating mocks

    Returns
    -------
    None
    """
    mocker.patch.object(CacheManager, "_write_cache_file", side_effect=PermissionError("ro"))
    spy_log = mocker.spy(cache_manager_custom.cls_log_emitter, "log_message")
    cache_manager_custom._save_cache("key", sample_dataframe)
    assert (spy_log.call_args.args[1], "key" in cache_manager_custom._cache) == ("warning", True)


def test_clean_old_cache_corrupt_file_is_removed_not_raised(
    cache_manager_custom: CacheManager,
) -> None:
    """Test a corrupt cache file is deleted without raising.

    Verifies
    --------
    - The corrupt file is gone after cleaning

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings

    Returns
    -------
    None
    """
    path_bad = cache_manager_custom._get_cache_file_path("bad")
    path_bad.write_text("{not json", encoding="utf-8")
    cache_manager_custom._clean_old_cache()
    assert not path_bad.exists()


def test_init_without_persistence_creates_no_directory(
    tmp_path: Path,
) -> None:
    """Test an in-memory manager does not touch the disk.

    Verifies
    --------
    - The cache directory is not created when persistence is off

    Parameters
    ----------
    tmp_path : Path
            Temporary directory path for testing

    Returns
    -------
    None
    """
    path_dir = tmp_path / "never_created"
    CacheManager(bool_persist_cache=False, path_cache_dir=str(path_dir))
    assert not path_dir.exists()


def test_cache_round_trip_preserves_provider_shaped_frame(
    cache_manager_custom: CacheManager,
) -> None:
    """Test the raw frames providers cache (strings and ints) survive a round trip.

    Verifies
    --------
    - Object-dtype string dates and integer years read back equal

    Parameters
    ----------
    cache_manager_custom : CacheManager
            CacheManager instance with custom settings

    Returns
    -------
    None
    """
    df_ = pd.DataFrame({"DATE": ["01/01/2026", "25/12/2026"], "ANO": [2026, 2026]})
    path_file = cache_manager_custom._get_cache_file_path("provider_shape")
    CacheManager._write_cache_file(path_file, datetime(2026, 1, 2), df_)
    pd.testing.assert_frame_equal(CacheManager._read_cache_file(path_file)[1], df_)


def test_init_accepts_a_path_object_for_the_cache_directory(tmp_path: Path) -> None:
    """Test ``path_cache_dir`` takes a ``Path``, as the docs and the naming convention imply.

    Verifies
    --------
    - The resolved cache directory equals the Path passed in

    Parameters
    ----------
    tmp_path : Path
            Temporary directory path for testing

    Returns
    -------
    None
    """
    assert CacheManager(path_cache_dir=tmp_path / "c")._path_cache_dir == tmp_path / "c"
