"""barotrauma.models.integrated_model

Compatibility wrapper.

The repository contains multiple historical model stacks. The maintained
integrated ML+physics implementation lives in `core.barotrauma_integrated_model`.
This module re-exports it under the `barotrauma.models` namespace to keep
imports stable.
"""

from __future__ import annotations

from core.barotrauma_integrated_model import IntegratedBarotraumaModel, SimulationResult

__all__ = ["IntegratedBarotraumaModel", "SimulationResult"]
