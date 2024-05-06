"""Thread class with a stop() method."""

import threading
from collections.abc import Callable
from typing import Any


class StoppableThread(threading.Thread):
    """Thread class with a stop() method."""

    def __init__(self, target: Callable[..., Any], args: tuple[Any, ...]) -> None:
        """Initialize the thread."""
        super().__init__()
        self.__stop_requested = False
        self.target = target
        self.args = args

    def start(self) -> None:
        """Start the thread."""
        super().start()
        self.__stop_requested = False

    def run(self) -> None:
        """Run the thread."""
        if self.__stop_requested:
            msg = "The thread is requested to stop."
            raise RuntimeError(msg)
        super().run()
        self.target(*self.args)

    def stop(self) -> None:
        """Stop the thread."""
        self.__stop_requested = True

    def is_stop_requested(self) -> bool:
        """Check if the thread is requested to stop.

        Returns:
            bool: True if the thread is requested to stop, False otherwise.
        """
        return self.__stop_requested
