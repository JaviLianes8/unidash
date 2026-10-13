"""Fold Unicode dashes and punctuation to plain ASCII while leaving letters untouched."""

from __future__ import annotations

from ._dashes import DASHES, DashHit, find_dashes, fold_dashes, is_dash, iter_fold_dashes
from ._fold import to_ascii_punct
from ._tables import Form, dash_table

__version__ = "0.2.0"

__all__ = [
    "DASHES",
    "DashHit",
    "Form",
    "dash_table",
    "find_dashes",
    "fold_dashes",
    "is_dash",
    "iter_fold_dashes",
    "to_ascii_punct",
]
