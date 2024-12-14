"""The module provides a class to handle the cache file for the score calculation."""

import json
from pathlib import Path
from typing import TypedDict


class Trial(TypedDict):
    """The type of the trial. Conforming to Docker input by using snake case.

    trial_no (str): The trial number.
    objective (object | None): The objective value.
    constraint (object | None): The constraint value.
    info (object): The information.
    score (float): The score.
    feasible (bool | None): The feasibility.
    """

    trial_no: str
    objective: object | None
    constraint: object | None
    info: object
    score: float
    feasible: bool | None


class CacheWriteError(Exception):
    """Exception raised for errors in writing to the cache."""

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__("Failed to write to the cache.")


class CacheReadError(Exception):
    """Exception raised for errors in writing to the cache."""

    def __init__(self) -> None:
        """Initialize the exception."""
        super().__init__("Failed to read the cache.")


class Cache:
    """The class to handle the cache file for the score calculation."""

    def __init__(self) -> None:
        """Initialize the cache class."""
        self.__loaded_filename: str | None = None  # file name of the loaded cache
        self.__values: list[Trial] | None = None  # values in the cache

        # Create a directory for the cache
        home_dir = Path.home()

        # .opthub_runner_adminディレクトリのパスを作成
        opthub_runner_admin_dir = home_dir / ".opthub_runner_admin"

        # ディレクトリの存在をチェック
        if not opthub_runner_admin_dir.exists():
            Path.mkdir(opthub_runner_admin_dir)
        self.__cache_dir_path = Path(opthub_runner_admin_dir) / "cache"
        if not Path.exists(self.__cache_dir_path):
            Path.mkdir(self.__cache_dir_path)

    def append(self, value: Trial) -> None:
        """Append a value to the cache.

        Args:
            value (Trial): The value to append to the cache.

        Raises:
            ValueError: If no file is loaded, an error occurs.
        """
        if self.__values is None or self.__loaded_filename is None:
            msg = "No file loaded."
            raise ValueError(msg)

        try:
            with Path.open(self.__get_cache_path(), "a") as file:
                file.write(json.dumps(value) + "\n")
            self.__values.append(value)

        except Exception as e:
            raise CacheWriteError from e

    def get_values(self) -> list[Trial]:
        """Get the values in the cache.

        Returns:
            list[Trial]: The values in the cache.
        """
        if self.__values is None:
            msg = "No file loaded."
            raise ValueError(msg)
        return self.__values

    def load(self, filename: str) -> None:
        """Load the cache file.

        Args:
            filename (str): The filename to load.
        """
        if self.__loaded_filename is not None and filename == self.__loaded_filename:
            return

        self.__loaded_filename = filename
        self.__values = []

        try:
            if not Path.exists(self.__get_cache_path()):
                return
            with Path.open(self.__get_cache_path(), "r") as file:
                for line in file:
                    self.__values.append(json.loads(line))
        except Exception as e:
            raise CacheReadError from e

    def clear(self) -> None:
        """Clear the cache."""
        if self.__loaded_filename is not None and not Path.exists(self.__get_cache_path()):
            Path.unlink(self.__get_cache_path())
        self.__loaded_filename = None
        self.__values = None

    def __get_cache_path(self) -> Path:
        """Get the file path of the loaded cache.

        Returns:
            Path: The file path of the loaded cache.
        """
        if self.__loaded_filename is None:
            msg = "No file loaded."
            raise ValueError(msg)
        return Path(self.__cache_dir_path) / Path(self.__loaded_filename + ".jsonl")
