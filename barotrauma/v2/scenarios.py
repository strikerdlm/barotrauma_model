"""
barotrauma.v2.scenarios
=======================

Preset ChamberProfile instances covering the most common hypobaric-chamber
training protocols. All profiles follow the ``ChamberProfile`` dataclass
contract from ``types.py``.

Published / reference protocols:
- USAFSAM Type I 25,000 ft (Garrett & Bradshaw 1990; FAA Ten-Year Survey,
  Valdez 1977 DTIC ADA037235): ~2,000 ft/min ascent, ~5,000 ft/min descent.
- USAFSAM Type II / RD 35,000 ft: rapid decompression with instantaneous
  step then controlled descent.
- Israeli AF post-2022 (Nakdimon PMID 36309795): 45-min preoxygenation,
  max ascent 3,000 ft/min, max altitude 25,000 ft.
- FAC (Colombia, DIMAE): chamber sited at Bogotá (~8,530 ft / 2,600 m).
  Profile details unpublished; representative below based on typical
  Latin American AF protocol parameters.
- Commercial cabin descent: ~600 ft/min from 8,000 ft cabin altitude
  (Kanick-Doyle 2005 baseline).
"""

from __future__ import annotations

from .types import ChamberProfile, ChamberSegment


# ---------------------------------------------------- USAFSAM Type I ---
USAFSAM_TYPE_I = ChamberProfile(
    name="USAFSAM Type I (25,000 ft)",
    start_altitude_ft=0.0,
    segments=(
        ChamberSegment(duration_s=750, end_altitude_ft=25000, label="ascent 2000 ft/min"),
        ChamberSegment(duration_s=900, end_altitude_ft=25000, label="hold 15 min"),
        ChamberSegment(duration_s=300, end_altitude_ft=0, label="descent 5000 ft/min"),
    ),
)

# ---------------------------------------------------- USAFSAM Type II --
USAFSAM_TYPE_II_RD = ChamberProfile(
    name="USAFSAM Type II — Rapid Decompression",
    start_altitude_ft=8000.0,
    segments=(
        # Pre-RD hold at 8,000 ft cabin altitude for 10 min
        ChamberSegment(duration_s=600, end_altitude_ft=8000, label="cabin hold"),
        # Instantaneous (1 s) decompression to 35,000 ft
        ChamberSegment(duration_s=1.0, end_altitude_ft=35000, label="RD event (1 s)"),
        # 5 min at altitude
        ChamberSegment(duration_s=300, end_altitude_ft=35000, label="35k ft exposure"),
        # Controlled descent 5,000 ft/min
        ChamberSegment(duration_s=420, end_altitude_ft=0, label="descent 5000 ft/min"),
    ),
)

# ---------------------------------------------- Israeli AF post-2022 --
ISRAELI_AF_POST_2022 = ChamberProfile(
    name="Israeli AF 2022+ (Nakdimon PMID 36309795)",
    start_altitude_ft=0.0,
    segments=(
        ChamberSegment(duration_s=2700, end_altitude_ft=0, label="45-min preoxygenation"),
        ChamberSegment(duration_s=500, end_altitude_ft=25000, label="ascent 3000 ft/min"),
        ChamberSegment(duration_s=600, end_altitude_ft=25000, label="hold 10 min"),
        ChamberSegment(duration_s=500, end_altitude_ft=0, label="descent 3000 ft/min"),
    ),
)

# ------------------------------------------------------ FAC (Colombia) -
# Starts at Bogotá elevation (~8,530 ft / 2,600 m). Descent returns to Bogotá,
# not sea level. Profile parameters are representative, not official.
FAC_BOGOTA_DEFAULT = ChamberProfile(
    name="FAC Bogotá default (DIMAE chamber, 8,530 ft start)",
    start_altitude_ft=8530.0,
    segments=(
        ChamberSegment(duration_s=600, end_altitude_ft=25000, label="ascent 1650 ft/min"),
        ChamberSegment(duration_s=900, end_altitude_ft=25000, label="hold 15 min"),
        ChamberSegment(duration_s=400, end_altitude_ft=8530, label="descent 2470 ft/min"),
    ),
)

# -------------------------------------------- Commercial cabin descent -
COMMERCIAL_CABIN_DESCENT = ChamberProfile(
    name="Commercial cabin descent (Kanick-Doyle 2005 reference)",
    start_altitude_ft=8000.0,
    segments=(
        ChamberSegment(duration_s=800, end_altitude_ft=0, label="descent 600 ft/min"),
    ),
)

# ---------------------------------------- Worst-case chamber descent ---
RAPID_DESCENT_10K_FT_MIN = ChamberProfile(
    name="Rapid descent 10,000 ft/min (stress test)",
    start_altitude_ft=25000.0,
    segments=(
        ChamberSegment(duration_s=150, end_altitude_ft=0, label="descent 10,000 ft/min"),
    ),
)

# -------------------------------------------- Slow descent 1000 ft/min -
SLOW_DESCENT_1K_FT_MIN = ChamberProfile(
    name="Slow descent 1,000 ft/min (best-case)",
    start_altitude_ft=25000.0,
    segments=(
        ChamberSegment(duration_s=1500, end_altitude_ft=0, label="descent 1,000 ft/min"),
    ),
)

# ------------------------------------ Italian AF (Morgagni / Landolfi) -
# Standard Italian Air Force chamber training. Morgagni 2010 PMID 20824995
# used a "standard high-altitude profile" (25,000 ft); Morgagni 2012 PMID
# 22764614 reported both 25,000 ft and 35,000 ft profiles. Landolfi 2009
# PMID 20027855 used 25,000 ft Italian AF training. Exact profile params
# are not published verbatim; these reconstructions match the published
# envelope (pre-oxygenation, moderate ascent, 15-min hold, controlled
# descent ≤ 3,000 ft/min).
ITALIAN_AF_25K = ChamberProfile(
    name="Italian AF 25,000 ft (Morgagni 2010/2012, Landolfi 2009)",
    start_altitude_ft=0.0,
    segments=(
        ChamberSegment(duration_s=1800, end_altitude_ft=0,
                       label="30-min O2 preoxygenation"),
        ChamberSegment(duration_s=750, end_altitude_ft=25000,
                       label="ascent 2,000 ft/min"),
        ChamberSegment(duration_s=900, end_altitude_ft=25000,
                       label="hold 15 min"),
        ChamberSegment(duration_s=500, end_altitude_ft=0,
                       label="descent 3,000 ft/min"),
    ),
)

ITALIAN_AF_35K = ChamberProfile(
    name="Italian AF 35,000 ft (Morgagni 2012)",
    start_altitude_ft=0.0,
    segments=(
        ChamberSegment(duration_s=1800, end_altitude_ft=0,
                       label="30-min O2 preoxygenation"),
        ChamberSegment(duration_s=1050, end_altitude_ft=35000,
                       label="ascent 2,000 ft/min"),
        ChamberSegment(duration_s=300, end_altitude_ft=35000,
                       label="hold 5 min"),
        ChamberSegment(duration_s=700, end_altitude_ft=0,
                       label="descent 3,000 ft/min"),
    ),
)

# ---------------------------- Groth 1986 pressure-chamber (Kanick-Doyle validation) -
GROTH_1986_VALIDATION = ChamberProfile(
    name="Groth 1986 pressure chamber (Kanick-Doyle validation)",
    start_altitude_ft=0.0,
    segments=(
        # Ascent to 8000 ft equivalent at 1920 ft/min over 25 s
        ChamberSegment(duration_s=25, end_altitude_ft=800.0, label="ascent 1920 ft/min, 25 s"),
        ChamberSegment(duration_s=30, end_altitude_ft=800.0, label="hold"),
        ChamberSegment(duration_s=25, end_altitude_ft=0.0, label="descent 1920 ft/min"),
    ),
)


PRESETS: dict[str, ChamberProfile] = {
    "usafsam_type_i": USAFSAM_TYPE_I,
    "usafsam_type_ii_rd": USAFSAM_TYPE_II_RD,
    "israeli_af_post_2022": ISRAELI_AF_POST_2022,
    "italian_af_25k": ITALIAN_AF_25K,
    "italian_af_35k": ITALIAN_AF_35K,
    "fac_bogota_default": FAC_BOGOTA_DEFAULT,
    "commercial_cabin_descent": COMMERCIAL_CABIN_DESCENT,
    "rapid_descent_10k": RAPID_DESCENT_10K_FT_MIN,
    "slow_descent_1k": SLOW_DESCENT_1K_FT_MIN,
    "groth_1986": GROTH_1986_VALIDATION,
}


def get_profile(name: str) -> ChamberProfile:
    """Lookup a preset profile by key."""
    if name not in PRESETS:
        raise KeyError(f"unknown profile '{name}' — available: {sorted(PRESETS)}")
    return PRESETS[name]
