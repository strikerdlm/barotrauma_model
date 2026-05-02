import re

with open('docs/manuscript_bmb_corrected.md', 'r', encoding='utf-8') as f:
    md = f.read()

# =====================================================================
# 1.  Build BibTeX database
# =====================================================================

ref_data = [
    ("Alper CM, Kitsko DJ, Swarts JD, Martin B, Yuksel S, Doyle WJ", "2011", "Role of the mastoid in middle ear pressure regulation", "Laryngoscope", "121(2):404–408", "10.1002/lary.21275"),
    ("Alper CM, Teixeira MS, Rath TJ, Hall-Burton D, Swarts JD", "2020", "Change in Eustachian tube function with balloon dilation in adults with ventilation tubes", "Otol Neurotol", "41(4):482–488", "10.1097/mao.0000000000002559"),
    ("Boel NM, Klokker M", "2017", "Upper respiratory infections and barotrauma among commercial pilots", "Aerosp Med Hum Perform", "88(1):17–22", "10.3357/amhp.4511.2017"),
    ("Buchman CA, Doyle WJ, Skoner D, Fireman P, Gwaltney JM", "1994", "Otologic manifestations of experimental rhinovirus infection", "Laryngoscope", "104(10):1295–1299", "10.1288/00005537-199410000-00021"),
    ("Chen T, Shih MC, Edwards TS, Nguyen SA, Meyer TA, Soler ZM, et al.", "2022", "Eustachian tube dysfunction (ETD) in chronic rhinosinusitis with comparison to primary ETD: a systematic review and meta-analysis", "Int Forum Allergy Rhinol", "12(7):942–951", "10.1002/alr.22942"),
    ("Doyle WJ", "2017", "A formal description of middle ear pressure-regulation", "Hear Res", "354:73–85", "10.1016/j.heares.2017.08.005"),
    ("Doyle WJ, Singla A, Banks J, El-Wagaa J, Swarts JD", "2014", "Pressure chamber tests of Eustachian tube function document lower efficiency in adults with colds when compared to without colds", "Acta Otolaryngol", "134(7):691–697", "10.3109/00016489.2014.892213"),
    ("Doyle WJ, Skoner DP, Alper CM, et al.", "1999", "Illness and otological changes during upper respiratory virus infection", "Laryngoscope", "109(2 Pt 1):324–328", "10.1097/00005537-199902000-00027"),
    ("Doyle WJ, Swarts JD, Banks J, Yuksel S, Alper CM", "2011", "Transmucosal O2 and CO2 exchange rates for the human middle ear", "Auris Nasus Larynx", "38(6):684–691", "10.1016/j.anl.2011.01.006"),
    ("Ghadiali SN, Banks J, Swarts JD", "2004", "Finite element analysis of active Eustachian tube function", "J Appl Physiol", "97(2):648–654", "10.1152/japplphysiol.01250.2003"),
    ("Kanick SC, Doyle WJ", "2005", "Barotrauma during air travel: predictions of a mathematical model", "J Appl Physiol", "98(5):1592–1602", "10.1152/japplphysiol.00974.2004"),
    ("Kikuchi T, Ikeda R, Oshima H, Takata I, Kawase T, Oshima T, Katori Y, Kobayashi T", "2017", "Effectiveness of Kobayashi plug for 252 ears with chronic patulous Eustachian tube", "Acta Otolaryngol", "137(3):253–258", "10.1080/00016489.2016.1231420"),
    ("Kobayashi T, Morita M, Yoshioka S, Mizuta K, Ohta S, Kikuchi T, Hayashi T, Kaneko A, Yamaguchi N, Hashimoto S, Kojima H, Murakami S, Takahashi H", "2018", "Diagnostic criteria for patulous Eustachian tube: a proposal by the Japan Otological Society", "Auris Nasus Larynx", "45(1):1–5", "10.1016/j.anl.2017.09.017"),
    ("Landolfi A, Torchia F, Autore A, Ciniglio Appiani M, Morgagni F, Ciniglio Appiani G", "2009", "Acute otitic barotrauma during hypobaric chamber training: prevalence and prevention", "Aviat Space Environ Med", "80(12):1059–1062", "10.3357/asem.2599.2009"),
    ("Lindfors OH, Ketola KS, Klockars TK, Leino TK, Sinkkonen ST", "2021", "Middle ear barotraumas in commercial aircrew", "Aerosp Med Hum Perform", "92(3):182–189", "10.3357/amhp.5738.2021"),
    ("McBride TP, Doyle WJ, Hayden FG, Gwaltney JM Jr", "1989", "Alterations of the Eustachian tube, middle ear, and nose in rhinovirus infection", "Arch Otolaryngol Head Neck Surg", "115(9):1054–1059", "10.1001/archotol.1989.01860330044014"),
    ("Moayedi S, Gizaw A, Sweet S, Sethuraman K, Witting M", "2025", "Pseudoephedrine prophylaxis does not prevent middle ear barotrauma in hyperbaric oxygen therapy", "Undersea Hyperb Med", "52(2):101–107", "10.22462/717"),
    ("Morgagni F, Autore A, Landolfi A, Ciniglio Appiani M, Marcoccia A", "2012", "Predictors of ear barotrauma in aircrews exposed to simulated high altitude", "Aviat Space Environ Med", "83(6):594–598", "10.3357/asem.3255.2012"),
    ("Morgagni F, Autore A, Landolfi A, Torchia F, Ciniglio Appiani G", "2010", "Altitude chamber related adverse effects among 1241 airmen", "Aviat Space Environ Med", "81(9):873–877", "10.3357/asem.2625.2010"),
    ("Oshima H, Yoshida M, Shindo H, Hirai R, Oshima T", "2025", "Clinical characteristics and diagnostic value of symptoms and objective findings in patulous eustachian tube: a large-scale study based on the Japan Otological Society criteria", "Auris Nasus Larynx", "52(6):651–656", "10.1016/j.anl.2025.09.002"),
    ("Saltelli A, Annoni P, Azzini I, Campolongo F, Ratto M, Tarantola S", "2010", "Variance based sensitivity analysis of model output: design and estimator for the total sensitivity index", "Comput Phys Commun", "181(2):259–270", "10.1016/j.cpc.2009.09.018"),
    ("Shindo H, Yoshida M, Hirai R, Oshima T", "2025", "Clinical characteristics and surgical indications in pediatric patulous Eustachian tube: the importance of habitual sniffing", "Auris Nasus Larynx", "52(5):545–549", "10.1016/j.anl.2025.07.003"),
    ("Toni T, Welch D, Strelkowa N, Ipsen A, Stumpf MPH", "2009", "Approximate Bayesian computation scheme for parameter inference and model selection in dynamical systems", "J R Soc Interface", "6(31):187–202", "10.1098/rsif.2008.0172"),
    ("Wang B, Xu X, Lin J, Jin Z", "2019", "Dynamic rabbit model of ear barotrauma", "Aerosp Med Hum Perform", "90(8):696–702", "10.3357/amhp.5167.2019"),
]

def surname(first_author_field):
    parts = first_author_field.strip().split()
    # Names are stored as "FirstName Initials" (e.g. "Alper CM", "Doyle WJ")
    # Surname is the first token
    return parts[0]

bib_lines = []
seen_keys = {}
for authors, year, title, journal, vp, doi in ref_data:
    sur = surname(authors)
    key = f"{sur}{year}"
    if key in seen_keys:
        key = f"{key}a"
    seen_keys[key] = True
    author_list = ' and '.join([a.strip() for a in authors.split(',')])
    # Parse volume/pages
    vm = re.match(r'(\d+)\(([^)]+)\)?:(.+)', vp)
    if vm:
        vol, num, pages = vm.groups()
    else:
        vm2 = re.match(r'(\d+):(.+)', vp)
        if vm2:
            vol, pages = vm2.groups()
            num = ''
        else:
            vol = vp
            num = ''
            pages = ''
    bib_lines.append(f"@article{{{key},")
    bib_lines.append(f"  author  = {{{author_list}}},")
    bib_lines.append(f"  year    = {{{year}}},")
    bib_lines.append(f"  title   = {{{title}}},")
    bib_lines.append(f"  journal = {{{journal}}},")
    if vol and re.match(r'^\d+$', str(vol)):
        bib_lines.append(f"  volume  = {{{vol}}},")
    if num:
        bib_lines.append(f"  number  = {{{num}}},")
    if pages:
        bib_lines.append(f"  pages   = {{{pages}}},")
    bib_lines.append(f"  doi     = {{{doi}}},")
    bib_lines.append("}")
    bib_lines.append("")

bib_content = '\n'.join(bib_lines)
with open('docs/submission/references.bib', 'w', encoding='utf-8') as f:
    f.write(bib_content)
print(f"Wrote {len(ref_data)} references to docs/submission/references.bib")

# =====================================================================
# 2.  Citation replacement map
# =====================================================================

cite_map = [
    # Multi-citations (longest first)
    ('(Morgagni et al., 2012; Landolfi et al., 2009; Morgagni et al., 2010)', r'\citep{Morgagni2012,Landolfi2009,Morgagni2010}'),
    ('(McBride et al., 1989; Buchman et al., 1994; Doyle et al., 1999)', r'\citep{McBride1989,Buchman1994,Doyle1999}'),
    ('(Kobayashi et al., 2018; Kikuchi et al., 2017; Shindo et al., 2025)', r'\citep{Kobayashi2018,Kikuchi2017,Shindo2025}'),
    ('(Lindfors et al., 2021; Boel & Klokker, 2017)', r'\citep{Lindfors2021,Boel2017}'),
    # Single citations
    ('(Morgagni et al., 2010)', r'\citep{Morgagni2010}'),
    ('(Morgagni et al., 2012)', r'\citep{Morgagni2012}'),
    ('(Landolfi et al., 2009)', r'\citep{Landolfi2009}'),
    ('(Lindfors et al., 2021)', r'\citep{Lindfors2021}'),
    ('(Kanick & Doyle, 2005)', r'\citep{Kanick2005}'),
    ('(Kanick-Doyle, 2005)', r'\citep{Kanick2005}'),
    ('(Buchman et al., 1994)', r'\citep{Buchman1994}'),
    ('(Doyle et al., 1999)', r'\citep{Doyle1999}'),
    ('(Doyle et al., 2014)', r'\citep{Doyle2014}'),
    ('(Doyle et al., 2011)', r'\citep{Doyle2011}'),
    ('(Doyle, 2017)', r'\citep{Doyle2017}'),
    ('(Chen et al., 2022)', r'\citep{Chen2022}'),
    ('(Alper et al., 2020)', r'\citep{Alper2020}'),
    ('(Alper et al., 2011)', r'\citep{Alper2011}'),
    ('(Ghadiali et al., 2004)', r'\citep{Ghadiali2004}'),
    ('(Toni et al., 2009)', r'\citep{Toni2009}'),
    ('(Saltelli et al., 2010)', r'\citep{Saltelli2010}'),
    ('(Wang et al., 2019)', r'\citep{Wang2019}'),
    ('(Moayedi et al., 2025)', r'\citep{Moayedi2025}'),
    ('(Oshima et al., 2025)', r'\citep{Oshima2025}'),
    ('(Shindo et al., 2025)', r'\citep{Shindo2025}'),
    ('(Kikuchi et al., 2017)', r'\citep{Kikuchi2017}'),
    ('(Kobayashi et al., 2018)', r'\citep{Kobayashi2018}'),
    ('(McBride et al., 1989)', r'\citep{McBride1989}'),
    # Bare author-year used as nouns
    ('Oshima et al. (2025)', r'\citet{Oshima2025}'),
    ('Moayedi et al. (2025)', r'\citet{Moayedi2025}'),
    ('Lindfors et al. (2021)', r'\citet{Lindfors2021}'),
    ('Alper et al. (2011)', r'\citet{Alper2011}'),
    ('Doyle et al. (2014)', r'\citet{Doyle2014}'),
    ('Doyle et al. (2011)', r'\citet{Doyle2011}'),
    ('Doyle (2017)', r'\citet{Doyle2017}'),
]

for old, new in cite_map:
    md = md.replace(old, new)

# =====================================================================
# 3.  Split manuscript into blocks
# =====================================================================

abstract_match = re.search(r'## Abstract\s*\n\n?(.*?)\n\n---', md, re.DOTALL)
if abstract_match:
    abstract_text = abstract_match.group(1).strip()
    # Remove abstract and everything before it (title page metadata) from main body
    body = md[abstract_match.end():]
else:
    abstract_text = ''
    body = md

refs_start = body.find('## References')
tables_start = body.find('## Tables')
figures_start = body.find('## Figure captions')

body_main = body[:refs_start].strip()

# Extract tables section (between ## Tables and ## Figure captions)
tables_text = ''
if tables_start != -1 and figures_start != -1:
    tables_text = body[tables_start:figures_start].strip()
    # Remove the '## Tables' header line
    tables_text = re.sub(r'^## Tables\s*\n+', '', tables_text)
    tables_text = re.sub(r'^## Tables\s*\n*', '', tables_text)
    tables_text = tables_text.strip()

# =====================================================================
# 4.  Convert markdown → LaTeX
# =====================================================================

def escape_tex(text):
    result = []
    in_math = False
    in_url = False
    url_depth = 0
    i = 0
    while i < len(text):
        if text[i] == '$' and not in_url:
            result.append(text[i])
            in_math = not in_math
            i += 1
            continue
        if not in_math and not in_url:
            if text.startswith(r'\url{', i):
                result.append(r'\url{')
                i += len(r'\url{')
                in_url = True
                url_depth = 1
                continue
            replaced = False
            for old, new in [('&', r'\&'), ('%', r'\%'), ('#', r'\#'), ('_', r'\_')]:
                if text[i:i+len(old)] == old:
                    result.append(new)
                    i += len(old)
                    replaced = True
                    break
            if not replaced:
                result.append(text[i])
                i += 1
        elif in_url:
            result.append(text[i])
            if text[i] == '{':
                url_depth += 1
            elif text[i] == '}':
                url_depth -= 1
                if url_depth == 0:
                    in_url = False
            i += 1
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)

def process_inline(text):
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', lambda m: r'\textbf{' + m.group(1) + '}', text)
    # Italic (not inside math)
    result = []
    in_math = False
    i = 0
    while i < len(text):
        if text[i] == '$':
            result.append(text[i])
            in_math = not in_math
            i += 1
            continue
        if not in_math and text[i] == '*':
            j = text.find('*', i+1)
            if j != -1:
                result.append('\\textit{')
                result.append(text[i+1:j])
                result.append('}')
                i = j + 1
                continue
        result.append(text[i])
        i += 1
    text = ''.join(result)
    # Unicode superscripts / subscripts — group contiguous runs so 10⁻⁸ → 10$^{-8}$
    sup_map = {'⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9','ⁿ':'n','⁻':'-'}
    sub_map = {'₀':'0','₁':'1','₂':'2','₃':'3','₄':'4','₅':'5','₆':'6','₇':'7','₈':'8','₉':'9'}
    import re as _re
    text = _re.sub('[' + ''.join(sup_map.keys()) + ']+', lambda m: '$^{' + ''.join(sup_map.get(c, c) for c in m.group(0)) + '}$', text)
    text = _re.sub('[' + ''.join(sub_map.keys()) + ']+', lambda m: '$_{' + ''.join(sub_map.get(c, c) for c in m.group(0)) + '}$', text)
    text = text.replace('·', '$\\cdot$')
    text = text.replace('α', '$\\alpha$')
    text = text.replace('∈', '$\\in$')
    text = text.replace('×', '$\\times$')
    text = text.replace('≈', '$\\approx$')
    text = text.replace('−', '-')
    text = text.replace('–', '--')
    text = text.replace('—', '---')
    text = text.replace('≥', '$\\geq$')
    text = text.replace('±', '$\\pm$')
    text = text.replace('∫', '$\\int$')
    text = text.replace('→', '$\\rightarrow$')
    text = text.replace('Θ', '$\\Theta$')
    text = text.replace('τ', '$\\tau$')
    text = text.replace('√', '$\\surd$')
    # URLs
    text = re.sub(r'<(https?://[^>]+)>', lambda m: r'\url{' + m.group(1) + '}', text)
    text = re.sub(r'https?://[^\s<>\[\]{}]+', lambda m: r'\url{' + m.group(0).rstrip('.,;:!?') + '}', text)
    # Remove accidental double \url wrappers
    text = re.sub(r'\\url\{\\url\{([^}]+)\}\}', r'\\url{\1}', text)
    # Inline code
    text = re.sub(r'`([^`]+)`', lambda m: r'\texttt{' + m.group(1) + '}', text)
    # Escape remaining TeX specials outside math
    text = escape_tex(text)
    # Merge adjacent inline math blocks separated by ^ or _ (e.g. $\Theta_i$)^$n_i$)
    text = re.sub(r'\$([^$]+)\$(\)?)\s*\^\s*\$([^$]+)\$', r'$\1\2^{\3}$', text)
    text = re.sub(r'\$([^$]+)\$(\)?)\s*_\s*\$([^$]+)\$', r'$\1\2_{\3}$', text)
    return text

def md_to_tex(text):
    lines = text.split('\n')
    out_lines = []
    in_table = False
    table_lines = []

    for line in lines:
        stripped = line.strip()

        if stripped == '---':
            out_lines.append('')
            continue

        # Headers (strip explicit numbering like "1. Introduction")
        if stripped.startswith('# ') and not stripped.startswith('## '):
            out_lines.append(f"\\section*{{{process_inline(stripped[2:].strip())}}}")
            continue
        if stripped.startswith('## '):
            heading = stripped[3:].strip()
            heading = re.sub(r'^\d+\.\s+', '', heading)
            out_lines.append(f"\\section{{{process_inline(heading)}}}")
            continue
        if stripped.startswith('### '):
            out_lines.append(f"\\subsection{{{process_inline(stripped[4:].strip())}}}")
            continue
        if stripped.startswith('#### '):
            out_lines.append(f"\\subsubsection{{{process_inline(stripped[5:].strip())}}}")
            continue

        # Tables
        if stripped.startswith('|'):
            table_lines.append(stripped)
            in_table = True
            continue
        elif in_table:
            out_lines.append(process_table(table_lines))
            table_lines = []
            in_table = False

        # Regular paragraph
        if stripped:
            out_lines.append(process_inline(line))
        else:
            out_lines.append('')

    if in_table and table_lines:
        out_lines.append(process_table(table_lines))

    return '\n'.join(out_lines)

def process_table(lines):
    PIPE_PLACEHOLDER = '\x00PIPE\x00'
    rows = []
    for line in lines:
        # Protect escaped pipes, then split
        protected = line.strip().replace('\\|', PIPE_PLACEHOLDER)
        cells = [c.strip().replace(PIPE_PLACEHOLDER, '|') for c in protected.strip('|').split('|')]
        rows.append(cells)
    if not rows:
        return ''
    # First row = header, second = separator, rest = data
    if len(rows) >= 2 and all(re.match(r'^[-:]+$', c) for c in rows[1]):
        header = rows[0]
        data = rows[2:]
    else:
        header = rows[0]
        data = rows[1:]
    num_cols = len(header)
    col_spec = 'l' * num_cols
    tex = f"\\begin{{table}}[htbp]\n\\centering\n\\begin{{tabular}}{{{col_spec}}}\n\\toprule\n"
    tex += ' & '.join(process_inline(c) for c in header) + ' \\\\\n'
    tex += '\\midrule\n'
    for row in data:
        while len(row) < num_cols:
            row.append('')
        tex += ' & '.join(process_inline(c) for c in row[:num_cols]) + ' \\\\\n'
    tex += '\\bottomrule\n\\end{tabular}\n\\end{table}'
    return tex

# =====================================================================
# 5.  Build title / author block
# =====================================================================

title_block = r"""\title{Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training: A Computational Prediction Model Calibrated to the Colombian Aerospace Force Cohort and Externally Validated Against Italian Air Force Cohorts}

\author{Diego L. Malpica$^{1,2,*}$ \and Marian A. Farf\'{a}n$^{1}$}

\date{}
"""

# =====================================================================
# 6.  Assemble full document
# =====================================================================

latex_doc = r"""\documentclass[11pt,a4paper]{article}

\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{amsmath,amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{natbib}
\usepackage{url}
\usepackage{hyperref}
\usepackage{lineno}
\usepackage{geometry}
\usepackage{caption}
\usepackage[protrusion=true,expansion=false]{microtype}

\geometry{margin=2.5cm}
\linenumbers
\pagestyle{plain}

% natbib author-year setup
\bibpunct{(}{)}{;}{a}{,}{,}

% upright derivative d
\newcommand{\diff}{\mathrm{d}}

""" + title_block + r"""

\begin{document}

\maketitle

\begin{abstract}
"""

# Convert abstract
if abstract_text:
    abstract_text = re.sub(r'\*\*Background\.\*\*', r'\\textbf{Background.}', abstract_text)
    abstract_text = re.sub(r'\*\*Objective\.\*\*', r'\\textbf{Objective.}', abstract_text)
    abstract_text = re.sub(r'\*\*Methods\.\*\*', r'\\textbf{Methods.}', abstract_text)
    abstract_text = re.sub(r'\*\*Results\.\*\*', r'\\textbf{Results.}', abstract_text)
    abstract_text = re.sub(r'\*\*Conclusion\.\*\*', r'\\textbf{Conclusion.}', abstract_text)
    # Convert remaining inline markup
    abstract_text = process_inline(abstract_text)
    latex_doc += abstract_text + '\n\\end{abstract}\n\n'
else:
    latex_doc += '\\end{abstract}\n\n'

# Convert body
body_tex = md_to_tex(body_main)
latex_doc += body_tex + '\n\n'

# Convert tables
if tables_text:
    tables_tex = md_to_tex(tables_text)
    latex_doc += tables_tex + '\n\n'

# Figures
latex_doc += r"""
% =====================================================================
% Figures
% =====================================================================

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\textwidth]{../figures/paper_c/fig_01_descent_rate_sensitivity.png}
\caption{Descent-rate sensitivity for a healthy patient on a 25,000-ft descent. Peak $|\Delta P|$ (top panel) grows monotonically with descent rate, approaching $\sim$400~mmHg at 10,000~ft$\cdot$min$^{-1}$. Per-exposure barotitis probability (bottom panel) increases across the full 500--10,000~ft$\cdot$min$^{-1}$ range because the dose-time integral does not saturate as sharply as the peak}
\label{fig:descent_rate}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\textwidth]{../figures/paper_c/fig_02_sobol_sensitivity.png}
\caption{Saltelli-Sobol total-order sensitivity index over four model parameters evaluated at a moderate-risk reference patient ($N = 128$ Saltelli base samples; 768 model evaluations; scrambled-Sobol QMC sequence, seed~2026). The aperture half-point dominates ($S_T \approx 0.99$), approximately fifty-fold above descent-phase swallow frequency ($S_T = 0.020$), aperture free-zone threshold ($S_T = 0.019$), and mastoid volume ($S_T = 0.005$). The three secondary parameters are indistinguishable from each other within Monte-Carlo noise}
\label{fig:sobol}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\textwidth]{../figures/paper_c/fig_03_external_validation.png}
\caption{External validation of the model against the calibration anchor (Colombian Aerospace Force pooled 2010--2026) and three independent published Italian Air Force cohorts. Observed per-exposure barotitis incidence (filled circles) is shown with Wilson 95\% confidence intervals (whiskers); simulated point estimates (diamonds) are colored green when within the observed CI and orange when outside. The model fell within the observed CI for the calibration cohort (sim 2.47\% vs obs 2.38\%, CI [2.06--2.75]) and for two of the three external cohorts (Morgagni 2012 and Landolfi 2009). The Morgagni 2010 simulated point (3.27\%) sits 0.91 percentage points above the upper CI bound of that cohort's observed estimate (1.51\%, CI [0.97--2.36]), within the cohort's own pre-screened-to-unscreened denominator spread (1.1\% to 2.7\%) reported in the source publication. Right margin shows event count over cohort denominator and the simulated point with within-CI status}
\label{fig:validation}
\end{figure}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.85\textwidth]{../figures/paper_c/fig_04_uri_pet_interaction.png}
\caption{Joint dependence of per-exposure barotitis probability on Patulous Eustachian-tube state (5 levels: No PET, S1 baseline patent and dry mucosa, S2 PET with inflammation, S3 habitual sniffer, S4 post-Kobayashi plug or stenotic-equivalent) and upper-respiratory-infection temporal state (6 levels: none, days 1--3, 4--7, 8--14, 15--21, 22--28). Each cell is the model output for a default healthy baseline patient on the FAC Bogot\'{a} chamber profile (8,530~ft start, 25,000~ft hold, 2,470~ft$\cdot$min$^{-1}$ descent), varying only the URI and PET states; values were computed by \texttt{barotrauma.v2.simulate} over the full $5 \times 6$ grid. The peak-URI window (days 4--7) dominates each PET row. PET-S1 (rupture-protective in the original Kanick-Doyle 2005 binary treatment) is converted to high risk by URI exposure, matching the PET-with-inflammation pathophysiology in the Japan Otological Society criteria. PET-S4 saturates regardless of URI state. PET-S3 returns uniformly low risk on this profile because the negative resting-pressure bias offsets the descent-side $\Delta P$ integral; this model behavior is profile-specific and should not be interpreted as habitual sniffing being clinically protective}
\label{fig:uri_pet}
\end{figure}

"""

# References
latex_doc += r"""
% =====================================================================
% References
% =====================================================================

\bibliographystyle{apalike}
\bibliography{references}

\end{document}
"""

with open('docs/submission/manuscript_bmb.tex', 'w', encoding='utf-8') as f:
    f.write(latex_doc)

print("Wrote docs/submission/manuscript_bmb.tex")
