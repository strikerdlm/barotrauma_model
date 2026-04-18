# 03 — Patulous Eustachian Tube (PET) for Hypobaric-Chamber MEB Modeling

**Purpose.** Close the gap left by Kanick–Doyle (2005): a mechanical model with
`P_ET_tissue < P_ambient` predicts a continuously open tube and ΔP ≈ 0
(rupture-protective) for PET, yet clinical PET carries real symptom burden and
can flip to an obstructive phenotype under inflammation. This brief frames PET
as a **state-dependent** risk variable rather than a single coefficient.

## 1. Diagnostic criteria (JOS 2016/2017)

"Definite PET" per Japan Otological Society (Ikeda 2020 PMID 32397811; Kawamura
2019 PMID 31881045; Ikeda 2024 PMID 39368418) requires **all three**:

1. **Aural symptoms** — voice autophony (93.6% of cases), aural fullness (87.2%),
   breathing autophony (78.2%).
2. **Symptom relief on tubal-obstruction procedure** — recumbency, forward head-
   bending, or nasopharyngeal orifice compression (positive in 91%).
3. **Objective patency**, any of:
   - Breath-synchronized **TM deflection** on otoscopy (69.1%).
   - **TTAG** nasopharynx→EAC pressure-transmission ratio > 0 (75.6%).
   - **Sonotubometry/Ohta method**: ≥10 dB attenuation drop sitting→supine
     (45.2–55.1%).
   - **Sitting 3-D CT**: continuously open lumen (68.6%); enlargement occurs at
     the **isthmus** in PET vs pharyngeal orifice in aging (Ikeda 2022 PMID
     35085108).

**Opening-pressure anchor (modeling).** Kitahara cohort (cited in DAN): PET
opens at **< 200 daPa** (≈ 2 cmH₂O, ≈ 1.5 mmHg); normal 200–650 daPa; stenotic
650–1200 daPa.

**Critical differential:** superior semicircular canal dehiscence (SSCD) produces
autophony in 94% and mimics PET (Poe 2007 PMID 17534202).

## 2. Severity — PHI-10 (Ikeda 2017 PMID 28306653)

10 items × 0–4 → **range 0–40**. Cronbach α = 0.887.

| Band | Score |
|---|---|
| No handicap | 0–8 |
| Mild | 10–16 |
| Moderate | 18–24 |
| Severe (Kobayashi-plug threshold) | 26–40 |

ETDQ-7 cannot discriminate PET severity (Ikeda 2018 PMID 28880712).

## 3. Pathophysiology & prevalence

**Prevalence 0.3–7.0%**; ~10–20% symptomatic; F > M; adolescents/adults
(Ikeda 2024). Triggers: weight loss (diet, bariatric, anorexia, hemodialysis),
pregnancy, oral contraceptives/estrogens, GLP-1 agonists, teprotumumab
(PHI-10 15 [3–24] in 15.6% of treated TED patients; Epperson 2025 PMID
39951668), radiotherapy, neuromuscular disease, TMJ, post-otitis fibrosis.
Mechanisms: **Ostmann fat-pad atrophy**, tensor-veli-palatini hypofunction,
mucosal thinning, and the **longitudinal concave defect of the anterolateral
mucosal valve** (Poe 2007). Middle-ear pressure is normally slightly negative;
in PET it equilibrates to ambient continuously, perceived as abnormal.

## 4. Barotrauma risk — four-state model

| State | Trigger | ET behavior | ΔP_tm in chamber | MEB risk |
|---|---|---|---|---|
| **S1** Baseline PET, upright, dry | none | Patent, opens < 200 daPa | ≈ 0 at all alts | **Low rupture** (Kanick–Doyle holds); autophony + aerophagia |
| **S2** PET + URI / rhinitis / recumbency | mucosal edema | Paradoxically closed or labile | Negative on descent, positive retention on ascent | **Elevated** — loses protective venting on abnormal substrate |
| **S3** PET + habitual sniffing | compensatory behavior | Active closure → sustained −ME pressure, TM retraction (type B/C tymp 42.6%; Shindo 2025 PMID 40779854) | Large negative bias at rest; stacks with climb | Adhesive TM, effusion, descent barotitis |
| **S4** Post-op (plug/shim/fat) | iatrogenic | Fully occluded | Stenotic-equivalent (> 1200 daPa proxy) | Obstructive-MEB envelope (Ikeda 2020 post-plug: 5/28 effusion, 4/28 TM perforation) |

**Paradoxical decongestant effect** (separate axis): oral pseudoephedrine or
oxymetazoline shrink peritubular soft tissue → *more* patent → *worse*
autophony (Iowa protocol). Pre-flight decongestants are therefore not
protective in PET.

**Aerophagia / over-Valsalva.** PET patients who Valsalva to "fix" fullness may
drive gastric-air retrograde flow and TM excursion; avoid forceful Valsalva as
countermeasure.

Baseline MEB in healthy aviators under chamber profiles is 2–8% (Landolfi 2009
PMID 20027855; Morgagni 2010 PMID 20824995). No published cohort stratifies by
PET, so S2/S3 risk multipliers are **mechanistic inferences**, not empirical
odds ratios.

## 5. Quantitative features for the simulator

| Parameter | Range | Source |
|---|---|---|
| ET opening pressure, PET | 0–200 daPa (0–15 mmHg) | Kitahara via DAN |
| Normal opening pressure | 200–650 daPa | Kitahara via DAN |
| Resting `P_ambient − P_ET_tissue`, PET | ≈ 0 mmHg | Ikeda 2024; Iowa protocol |
| Sniff-induced ME pressure (S3) | −100 to −400 daPa | Shindo 2025 |
| URI-induced closure probability (S2) | 0.3–0.7 (Bernoulli input) | Mechanistic (Iowa; Shindo 2025; Lee 2025 PMID 40587724) |
| PHI-10 at S1 | 10–24 typical | Ikeda 2017 |
| PHI-10 at S3 (sniffers) | 26–40 (severe) | Ikeda 2017; Shindo 2025 |

## 6. Aviation / dive regulations

- **FAA** (14 CFR §67, AME Guide Item 29): PET not named; handled under generic
  middle-ear clause prohibiting disease causing vertigo or equilibrium/speech
  disturbance; any symptomatic ETD defers to AMCD. URI explicitly raises
  aerotitis risk (ENR 1.15 §2.2.2).
- **EASA Part-MED AMC1/AMC2 MED.B.080(i):** "Permanent dysfunction of the
  Eustachian tube(s) may be assessed as fit if ENT evaluation is satisfactory"
  — explicit case-by-case fit for Class 1 and 2.
- **USAF AFI 48-123 + ACS Waiver Guide:** ETD disqualifying if risk of
  incapacitation/subtle decrement; waiver possible once stable.
- **ICAO Annex 1:** deferred to state authority; no explicit PET clause.
- **Dive (UHMS/DAN; Mallen 2020 PMID 30776095):** PET not automatically
  disqualifying absent effusion or alternobaric vertigo; post-plug/shim cases
  reviewed individually.

## 7. Treatment — modeling implications

- Conservative (saline, head-down, weight restoration, **avoid decongestants**):
  mechanical state unchanged; PHI-10 often unchanged (Ikeda 2017).
- **Kobayashi silicone plug:** PHI-10 34.4 → 5.7 at 6 mo; 82.1% success;
  17.2% post-op effusion, 13.8% TM perforation (Ikeda 2020 PMID 31400157).
  Converts S1 → S4.
- **Fat / cartilage / Alloderm valve augmentation:** Poe 2007 — restores
  convexity; immediate autophony relief in 14/14 ears.
- **Shim, mass-loading TM, AET reversal:** step-up strategies (AlAmry 2024
  PMID 38727149; Yang 2023 PMID 37253528).

## 8. Modeling recommendation

Treat PET as a **four-state latent variable** (S1–S4) conditioned on URI
status, posture, and surgical history — *not* as a single `P_ET_tissue`
offset. Kanick–Doyle's prediction holds only in S1. **S2 is the safety-critical
state for chamber training**: require baseline tympanometry + nasal endoscopy
within 24 h of profile exposure, and defer profiles with active mucosal edema
or type-B/C tympanogram. Implement S3 as a per-session modifier when history
of habitual sniffing is documented.

---

**Key PMIDs:** 39368418, 32397811, 31881045, 28306653, 28880712, 31400157,
31430219, 33989255, 35085108, 40779854, 17534202, 40587724, 38727149,
39951668, 20027855, 20824995, 30776095, 37253528. **Regulatory:** EASA
AMC1/AMC2 MED.B.080(i); FAA AME Guide Item 29 and ENR 1.15 §2.2; AFI 48-123.
