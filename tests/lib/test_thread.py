"""This module tests the thread module."""

from time import sleep, time
from typing import Any

from opthub_runner.lib.thread import StoppableThread


def test_stoppable_thread() -> None:
    """Test StoppableThread class."""

    def target() -> None:
        """The target function."""
        sleep(5)

    thread = StoppableThread(target, ())
    start = time()
    thread.start()
    thread.join()
    joined = time()
    print(joined - start)


def test_stoppable_thread_with_stop() -> None:
    """Test StoppableThread class."""

    class TestClass:
        """Test class."""

        def __init__(self, args: tuple[Any, ...]) -> None:
            """Initialize the class."""
            self.args = args
            self.thread: StoppableThread | None = None

        def target(self, sleep_time: int) -> None:
            """The target function."""
            while True:
                if self.thread is None:
                    msg = "The thread is None."
                    raise ValueError(msg)
                if self.thread.is_stop_requested():
                    print("The stoppable thread is stopped.")
                    break
                print("The stoppable thread is running.")
                sleep(sleep_time)

        def start(self) -> None:
            self.thread = StoppableThread(self.target, self.args)
            self.thread.start()

        def stop(self) -> None:
            if self.thread is None:
                msg = "The thread is None."
                raise ValueError(msg)
            self.thread.stop()
            self.thread.join()

    sleep_time = 3
    test_class = TestClass((sleep_time,))

    start = time()
    test_class.start()
    print("The main thread is running.")
    sleep(11)
    print("The main thread makes the stop request.")
    sleep(1)
    test_class.stop()
    joined = time()
    print(joined - start)
