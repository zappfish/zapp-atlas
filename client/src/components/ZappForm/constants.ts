export const WT_OPTIONS = [
  { value: '', label: 'Select strain/background' },
  { value: 'unspecified WT', label: 'Unspecified WT' },
  { value: 'AB', label: 'AB' },
  { value: 'TU', label: 'TU' },
  { value: 'WIK', label: 'WIK' },
  { value: 'TL', label: 'TL' },
  { value: 'other', label: 'Other (specify in notes)' }
];

export const STAGE_UNIT_OPTIONS = [
  { value: 'hpf', label: 'hpf' },
  { value: 'dpf', label: 'dpf' },
  { value: 'month', label: 'month' }
];

export const EXPOSURE_TYPE_OPTIONS = [
  { value: 'continuous', label: 'Continuous exposure' },
  { value: 'repeated', label: 'Repeated exposures' }
];

export const PATTERN_OPTIONS = [
  { value: 'static', label: 'Sustained - static' },
  { value: 'static_renewal', label: 'Sustained - static renewal' },
  { value: 'flow_through', label: 'Sustained - dynamic (flow through)' }
];

export const SEVERITY_OPTIONS = [
  { value: '', label: 'Select severity' },
  { value: 'mild', label: 'Mild' },
  { value: 'moderate', label: 'Moderate' },
  { value: 'severe', label: 'Severe' }
];

export const SOURCE_TYPE_OPTIONS = [
  { value: '', label: 'Select source type' },
  { value: 'PMID', label: 'PMID' },
  { value: 'DOI', label: 'DOI' },
  { value: 'Other publication', label: 'Other publication' },
  { value: 'Internal database', label: 'Internal database' },
  { value: 'Non-published experimental result', label: 'Non-published experimental result' },
  { value: 'Other', label: 'Other' }
];

export const CONC_UNIT_OPTIONS = [
  { value: 'uM', label: 'μM' },
  { value: 'mg/L', label: 'mg/L' }
];

export const SUBSTANCE_IDTYPE_OPTIONS = [
  { value: 'None', label: 'None (name only)' },
  { value: 'PubChem', label: 'PubChem ID' },
  { value: 'CAS', label: 'CAS number' },
  { value: 'ChEBI', label: 'ChEBI' }
];

export const DURATION_UNIT_OPTIONS = [
  { value: 'hour', label: 'hour' },
  { value: 'min', label: 'min' }
];
