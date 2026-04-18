"""
barotrauma.legacy
=================

Historical v1 implementation retained for reproducibility and back-compatibility.

This subpackage freezes the pre-2026-04 model stack that was superseded by
``barotrauma.v2``. Do not extend. Use ``barotrauma.v2`` for new work.

Legacy entry points kept importable so existing notebooks/scripts survive:

    from barotrauma.legacy.models.chamber_risk import (
        HypobaricChamberRiskModel, ChamberScenario,
    )

See MIGRATION.md for the v1→v2 mapping.
"""

from __future__ import annotations

__all__ = ["models", "analysis", "utils"]
