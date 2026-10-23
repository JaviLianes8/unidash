r"""Fold Unicode dashes and punctuation to plain ASCII while leaving letters untouched.

The public names are listed in ``__all__``. ``DASHES`` is the set of every character with the
Unicode 18.0 Dash property, and ``Form`` is the type of the ``form`` argument: one of
``"ascii"``, ``"tex"`` or ``"typographic"``.

>>> import unidash
>>> len(unidash.DASHES), "-" in unidash.DASHES, "\u2014" in unidash.DASHES
(31, True, True)
>>> form: unidash.Form = "tex"
>>> unidash.fold_dashes("a\u2013b", form)
'a--b'
"""

from __future__ import annotations

from ._dashes import DASHES, dash_table, find_dashes, fold_dashes, is_dash, iter_fold_dashes
from ._fold import to_ascii_punct
from ._hit import DashHit
from ._tables import Form

__version__ = "1.0.0"

# DashHit shows and pickles as unidash.DashHit, so a pickle never depends on the private
# module that defines it.
DashHit.__module__ = __name__

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
