"""The module provides a class to handle the cache file for the score calculation."""

import pickle
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
        if self.__values is None:
            msg = "No file loaded."
            raise ValueError(msg)

        self.__values.append(value)

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

        if self.__loaded_filename is not None:
            with Path.open(Path(self.__cache_dir_path) / Path(self.__loaded_filename + ".pkl"), "wb") as file:
                pickle.dump(self.__values, file)

        self.__loaded_filename = filename
        self.__values = []
        if Path.exists(Path(self.__cache_dir_path) / Path(self.__loaded_filename + ".pkl")):
            with Path.open(Path(self.__cache_dir_path) / Path(self.__loaded_filename + ".pkl"), "rb") as file:
                self.__values = pickle.load(file)

    def clear(self) -> None:
        """Clear the cache."""
        if self.__loaded_filename is not None and not Path.exists(
            Path(self.__cache_dir_path) / Path(self.__loaded_filename + ".pkl"),
        ):
            Path.unlink(Path(self.__cache_dir_path) / Path(self.__loaded_filename + ".pkl"))
        self.__loaded_filename = None
        self.__values = None
