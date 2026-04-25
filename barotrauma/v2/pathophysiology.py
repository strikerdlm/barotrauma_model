"""
barotrauma.v2.pathophysiology
=============================

URI / Patulous-ET / comorbidity state machine. Converts the qualitative
patient state into numeric modifiers applied to ET function during a
chamber exposure.

Sources:
- docs/research_notes/02_uri_et_dysfunction.md — URI modifier table, 9 states.
- docs/research_notes/03_patulous_et.md — Patulous ET 4-state model.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from . import constants as C
from .types import (
    ChronicRhinitis,
    EtFunction,
    MedicationEffect,
    PatientState,
    PetState,
    UriState,
)

if TYPE_CHECKING:  # pragma: no cover
    pass


# ------------------------------------------------------ modifier object -
@dataclass(frozen=True)
class Modifiers:
    """Multiplicative/additive modifiers assembled from URI + PET + comorbidity."""

    ra_mult: float = 1.0                 # on active resistance R_A
    passive_opening_shift_mmHg: float = 0.0
    pet_tissue_offset_mmHg: float = 0.0   # vs. ambient (positive = more obstructive)
    eq_rate_mult: float = 1.0             # catch-all on equalization efficacy
    valsalva_mult: float = 1.0
    per_descent_rr: float = 1.0           # prior on per-descent MEB RR
    # PET-state flags
    is_patulous_patent: bool = False     # S1 — continuously open
    patulous_unstable: bool = False       # S2 — paradoxical closure under inflammation
    habitual_sniffer_bias: bool = False   # S3 — sustained -ME pressure bias
    post_plug_stenotic: bool = False     # S4 — behaves like severe obstruction
    notes: tuple[str, ...] = ()


# ------------------------------------------------------- core builder --
def modifiers_for_patient(patient: PatientState) -> Modifiers:
    """
    Compose the patient's active modifier set from URI × PET × rhinitis × medication.

    URI and chronic rhinitis are multiplicative on RA; P_O' shifts add; MEB RRs
    multiply. PET state changes the *shape* of ET dynamics rather than just
    scaling RA, so its effects are flagged separately (handled in et_dynamics).
    """
    m = _uri_modifiers(patient.uri)
    m = _compose(m, _rhinitis_modifiers(patient.rhinitis))
    m = _compose(m, _pet_modifiers(patient.pet, uri=patient.uri,
                                   habitual_sniffer=patient.habitual_sniffer))
    m = _apply_medication(m, patient.medication, pet=patient.pet)
    m = _compose(m, _previous_meb_modifier(patient.previous_meb))
    m = _compose(m, _v23_covariate_modifiers(patient))
    m = _compose(m, _bdet_modifier(patient.bdet_treated, pet=patient.pet))
    return m


# --------------------------------------------------------- URI part ---
def _uri_modifiers(uri: UriState) -> Modifiers:
    row = C.URI_MODIFIERS[uri]
    if uri == "none":
        return Modifiers()
    return Modifiers(
        ra_mult=row["ra_mult"],
        passive_opening_shift_mmHg=row["po_shift_mmHg"],
        pet_tissue_offset_mmHg=row["pet_offset_mmHg"],
        eq_rate_mult=row["eq_rate_mult"],
        valsalva_mult=row["valsalva_mult"],
        per_descent_rr=row["meb_rr"],
        notes=(f"URI {uri}: RA×{row['ra_mult']:.1f}, MEB RR×{row['meb_rr']:.1f}",),
    )


def _rhinitis_modifiers(rhinitis: ChronicRhinitis) -> Modifiers:
    row = C.CHRONIC_RHINITIS_MODIFIERS[rhinitis]
    if rhinitis == "none":
        return Modifiers()
    return Modifiers(
        ra_mult=row["ra_mult"],
        passive_opening_shift_mmHg=row["po_shift_mmHg"],
        pet_tissue_offset_mmHg=row["pet_offset_mmHg"],
        per_descent_rr=row["meb_rr"],
        notes=(f"Chronic {rhinitis}: RA×{row['ra_mult']:.2f}, RR×{row['meb_rr']:.2f}",),
    )


# -------------------------------------------------- Patulous ET part ---
def _pet_modifiers(pet: PetState, *, uri: UriState, habitual_sniffer: bool) -> Modifiers:
    """Patulous ET state machine. See docs/research_notes/03 §4."""
    if pet == "normal":
        return Modifiers()

    if pet == "s2" or (pet == "s1" and uri != "none"):
        # PET + URI / rhinitis / recumbency = paradoxical closure on abnormal substrate.
        # This is the safety-critical state: not protected, and ET may lock at
        # lower pressure than a purely-obstructive ear because the mucosa is
        # already inflamed over a deficient cartilage substrate.
        return Modifiers(
            patulous_unstable=True,
            ra_mult=3.5,
            passive_opening_shift_mmHg=60.0 * C.MMHG_PER_DAPA,
            per_descent_rr=4.0,
            notes=("PET-S2 (PET + inflammation): paradoxical closure, HIGH RISK",),
        )

    if pet == "s1":
        # Baseline patent, upright, dry. Kanick-Doyle prediction holds:
        # tube continuously open → ΔP ≈ 0. Protective for rupture.
        return Modifiers(
            is_patulous_patent=True,
            per_descent_rr=0.4,    # structurally lower MEB in healthy S1
            notes=("PET-S1 (baseline patent): rupture-protective per Kanick-Doyle",),
        )

    if pet == "s3":
        # Habitual sniffer. Shindo 2025: type B/C tympanograms in 42.6%.
        # Baseline ME pressure sits at ≈ -15 mmHg from active closure.
        #
        # v2.2.1 update: Oshima 2025 (PMID 41014990), n=1009 PET patients,
        # reports habitual-sniffing OR 8.18 for PET vs baseline. We raise
        # per_descent_rr from the prior 2.5 to 4.0, reflecting the full
        # OR convolved with already-applied ET-function physics in the
        # deterministic simulator (raising from 2.5 directly to 8.18 would
        # double-count the physiological ΔP bias already modeled).
        return Modifiers(
            habitual_sniffer_bias=True,
            pet_tissue_offset_mmHg=0.0,      # tissue pressure near normal when not sniffing
            per_descent_rr=4.0,
            notes=("PET-S3 (habitual sniffer): sustained −ME pressure, descent-vulnerable (Oshima 2025)",),
        )

    if pet == "s4":
        # Post-Kobayashi-plug or post-fat/cartilage augmentation.
        # Behaves as severely obstructive — large passive opening threshold.
        return Modifiers(
            post_plug_stenotic=True,
            ra_mult=20.0,
            passive_opening_shift_mmHg=C.PET_S4_OPENING_MMHG - C.ET_PASSIVE_OPENING_ME_MMHG,
            per_descent_rr=3.0,
            notes=("PET-S4 (post-plug): stenotic-equivalent behavior",),
        )

    return Modifiers()


# --------------------------------------------------- Medication part ---
def _apply_medication(
    m: Modifiers,
    med: MedicationEffect,
    *,
    pet: PetState,
) -> Modifiers:
    rr = C.MEDICATION_RR[med]

    # Paradoxical worsening: oral/topical decongestants in PET shrink peritubal
    # soft tissue → more patent → worse autophony and worse MEB risk in S2/S3.
    # (docs/research_notes/03 §7)
    decongestant = med in ("pseudoephedrine_oral", "oxymetazoline_topical")
    if decongestant and pet in ("s1", "s2", "s3"):
        rr = 1.4                                    # 40% worse, not better
        m = replace(
            m,
            notes=m.notes + (
                f"{med} in PET-{pet}: PARADOXICAL WORSENING (RR 1.4)",
            ),
        )

    return replace(
        m,
        per_descent_rr=m.per_descent_rr * rr,
        notes=m.notes + (f"medication {med}: RR×{rr:.2f}",) if med != "none" else m.notes,
    )


# ---------------------------------------- v2.3.0 categorical covariates -
def _v23_covariate_modifiers(patient: PatientState) -> Modifiers:
    """Compose modifiers for the v2.3.0 categorical covariates on
    ``PatientState``: sensory_neuropathy, impaired_volitional_equalization,
    glp1_exposure.

    Each active flag contributes its per-descent RR multiplicatively; when
    no flag is set, returns a no-op Modifiers(). Notes are accumulated so
    the clinical-decision-support panel can surface which covariates
    drove the composite risk.
    """
    rr = 1.0
    notes: list[str] = []

    if patient.sensory_neuropathy:
        rr *= C.SENSORY_NEUROPATHY_RR
        notes.append(f"Sensory neuropathy (Voigt 2025): RR×{C.SENSORY_NEUROPATHY_RR:.2f}")

    if patient.impaired_volitional_equalization:
        rr *= C.IMPAIRED_VOLITIONAL_EQUALIZATION_RR
        notes.append(
            f"Impaired volitional equalization (Lee 2025): RR×{C.IMPAIRED_VOLITIONAL_EQUALIZATION_RR:.2f}"
        )

    if patient.glp1_exposure:
        rr *= C.GLP1_EXPOSURE_RR
        notes.append(f"GLP-1 exposure (Sudhoff 2025): RR×{C.GLP1_EXPOSURE_RR:.2f}")

    if not notes:
        return Modifiers()
    return Modifiers(per_descent_rr=rr, notes=tuple(notes))


# --------------------------------------- v2.3.0 BDET post-treatment --
def _bdet_modifier(bdet_treated: bool, *, pet: PetState) -> Modifiers:
    """Partial ET-function restoration for patients with prior balloon
    dilation of the Eustachian tube.

    Evidence: Swords 2025 Cochrane (PMID 40008607) + Khan 2026
    (PMID 41776716). See constants.BDET_* for parameter derivation.

    Safety: BDET is contraindicated in patulous ET because further
    patency exacerbates autophony and paradoxical closure under
    inflammation. When bdet_treated is set alongside a non-normal PET
    state, we apply the numerical modifier (the model does not
    second-guess a clinician who entered it) but surface a CDS note
    flagging the clinical inconsistency.
    """
    if not bdet_treated:
        return Modifiers()

    notes: list[str] = [
        f"BDET-treated (Swords 2025, Khan 2026): RA×{C.BDET_RA_MULT:.2f}, "
        f"RR×{C.BDET_PER_DESCENT_RR:.2f}",
    ]
    if pet != "normal":
        notes.append(
            f"⚠ CLINICAL INCONSISTENCY: bdet_treated + PET-{pet} — "
            "BDET is contraindicated in patulous ET. Simulation proceeds "
            "with BDET modifiers applied; verify patient history before "
            "acting on output."
        )

    return Modifiers(
        ra_mult=C.BDET_RA_MULT,
        passive_opening_shift_mmHg=C.BDET_OPENING_SHIFT_MMHG,
        eq_rate_mult=C.BDET_EQ_RATE_MULT,
        per_descent_rr=C.BDET_PER_DESCENT_RR,
        notes=tuple(notes),
    )


# -------------------------------------------------------- history ----
def _previous_meb_modifier(previous_meb: bool) -> Modifiers:
    if not previous_meb:
        return Modifiers()
    # Modest recurrence penalty (Boel 2017, Rosenkvist 2008).
    return Modifiers(
        per_descent_rr=1.5,
        notes=("Prior MEB history: RR×1.5",),
    )


# --------------------------------------------- composition utility ---
def _compose(a: Modifiers, b: Modifiers) -> Modifiers:
    """Combine two modifier sets (multiplicative on multipliers, additive on shifts)."""
    return Modifiers(
        ra_mult=a.ra_mult * b.ra_mult,
        passive_opening_shift_mmHg=a.passive_opening_shift_mmHg + b.passive_opening_shift_mmHg,
        pet_tissue_offset_mmHg=a.pet_tissue_offset_mmHg + b.pet_tissue_offset_mmHg,
        eq_rate_mult=a.eq_rate_mult * b.eq_rate_mult,
        valsalva_mult=a.valsalva_mult * b.valsalva_mult,
        per_descent_rr=a.per_descent_rr * b.per_descent_rr,
        is_patulous_patent=a.is_patulous_patent or b.is_patulous_patent,
        patulous_unstable=a.patulous_unstable or b.patulous_unstable,
        habitual_sniffer_bias=a.habitual_sniffer_bias or b.habitual_sniffer_bias,
        post_plug_stenotic=a.post_plug_stenotic or b.post_plug_stenotic,
        notes=a.notes + b.notes,
    )


# ---------------------------------------------- applied ET parameters -
def apply_modifiers_to_et(et: EtFunction, m: Modifiers) -> EtFunction:
    """
    Compose an effective EtFunction with URI/PET/rhinitis modifiers applied.

    The resulting ET function reflects what the engine should use for this
    specific exposure, *not* the patient's long-term baseline.
    """
    base_open_me = et.passive_opening_mmHg_me
    base_open_np = et.passive_opening_mmHg_np
    base_ra = et.active_resistance_mmHg_ml_min
    base_fge = et.fge_controls

    # PET states override the passive opening behavior
    if m.is_patulous_patent and not m.patulous_unstable:
        # S1: set opening very low so the tube is effectively always open
        base_open_me = C.PET_S1_OPENING_MMHG
        base_open_np = C.PET_S1_OPENING_MMHG
    elif m.post_plug_stenotic:
        # S4: force stenotic opening
        base_open_me = C.PET_S4_OPENING_MMHG
        base_open_np = C.PET_S4_OPENING_MMHG + 0.0

    return EtFunction(
        severity=et.severity,
        passive_opening_mmHg_me=base_open_me + m.passive_opening_shift_mmHg,
        passive_opening_mmHg_np=base_open_np + m.passive_opening_shift_mmHg,
        closing_mmHg=et.closing_mmHg,
        active_resistance_mmHg_ml_min=base_ra * m.ra_mult,
        active_open_duration_s=et.active_open_duration_s,
        swallow_freq_per_hr_cruise=et.swallow_freq_per_hr_cruise,
        swallow_freq_per_hr_descent=et.swallow_freq_per_hr_descent * m.eq_rate_mult,
        fge_controls=max(0.0, min(1.0, base_fge * m.eq_rate_mult)),
    )
