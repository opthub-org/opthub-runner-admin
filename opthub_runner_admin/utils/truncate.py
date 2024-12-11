"""Truncate text utility functions for Opthub Runner Admin."""


def truncate_text_center(text: str, max_length: int, ellipsis: str = "\n... Content omitted for length ...\n") -> str:
    """Truncates text by removing content from the middle while preserving start and end portions.

    Args:
        text (str): The input text to truncate
        max_length (int): Maximum desired length of the output text
        ellipsis (str): Text to insert at truncation point (default shows content was omitted)

    Returns:
        str: Truncated text with ellipsis in the middle
    """
    if len(text) <= max_length:
        return text

    # Ensure max_length is large enough to show some content
    if max_length < len(ellipsis) + 4:
        message = "max_length must be at least length of ellipsis + 4 characters"
        raise ValueError(message)

    # Calculate available space for content
    available_length = max_length - len(ellipsis)

    # Calculate length for start and end portions
    start_length = available_length // 2
    end_length = available_length - start_length

    # Extract start and end portions
    start_text = text[:start_length].rstrip()
    end_text = text[-end_length:].lstrip()

    # Combine with ellipsis
    return f"{start_text}{ellipsis}{end_text}"
