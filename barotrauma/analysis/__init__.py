"""
barotrauma.analysis — compatibility shim redirecting to barotrauma.legacy.analysis.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "barotrauma.analysis is a compatibility shim; the implementation has been "
    "moved to barotrauma.legacy.analysis. New code should use barotrauma.v2.",
    DeprecationWarning,
    stacklevel=2,
)

import sys as _sys


def _alias(name: str) -> None:
    try:
        mod = __import__(f"barotrauma.legacy.analysis.{name}", fromlist=[name])
        globals()[name] = mod
        _sys.modules[f"barotrauma.analysis.{name}"] = mod
    except Exception:  # pragma: no cover
        pass


for _n in ("enhanced_visualization", "statistics", "visualization"):
    _alias(_n)

del _alias, _sys
