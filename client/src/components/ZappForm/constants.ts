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
  { value: 'None',             label: 'None (name only)' },
  { value: 'CHEBI',            label: 'ChEBI' },
  { value: 'PUBCHEM.COMPOUND', label: 'PubChem Compound' },
  { value: 'CAS',              label: 'CAS number' },
  { value: 'INCHIKEY',         label: 'InChIKey' },
  { value: 'HMDB',             label: 'HMDB' },
  { value: 'CHEMBL.COMPOUND',  label: 'ChEMBL' },
  { value: 'UNII',             label: 'UNII' },
  { value: 'MESH',             label: 'MeSH' },
  { value: 'UMLS',             label: 'UMLS' },
  { value: 'DrugCentral',      label: 'DrugCentral' },
  { value: 'GTOPDB',           label: 'GtoPdb' },
  { value: 'RXCUI',            label: 'RxCUI' },
  { value: 'DRUGBANK',         label: 'DrugBank' },
  { value: 'KEGG.COMPOUND',    label: 'KEGG Compound' },
  { value: 'UniProtKB',        label: 'UniProtKB' },
  { value: 'ENSEMBL',          label: 'Ensembl' },
  { value: 'PR',               label: 'Protein Ontology (PR)' },
];

export const DURATION_UNIT_OPTIONS = [
  { value: 'minute', label: 'minute' },
  { value: 'hour', label: 'hour' },
  { value: 'day', label: 'day' }
];
