"""
barotrauma.utils — compatibility shim redirecting to barotrauma.legacy.utils.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "barotrauma.utils is a compatibility shim; the implementation has been "
    "moved to barotrauma.legacy.utils.",
    DeprecationWarning,
    stacklevel=2,
)

import sys as _sys


def _alias(name: str) -> None:
    try:
        mod = __import__(f"barotrauma.legacy.utils.{name}", fromlist=[name])
        globals()[name] = mod
        _sys.modules[f"barotrauma.utils.{name}"] = mod
    except Exception:  # pragma: no cover
        pass


for _n in ("plot_et", "plot_risk", "sensitivity_analyzer"):
    _alias(_n)

del _alias, _sys
