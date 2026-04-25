"""Build YAML-fronted markdown for the three barotrauma manuscripts.

Reads each manuscript, extracts title/abstract/keywords from the markdown
header, builds a structured YAML front matter conforming to npj-export's
template, and writes the wrapped manuscript to /root/.openclaw/workspace/exports/.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path("/root/.openclaw/workspace/barotrauma_model")
EXPORTS = Path("/root/.openclaw/workspace/exports")
EXPORTS.mkdir(parents=True, exist_ok=True)
DATE = "2026-04-25"


# Unicode → LaTeX math conversions for body text. TeX Gyre Termes lacks several
# superscript/subscript glyphs; convert them to LaTeX math so xelatex renders
# them via the math fonts.
SUP_DIGIT = {"⁰":"0","¹":"1","²":"2","³":"3","⁴":"4","⁵":"5","⁶":"6","⁷":"7","⁸":"8","⁹":"9"}
SUB_DIGIT = {"₀":"0","₁":"1","₂":"2","₃":"3","₄":"4","₅":"5","₆":"6","₇":"7","₈":"8","₉":"9"}
SUP_OTHER = {"⁻":"-","⁺":"+","⁼":"=","⁽":"(","⁾":")"}
SUB_OTHER = {"₋":"-","₊":"+","₌":"=","₍":"(","₎":")"}

_SUP_RE = re.compile(r"(?:[" + "".join(SUP_DIGIT) + "".join(SUP_OTHER) + r"])+")
_SUB_RE = re.compile(r"(?:[" + "".join(SUB_DIGIT) + "".join(SUB_OTHER) + r"])+")


def _sup_to_math(m: re.Match) -> str:
    body = "".join(SUP_DIGIT.get(c, SUP_OTHER.get(c, "")) for c in m.group(0))
    return f"$^{{{body}}}$"


def _sub_to_math(m: re.Match) -> str:
    body = "".join(SUB_DIGIT.get(c, SUB_OTHER.get(c, "")) for c in m.group(0))
    return f"$_{{{body}}}$"


# Standalone math symbols missing from TeX Gyre Termes — wrap in math mode.
EXTRA_MATH = {
    "∈": r"$\in$",
    "∉": r"$\notin$",
    "∫": r"$\int$",
    "∑": r"$\sum$",
    "∏": r"$\prod$",
    "∂": r"$\partial$",
    "∇": r"$\nabla$",
    "ⁿ": "$^{n}$",
    "∞": r"$\infty$",
    "≪": r"$\ll$",
    "≫": r"$\gg$",
}


def sanitise_body(body: str) -> str:
    """Convert Unicode super/subscripts and missing math glyphs to LaTeX math.

    Markdown structure (headings, lists, bold, links, HTML <sub>/<sup>) is
    preserved.
    """
    out = _SUP_RE.sub(_sup_to_math, body)
    out = _SUB_RE.sub(_sub_to_math, out)
    for ch, tex in EXTRA_MATH.items():
        out = out.replace(ch, tex)
    return out


def latex_escape(s: str) -> str:
    """Escape for YAML-single-quoted-string-to-LaTeX rendering.

    Pipeline: Unicode super/sub/math glyph conversion → LaTeX percent/amp/hash
    escaping → YAML single-quote doubling.
    """
    if s is None:
        return ""
    # Convert Unicode glyphs to LaTeX math first, then handle the
    # LaTeX/YAML escapes.
    out = sanitise_body(s)
    out = (out.replace("%", "\\%")
              .replace("&", "\\&")
              .replace("#", "\\#")
              .replace("'", "''"))
    return out


# Add ∪ (set union) to the EXTRA_MATH map (used by sanitise_body).
EXTRA_MATH["∪"] = r"$\cup$"
EXTRA_MATH["∩"] = r"$\cap$"


def extract_section(body: str, header: str, end_pattern: str = r"\n\n\*\*") -> str:
    """Extract the prose between '**header.**' and the next '**...**' label."""
    pat = re.compile(rf"\*\*{re.escape(header)}\.?\*\*\s*(.+?)(?={end_pattern}|\n\n---)", re.DOTALL)
    m = pat.search(body)
    if not m:
        return ""
    text = m.group(1).strip()
    # Collapse internal newlines to spaces
    text = re.sub(r"\s+", " ", text)
    return text


def build_paper1() -> Path:
    """Paper 1 — physics-informed prediction model."""
    raw = (ROOT / "docs" / "manuscript.md").read_text()
    lines = raw.splitlines()
    # Body starts at line 29 (## 1. Introduction) — 0-indexed 28
    body_start = next(i for i, l in enumerate(lines) if l.startswith("## 1. Introduction"))
    header_block = "\n".join(lines[:body_start])
    body = "\n".join(lines[body_start:])

    # Extract structured abstract
    abs_bg = extract_section(header_block, "Background")
    abs_obj = extract_section(header_block, "Objective")
    abs_meth = extract_section(header_block, "Methods")
    abs_res = extract_section(header_block, "Results")
    abs_concl = extract_section(header_block, "Conclusion")
    keywords_match = re.search(r"\*\*Keywords:?\*\*\s*(.+)", header_block)
    keywords = keywords_match.group(1).strip() if keywords_match else ""

    yaml = f"""---
title: 'Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training: A Computational Prediction Model Calibrated to the Colombian Aerospace Force Cohort and Externally Validated Against Italian Air Force Cohorts'

running-title: 'Physics-Informed MEB Model'
running-authors: 'Malpica \\& Farfán'

article-type: 'Original Research'
journal-line: '\\textit{{Aerospace Medicine and Human Performance}} (AsMA)'

author-line: 'Diego L. Malpica, MD\\textsuperscript{{1*}}\\enspace·\\enspace Marian A. Farfán, MD\\textsuperscript{{1}}'

affil-1: 'Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force, Bogotá, Colombia'

correspondence: 'diego.malpica@fac.mil.co'
pdf-author: 'Malpica DL, Farfán MA'

wordcount: '\\textasciitilde{{}}3,250 body \\,/\\, 249 abstract'
version: '1.0 (April 2026)'
repository: 'github.com/strikerdlm/barotrauma\\_model'

abstract-background: '{latex_escape(abs_bg)}'
abstract-objective: '{latex_escape(abs_obj)}'
abstract-methods: '{latex_escape(abs_meth)}'
abstract-results: '{latex_escape(abs_res)}'
abstract-conclusions: '{latex_escape(abs_concl)}'
abstract-keywords: '{latex_escape(keywords)}'
---

"""
    out_path = EXPORTS / f"{DATE}_paper1_physics_informed_meb_model.md"
    out_path.write_text(yaml + sanitise_body(body))
    return out_path


def build_paper2() -> Path:
    """Paper 2 — FAC cohort epidemiology."""
    raw = (ROOT / "docs" / "manuscript_fac_cohort.md").read_text()
    lines = raw.splitlines()
    body_start = next(i for i, l in enumerate(lines) if l.startswith("## 1. Introduction"))
    header_block = "\n".join(lines[:body_start])
    body = "\n".join(lines[body_start:])

    abs_bg = extract_section(header_block, "Background")
    abs_meth = extract_section(header_block, "Methods")
    abs_res = extract_section(header_block, "Results")
    abs_concl = extract_section(header_block, "Discussion")
    keywords_match = re.search(r"\*\*Keywords:?\*\*\s*(.+)", header_block)
    keywords = keywords_match.group(1).strip() if keywords_match else ""

    yaml = f"""---
title: 'Sixteen-Year Incidence of Ear Barotrauma in a Hypobaric-Chamber Training Program at 2,640 m Baseline Altitude: Colombian Aerospace Force 2010--2026 Cohort'

running-title: 'FAC Chamber Barotrauma Incidence'
running-authors: 'Malpica \\textit{{et al.}}'

article-type: 'Research Article'
journal-line: '\\textit{{Aerospace Medicine and Human Performance}} (AsMA)'

author-line: 'Diego L. Malpica, MD\\textsuperscript{{1*}}\\enspace·\\enspace Laura Pineda, MD\\textsuperscript{{2}}\\enspace·\\enspace Maria Alejandra Correa, MD\\textsuperscript{{3}}\\enspace·\\enspace Sonia Jaimes, MD\\textsuperscript{{3}}'

affil-1: 'Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force, Bogotá, Colombia (Aerospace Medicine Specialist)'
affil-2: 'Aeromedical Certification Subdirectorate, Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force, Bogotá, Colombia (Aerospace Medicine Specialist)'
affil-3: 'Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force, Bogotá, Colombia (M.A.C. — Otolaryngologist; S.J. — Aviation Physiology Instructor)'

correspondence: 'diego.malpica@fac.mil.co'
pdf-author: 'Malpica DL, Pineda L, Correa MA, Jaimes S'

wordcount: '\\textasciitilde{{}}3,580 body \\,/\\, 248 abstract'
version: '1.0 (April 2026)'
repository: 'github.com/strikerdlm/barotrauma\\_model'

abstract-background: '{latex_escape(abs_bg)}'
abstract-methods: '{latex_escape(abs_meth)}'
abstract-results: '{latex_escape(abs_res)}'
abstract-conclusions: '{latex_escape(abs_concl)}'
abstract-keywords: '{latex_escape(keywords)}'
---

"""
    out_path = EXPORTS / f"{DATE}_paper2_fac_cohort.md"
    out_path.write_text(yaml + sanitise_body(body))
    return out_path


def build_paper3() -> Path:
    """Paper 3 — preflight fidelity."""
    raw = (ROOT / "docs" / "manuscript_preflight_fidelity.md").read_text()
    lines = raw.splitlines()
    body_start = next(i for i, l in enumerate(lines) if l.startswith("## Introduction"))
    header_block = "\n".join(lines[:body_start])
    body = "\n".join(lines[body_start:])

    abs_obj = extract_section(header_block, "Objectives")
    abs_meth_design = extract_section(header_block, "Design")
    abs_setting = extract_section(header_block, "Setting")
    abs_pop = extract_section(header_block, "Participants")
    abs_outcomes = extract_section(header_block, "Main outcome measures")
    abs_res = extract_section(header_block, "Results")
    abs_concl = extract_section(header_block, "Conclusions")

    # Combine into the 5-field structured layout
    abs_bg = ("Ear barotrauma is the dominant medical complication of "
              "pressurised flight and hypobaric-chamber training; preflight "
              "screening is the principal operational gate, yet no published "
              "study has quantified its discriminatory performance. This study "
              "characterises the flag-level and multivariable performance of "
              "the DIMAE digital preflight instrument.")
    abs_methods_full = (f"{abs_meth_design} {abs_setting} {abs_pop} "
                        f"{abs_outcomes}")

    keywords_match = re.search(r"\*\*Keywords:?\*\*\s*(.+)", header_block)
    keywords = keywords_match.group(1).strip() if keywords_match else ""

    yaml = f"""---
title: 'Screening Performance and Surveillance Yield of a Digital Preflight Medical Instrument for Military Hypobaric-Chamber Training: A Cross-Sectional Observational Study of 1,046 Consecutive Evaluations'

running-title: 'Preflight Screening Fidelity'
running-authors: 'Malpica'

article-type: 'Original Research (cross-sectional observational study)'
journal-line: '\\textit{{BMJ Open}}'

author-line: 'Diego L. Malpica, MD\\textsuperscript{{1*}}'

affil-1: 'Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force (FAC), Bogotá, Colombia'

correspondence: 'dlmalpica@yahoo.com'
pdf-author: 'Malpica DL'

wordcount: '\\textasciitilde{{}}3,041 body \\,/\\, 248 abstract'
version: '1.0 (April 2026)'
repository: 'github.com/strikerdlm/barotrauma\\_model'

abstract-background: '{latex_escape(abs_bg)}'
abstract-objective: '{latex_escape(abs_obj)}'
abstract-methods: '{latex_escape(abs_methods_full)}'
abstract-results: '{latex_escape(abs_res)}'
abstract-conclusions: '{latex_escape(abs_concl)}'
abstract-keywords: '{latex_escape(keywords)}'
---

"""
    out_path = EXPORTS / f"{DATE}_paper3_preflight_fidelity.md"
    out_path.write_text(yaml + sanitise_body(body))
    return out_path


if __name__ == "__main__":
    p1 = build_paper1()
    p2 = build_paper2()
    p3 = build_paper3()
    print(f"Paper 1: {p1}")
    print(f"Paper 2: {p2}")
    print(f"Paper 3: {p3}")
