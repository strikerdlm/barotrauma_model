"""
barotrauma
==========

Physics-informed middle-ear barotrauma (MEB) risk model for hypobaric chamber
training and pressurized flight.

Two API surfaces are exposed:

* ``barotrauma.v2`` (default) — current model, calibrated to Colombian
  Aerospace Force (FAC) 10-year cohort (5.8% MEB prevalence, URI as the
  dominant modifiable risk factor). Physics core extends Kanick & Doyle 2005
  with Doyle 2017 species-resolved gas exchange, Alper 2020 Eustachian-tube
  parameter distributions, and a multi-state URI / Patulous ET pathophysiology
  module. See ``barotrauma.v2`` and ``docs/model_card.md``.

* ``barotrauma.legacy`` — frozen v1 stack (deterministic abstract model, no
  real-cohort calibration). Kept for reproducibility of prior analyses. Do
  not extend.

Quick start::

    from barotrauma.v2 import simulate, PatientState, ChamberProfile
    from barotrauma.v2.scenarios import USAFSAM_TYPE_I

    patient = PatientState(uri="none", pet="normal", et_dysfunction="mild")
    result = simulate(patient, USAFSAM_TYPE_I)
    print(result.risk.p_barotitis, result.risk.p_baromyringitis)

Author
------
Dr. Diego L. Malpica, MD — Aerospace Medicine, Colombia.
ORCID: https://orcid.org/0000-0002-2257-4940
"""

from __future__ import annotations

__version__ = "2.0.0"
__author__ = "Dr. Diego L. Malpica"
__email__ = "dlmalpica@yahoo.com"

from . import v2
from . import legacy

__all__ = ["v2", "legacy", "__version__"]
