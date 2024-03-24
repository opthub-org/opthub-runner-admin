"""The module provides a class to handle the cache file for the score calculation."""

import pickle
import shutil
import tempfile
from pathlib import Path

from opthub_runner.lib.scorer_history import Trial


class Cache:
    """The class to handle the cache file for the score calculation."""

    def __init__(self) -> None:
        """Initialize the cache class."""
        self.__loaded_filename: str | None = None  # 現在読み込んでいるキャッシュのファイル名
        self.__values: list[Trial] | None = None  # 現在持っているキャッシュの値

        # キャッシュ保管用のディレクトリを作っておく
        temp_dir = tempfile.gettempdir()
        self.__cache_dir_path = Path(temp_dir) / "cache"
        if Path.exists(self.__cache_dir_path):
            shutil.rmtree(self.__cache_dir_path)
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
        """
        このキャッシュのデータを削除する．

        """
        if self.__loaded_filename is not None and not Path.exists(
            Path(self.__cache_dir_path) / Path(self.__loaded_filename + ".pkl"),
        ):
            Path.unlink(Path(self.__cache_dir_path) / Path(self.__loaded_filename + ".pkl"))
        self.__loaded_filename = None
        self.__values = None
