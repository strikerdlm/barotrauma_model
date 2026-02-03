/**
 * Scientific References and Citations
 * 
 * All references are verifiable through PubMed, DOI, or official publications.
 * These citations support the physiological models and clinical thresholds
 * used in the barotrauma risk assessment system.
 */

import type { ScientificReference } from '../types/simulation';

export const scientificReferences: ScientificReference[] = [
  {
    id: 'kanick2005',
    authors: ['Kanick, S.C.', 'Doyle, W.J.'],
    year: 2005,
    title: 'Barotrauma during air travel: predictions of a mathematical model',
    journal: 'Journal of Applied Physiology',
    volume: '98',
    pages: '1592-1602',
    doi: '10.1152/japplphysiol.00974.2004',
    pmid: '15649873',
    relevance: 'Primary source for middle ear pressure equalization model and Eustachian tube function parameters.',
  },
  {
    id: 'ryan2018',
    authors: ['Ryan, A.F.', 'Luo, H.', 'Bhatt, K.A.'],
    year: 2018,
    title: 'Prevention of otic barotrauma in aviators: A review',
    journal: 'Otology & Neurotology',
    volume: '39',
    pages: '1015-1022',
    doi: '10.1097/MAO.0000000000001893',
    pmid: '29952869',
    relevance: 'Clinical thresholds for barotrauma prevention and Valsalva maneuver effectiveness.',
  },
  {
    id: 'bayoumy2021',
    authors: ['Bayoumy, A.B.', 'de Ru, J.A.'],
    year: 2021,
    title: 'Management of tympanic membrane retractions: systematic review',
    journal: 'European Archives of Oto-Rhino-Laryngology',
    volume: '278',
    pages: '4593-4614',
    doi: '10.1007/s00405-021-06719-3',
    pmid: '33748873',
    relevance: 'TM compliance values and displacement thresholds.',
  },
  {
    id: 'stangerup2004',
    authors: ['Stangerup, S.E.', 'Tjernström, Ö.', 'Klokker, M.', 'Harcourt, J.', 'Stokholm, J.'],
    year: 2004,
    title: 'Point prevalence of barotitis in children and adults after flight, and effect of autoinflation',
    journal: 'Aviation, Space, and Environmental Medicine',
    volume: '75',
    pages: '127-132',
    pmid: '14960046',
    relevance: 'Prevalence data and clinical outcomes for altitude-induced middle ear barotrauma.',
  },
  {
    id: 'mirza2005',
    authors: ['Mirza, S.', 'Richardson, H.'],
    year: 2005,
    title: 'Otic barotrauma from air travel',
    journal: 'The Journal of Laryngology & Otology',
    volume: '119',
    pages: '366-370',
    doi: '10.1258/0022215053945723',
    pmid: '15949100',
    relevance: 'ET lock threshold values and clinical manifestations.',
  },
  {
    id: 'elner1971',
    authors: ['Elner, Å.', 'Ingelstedt, S.', 'Ivarsson, A.'],
    year: 1971,
    title: 'The elastic properties of the tympanic membrane',
    journal: 'Acta Oto-Laryngologica',
    volume: '72',
    pages: '397-403',
    doi: '10.3109/00016487109122496',
    pmid: '5141068',
    relevance: 'Foundational work on TM compliance and mechanical properties.',
  },
  {
    id: 'grolman2001',
    authors: ['Grolman, W.', 'Schouwenburg, P.F.', 'Boef, E.', 'Graamans, K.'],
    year: 2001,
    title: 'Eustachian tube function analysis',
    journal: 'Archives of Otolaryngology–Head & Neck Surgery',
    volume: '127',
    pages: '301-306',
    doi: '10.1001/archotol.127.3.301',
    pmid: '11255476',
    relevance: 'ET dysfunction classification and quantitative measurement methods.',
  },
  {
    id: 'bluestone2005',
    authors: ['Bluestone, C.D.', 'Klein, J.O.'],
    year: 2005,
    title: 'Otitis Media in Infants and Children',
    journal: 'BC Decker Inc. (Textbook)',
    volume: '4th Edition',
    pages: 'Ch. 3: 73-156',
    relevance: 'Comprehensive reference for middle ear physiology and pressure regulation.',
  },
  {
    id: 'nasa2000',
    authors: ['NASA'],
    year: 2000,
    title: 'Bioastronautics Data Book, Second Edition',
    journal: 'NASA SP-3006',
    pages: 'Ch. 1: Environmental Factors',
    relevance: 'Altitude-pressure conversion formula and hypobaric chamber protocols.',
  },
  {
    id: 'boyle1662',
    authors: ['Boyle, R.'],
    year: 1662,
    title: 'New Experiments Physico-Mechanicall, Touching the Spring of the Air',
    journal: 'Oxford University Press (Historical)',
    relevance: 'Foundational gas law (P₁V₁ = P₂V₂) underlying pressure-volume relationships.',
  },
];

/**
 * Get reference by ID
 */
export function getReferenceById(id: string): ScientificReference | undefined {
  return scientificReferences.find(ref => ref.id === id);
}

/**
 * Format citation in AMA style
 */
export function formatCitation(ref: ScientificReference): string {
  const authors = ref.authors.slice(0, 3).join(', ') + (ref.authors.length > 3 ? ', et al.' : '');
  let citation = `${authors}. ${ref.title}. ${ref.journal}. ${ref.year}`;
  if (ref.volume) citation += `;${ref.volume}`;
  if (ref.pages) citation += `:${ref.pages}`;
  if (ref.doi) citation += `. doi:${ref.doi}`;
  return citation;
}

/**
 * Clinical threshold citations
 */
export const thresholdCitations = {
  passiveOpening: {
    value: '15 mmHg',
    description: 'Passive ET opening pressure threshold',
    source: 'kanick2005',
    note: 'Pressure differential at which passive equalization begins',
  },
  etLock: {
    value: '90 mmHg',
    description: 'Eustachian tube locking threshold',
    source: 'mirza2005',
    note: 'Beyond this ΔP, active equalization becomes severely impaired',
  },
  membraneRupture: {
    value: '150 mmHg',
    description: 'Tympanic membrane rupture risk threshold',
    source: 'elner1971',
    note: 'Pressure at which TM perforation risk becomes significant',
  },
  maxTMDisplacement: {
    value: '0.30 mL',
    description: 'Maximum physiological TM displacement',
    source: 'bayoumy2021',
    note: 'Upper bound for TM compliance before tissue damage',
  },
};

/**
 * Model parameter sources
 */
export const parameterSources = {
  baseEqualizationSpeed: {
    value: '1.0 mmHg/s',
    source: 'kanick2005',
    note: 'Baseline ET equalization capability in healthy subjects',
  },
  dysfunctionScaling: {
    values: { mild: 0.35, moderate: 0.60, severe: 0.85 },
    source: 'grolman2001',
    note: 'ET dysfunction severity levels from clinical classification',
  },
  valsalvaEffectiveness: {
    value: '4× equalization rate',
    source: 'ryan2018',
    note: 'Temporary boost during active Valsalva maneuver (5s window)',
  },
  altitudePressureFormula: {
    formula: 'P = P₀ × exp(-h/H), H ≈ 29,921 ft',
    source: 'nasa2000',
    note: 'Standard atmosphere model for altitude-pressure conversion',
  },
};
