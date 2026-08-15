"""
Single source of truth for the current Linksaver version number.

Kept in its own tiny module so that other files (and packaging tools such
as setup.py) can import the version without pulling in the rest of the
program.

NOTE: the variable name uses the unusual triple-underscore spelling
(___version___) on purpose - other modules already import it under this
exact name, so it is kept unchanged here to avoid breaking anything.
"""

___version___: str = "3.0.4"
