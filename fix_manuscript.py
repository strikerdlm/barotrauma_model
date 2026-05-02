import re

with open('docs/manuscript.md', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Fix figure count in header
text = text.replace('figures 2.', 'figures 4.')

# 2. Fix table numbering (Roman -> Arabic)
text = re.sub(r'\bTable I\b', 'Table 1', text)
text = re.sub(r'\bTable II\b', 'Table 2', text)
text = re.sub(r'\bTable III\b', 'Table 3', text)
text = re.sub(r'\bTable IV\b', 'Table 4', text)

# 3. Fix declarations heading
text = text.replace('## Declarations', '## Statements and Declarations')

# 4. Fix figure captions format
text = re.sub(r'\*\*Figure (\d+)\.\*\*', r'**Fig. \1**', text)
# Remove trailing periods from figure caption lines
lines = text.split('\n')
for i, line in enumerate(lines):
    if line.startswith('**Fig. ') and line.endswith('.'):
        lines[i] = line[:-1]
text = '\n'.join(lines)

# 5. Replace in-text citations (multi-citation patterns first)
text = text.replace('data¹⁰·¹¹', 'data (Buchman et al., 1994; Doyle et al., 1999)')
text = text.replace('populations,⁴·¹²', 'populations (Lindfors et al., 2021; Boel & Klokker, 2017),')
text = text.replace('post-onset,⁹⁻¹¹', 'post-onset (McBride et al., 1989; Buchman et al., 1994; Doyle et al., 1999),')
text = text.replace('data⁹⁻¹¹', 'data (McBride et al., 1989; Buchman et al., 1994; Doyle et al., 1999)')
text = text.replace('one.⁶⁻⁸', 'one (Kobayashi et al., 2018; Kikuchi et al., 2017; Shindo et al., 2025).')
text = text.replace('states.⁶⁻⁸', 'states (Kobayashi et al., 2018; Kikuchi et al., 2017; Shindo et al., 2025).')
text = text.replace('literature⁶⁻⁸', 'literature (Kobayashi et al., 2018; Kikuchi et al., 2017; Shindo et al., 2025)')
text = text.replace('exposure¹⁻³', 'exposure (Morgagni et al., 2012; Landolfi et al., 2009; Morgagni et al., 2010)')
text = text.replace('cohorts¹⁻³', 'cohorts (Morgagni et al., 2012; Landolfi et al., 2009; Morgagni et al., 2010)')
text = text.replace('publications.¹⁻³', 'publications (Morgagni et al., 2012; Landolfi et al., 2009; Morgagni et al., 2010).')

# Single citations
text = text.replace('careers.⁴', 'careers (Lindfors et al., 2021).')
text = text.replace('model.⁵', 'model (Kanick & Doyle, 2005).')
text = text.replace('meta-analyses.¹⁶', 'meta-analyses (Chen et al., 2022).')
text = text.replace('(Shindo 2025).⁸', '(Shindo et al., 2025).')
text = text.replace('Oshima 2025²⁴', 'Oshima et al. (2025)')
text = text.replace('Moayedi 2025²³', 'Moayedi et al. (2025)')
text = text.replace('work¹⁷', 'work (Ghadiali et al., 2004)')
text = text.replace('(Doyle 2017).¹⁸', '(Doyle, 2017).')
text = text.replace('Doyle 2017.¹⁸', '(Doyle, 2017).')
text = text.replace('ABC-SMC)¹⁹', 'ABC-SMC) (Toni et al., 2009)')
text = text.replace('indices²⁰', 'indices (Saltelli et al., 2010)')
text = text.replace('gradient²²', 'gradient (Wang et al., 2019)')
text = text.replace('measurements.²¹', 'measurements (Alper et al., 2020).')
text = text.replace('Alper 2011¹³;', 'Alper et al. (2011);')
text = text.replace('(Doyle 2014 pressure-chamber test);¹⁴', '(Doyle et al., 2014);')
text = text.replace('(Doyle 2011).¹⁵', '(Doyle et al., 2011).')
text = text.replace('Doyle 2011.¹⁵', '(Doyle et al., 2011).')
text = text.replace('Lindfors 2021⁴', 'Lindfors et al. (2021)')

# 6. Basic math notation fixes
text = text.replace('d(ΔP)/dt', '$\\mathrm{d}(\\Delta P)/\\mathrm{d}t$')
text = text.replace('dΔP/dt', '$\\mathrm{d}\\Delta P/\\mathrm{d}t$')
text = text.replace('R<sub>A</sub>', '$R_A$')
text = text.replace('P<sub>O</sub>\'', '$P_O\'$')
text = text.replace('V<sub>ME</sub>', '$V_{\\mathrm{ME}}$')
text = text.replace('h<sub>i</sub>(t)', '$h_i(t)$')
text = text.replace('Θ<sub>i</sub>', '$\\Theta_i$')
text = text.replace('r<sub>i</sub>', '$r_i$')
text = text.replace('p<sub>barotitis</sub>', '$p_{\\mathrm{barotitis}}$')
text = text.replace('p<sub>rupture</sub>', '$p_{\\mathrm{rupture}}$')
text = text.replace('n<sub>i</sub>', '$n_i$')
text = text.replace('P<sub>i</sub>', '$P_i$')
text = text.replace('h<sub>i</sub>', '$h_i$')
text = text.replace('V<sub>tympanum</sub>', '$V_{\\mathrm{tympanum}}$')
text = text.replace('V<sub>mastoid</sub>', '$V_{\\mathrm{mastoid}}$')
text = text.replace('r<sub>barotitis</sub>', '$r_{\\mathrm{barotitis}}$')
text = text.replace('r<sub>baromyringitis</sub>', '$r_{\\mathrm{baromyringitis}}$')
text = text.replace('r<sub>rupture</sub>', '$r_{\\mathrm{rupture}}$')
text = text.replace('S<sub>T</sub>', '$S_T$')
text = text.replace('S<sub>i</sub>', '$S_i$')
text = text.replace('CO<sub>2</sub>', '$\\mathrm{CO}_2$')
text = text.replace('O<sub>2</sub>', '$\\mathrm{O}_2$')
text = text.replace('N<sub>2</sub>', '$\\mathrm{N}_2$')
text = text.replace('H<sub>2</sub>O', '$\\mathrm{H}_2\\mathrm{O}$')
text = text.replace('ΔP<sub>½</sub>', '$\\Delta P_{1/2}$')

# General ΔP in remaining places (be careful to avoid already-mathed ones)
# Use a heuristic: replace ΔP when not preceded by $ and not followed by $
def delta_p_repl(m):
    return m.group(1) + '$\\Delta P$' + m.group(2)

text = re.sub(r'(?<!\$)(?<![\\])ΔP(?!\$)', r'$\\Delta P$', text)

# 7. Replace numbered references with alphabetized name-year list
ref_block = """## References

Alper CM, Kitsko DJ, Swarts JD, Martin B, Yuksel S, Doyle WJ (2011) Role of the mastoid in middle ear pressure regulation. *Laryngoscope* 121(2):404–408. https://doi.org/10.1002/lary.21275

Alper CM, Teixeira MS, Rath TJ, Hall-Burton D, Swarts JD (2020) Change in Eustachian tube function with balloon dilation in adults with ventilation tubes. *Otol Neurotol* 41(4):482–488. https://doi.org/10.1097/mao.0000000000002559

Boel NM, Klokker M (2017) Upper respiratory infections and barotrauma among commercial pilots. *Aerosp Med Hum Perform* 88(1):17–22. https://doi.org/10.3357/amhp.4511.2017

Buchman CA, Doyle WJ, Skoner D, Fireman P, Gwaltney JM (1994) Otologic manifestations of experimental rhinovirus infection. *Laryngoscope* 104(10):1295–1299. https://doi.org/10.1288/00005537-199410000-00021

Chen T, Shih MC, Edwards TS, Nguyen SA, Meyer TA, Soler ZM, et al. (2022) Eustachian tube dysfunction (ETD) in chronic rhinosinusitis with comparison to primary ETD: a systematic review and meta-analysis. *Int Forum Allergy Rhinol* 12(7):942–951. https://doi.org/10.1002/alr.22942

Doyle WJ (2017) A formal description of middle ear pressure-regulation. *Hear Res* 354:73–85. https://doi.org/10.1016/j.heares.2017.08.005

Doyle WJ, Singla A, Banks J, El-Wagaa J, Swarts JD (2014) Pressure chamber tests of Eustachian tube function document lower efficiency in adults with colds when compared to without colds. *Acta Otolaryngol* 134(7):691–697. https://doi.org/10.3109/00016489.2014.892213

Doyle WJ, Skoner DP, Alper CM, et al. (1999) Illness and otological changes during upper respiratory virus infection. *Laryngoscope* 109(2 Pt 1):324–328. https://doi.org/10.1097/00005537-199902000-00027

Doyle WJ, Swarts JD, Banks J, Yuksel S, Alper CM (2011) Transmucosal O2 and CO2 exchange rates for the human middle ear. *Auris Nasus Larynx* 38(6):684–691. https://doi.org/10.1016/j.anl.2011.01.006

Ghadiali SN, Banks J, Swarts JD (2004) Finite element analysis of active Eustachian tube function. *J Appl Physiol* 97(2):648–654. https://doi.org/10.1152/japplphysiol.01250.2003

Kanick SC, Doyle WJ (2005) Barotrauma during air travel: predictions of a mathematical model. *J Appl Physiol* 98(5):1592–1602. https://doi.org/10.1152/japplphysiol.00974.2004

Kikuchi T, Ikeda R, Oshima H, Takata I, Kawase T, Oshima T, Katori Y, Kobayashi T (2017) Effectiveness of Kobayashi plug for 252 ears with chronic patulous Eustachian tube. *Acta Otolaryngol* 137(3):253–258. https://doi.org/10.1080/00016489.2016.1231420

Kobayashi T, Morita M, Yoshioka S, Mizuta K, Ohta S, Kikuchi T, Hayashi T, Kaneko A, Yamaguchi N, Hashimoto S, Kojima H, Murakami S, Takahashi H (2018) Diagnostic criteria for patulous Eustachian tube: a proposal by the Japan Otological Society. *Auris Nasus Larynx* 45(1):1–5. https://doi.org/10.1016/j.anl.2017.09.017

Landolfi A, Torchia F, Autore A, Ciniglio Appiani M, Morgagni F, Ciniglio Appiani G (2009) Acute otitic barotrauma during hypobaric chamber training: prevalence and prevention. *Aviat Space Environ Med* 80(12):1059–1062. https://doi.org/10.3357/asem.2599.2009

Lindfors OH, Ketola KS, Klockars TK, Leino TK, Sinkkonen ST (2021) Middle ear barotraumas in commercial aircrew. *Aerosp Med Hum Perform* 92(3):182–189. https://doi.org/10.3357/amhp.5738.2021

McBride TP, Doyle WJ, Hayden FG, Gwaltney JM Jr (1989) Alterations of the Eustachian tube, middle ear, and nose in rhinovirus infection. *Arch Otolaryngol Head Neck Surg* 115(9):1054–1059. https://doi.org/10.1001/archotol.1989.01860330044014

Moayedi S, Gizaw A, Sweet S, Sethuraman K, Witting M (2025) Pseudoephedrine prophylaxis does not prevent middle ear barotrauma in hyperbaric oxygen therapy. *Undersea Hyperb Med* 52(2):101–107. https://doi.org/10.22462/717

Morgagni F, Autore A, Landolfi A, Ciniglio Appiani M, Marcoccia A (2012) Predictors of ear barotrauma in aircrews exposed to simulated high altitude. *Aviat Space Environ Med* 83(6):594–598. https://doi.org/10.3357/asem.3255.2012

Morgagni F, Autore A, Landolfi A, Torchia F, Ciniglio Appiani G (2010) Altitude chamber related adverse effects among 1241 airmen. *Aviat Space Environ Med* 81(9):873–877. https://doi.org/10.3357/asem.2625.2010

Oshima H, Yoshida M, Shindo H, Hirai R, Oshima T (2025) Clinical characteristics and diagnostic value of symptoms and objective findings in patulous eustachian tube: a large-scale study based on the Japan Otological Society criteria. *Auris Nasus Larynx* 52(6):651–656. https://doi.org/10.1016/j.anl.2025.09.002

Saltelli A, Annoni P, Azzini I, Campolongo F, Ratto M, Tarantola S (2010) Variance based sensitivity analysis of model output: design and estimator for the total sensitivity index. *Comput Phys Commun* 181(2):259–270. https://doi.org/10.1016/j.cpc.2009.09.018

Shindo H, Yoshida M, Hirai R, Oshima T (2025) Clinical characteristics and surgical indications in pediatric patulous Eustachian tube: the importance of habitual sniffing. *Auris Nasus Larynx* 52(5):545–549. https://doi.org/10.1016/j.anl.2025.07.003

Toni T, Welch D, Strelkowa N, Ipsen A, Stumpf MPH (2009) Approximate Bayesian computation scheme for parameter inference and model selection in dynamical systems. *J R Soc Interface* 6(31):187–202. https://doi.org/10.1098/rsif.2008.0172

Wang B, Xu X, Lin J, Jin Z (2019) Dynamic rabbit model of ear barotrauma. *Aerosp Med Hum Perform* 90(8):696–702. https://doi.org/10.3357/amhp.5167.2019
"""

# Find and replace the old references block
old_refs_start = text.find('## References')
old_refs_end = text.find('## Tables')
if old_refs_start != -1 and old_refs_end != -1:
    text = text[:old_refs_start] + ref_block + '\n\n' + text[old_refs_end:]

# 8. Insert title page metadata after the title line
title_line = '# Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training: A Computational Prediction Model Calibrated to the Colombian Aerospace Force Cohort and Externally Validated Against Italian Air Force Cohorts'
title_page = """# Physics-Informed Middle Ear Barotrauma Risk for Hypobaric Chamber Training: A Computational Prediction Model Calibrated to the Colombian Aerospace Force Cohort and Externally Validated Against Italian Air Force Cohorts

**Diego L. Malpica, MD**<sup>1,2,*</sup>
**Marian A. Farfán, MD**<sup>1</sup>

<sup>1</sup> Subdirectorate of Aerospace Sciences, Direction of Aerospace Medicine (DIMAE), Colombian Aerospace Force (Fuerza Aeroespacial Colombiana, FAC), Bogotá, Colombia.
<sup>2</sup> Aerospace Medicine Research Program, DIMAE, Colombian Aerospace Force, Bogotá, Colombia.

<sup>\*</sup> Corresponding author.
Email: diego.malpica@fac.mil.co
ORCID (D.L.M.): 0000-0002-2257-4940

**Author contributions** — D.L.M.: Conceptualization, Methodology, Software, Validation, Formal analysis, Investigation, Data curation, Writing – Original Draft, Writing – Review & Editing, Visualization, Supervision, Project administration. M.A.F.: Methodology, Writing – Review & Editing.

---
"""

text = text.replace(title_line, title_page.strip(), 1)

with open('docs/manuscript_bmb_corrected.md', 'w', encoding='utf-8') as f:
    f.write(text)

print('Corrected manuscript written to docs/manuscript_bmb_corrected.md')
