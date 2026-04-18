"""
barotrauma.models — compatibility shim for the v1 import path.

The pre-v2 implementation lived under ``barotrauma.models.*``. After the v2
rewrite these modules were relocated to ``barotrauma.legacy.models.*``.
This shim re-exports the legacy modules so pre-v2 code (Streamlit apps,
notebooks, external scripts) keeps working with a DeprecationWarning.

New code should import from ``barotrauma.v2`` directly.
"""

from __future__ import annotations

import warnings as _warnings

_warnings.warn(
    "barotrauma.models is a compatibility shim; the implementation has been "
    "moved to barotrauma.legacy.models. New code should use barotrauma.v2.",
    DeprecationWarning,
    stacklevel=2,
)

# Alias legacy modules under the old import path. Each is tried individually
# so that an optional-dependency failure (e.g. seaborn missing) in one module
# doesn't block the others. Submodule imports
# (``from barotrauma.models.chamber_risk import ...``) are supported via
# sys.modules aliasing.
import sys as _sys


def _alias(name: str) -> None:
    try:
        mod = __import__(f"barotrauma.legacy.models.{name}", fromlist=[name])
        globals()[name] = mod
        _sys.modules[f"barotrauma.models.{name}"] = mod
    except Exception:  # pragma: no cover - optional deps may be absent
        pass


for _n in (
    "chamber_risk",
    "clinical_risk",
    "flight_profile",
    "integrated_model",
    "ml_risk_model",
    "physiology",
    "valsalva_chamber_integration",
    "valsalva_video_analysis",
    "video_processor",
):
    _alias(_n)

del _alias, _sys
