"""
Tiny helper for asking the user a question on the command line.

Having this in one place means every command asks questions the exact
same way (and it's the one spot to change if we ever want to, say, add
readline history or validation).
"""


def prompt(message: str) -> str:
    """
    Ask the user a question and return their (whitespace-trimmed) answer.

    Args:
        message: Text shown right before the input cursor.

    Returns:
        The text the user typed, with leading/trailing whitespace removed.
    """

    return input(message).strip()
