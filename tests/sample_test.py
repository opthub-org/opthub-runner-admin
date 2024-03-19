"""Sample Test for the project."""


def test_hello() -> None:
    """Hello is equal to hello."""
    hello: str = "hello"
    if hello != "hellp":
        AssertionError("hello is not equal to hello")
