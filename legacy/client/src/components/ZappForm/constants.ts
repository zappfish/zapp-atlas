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

export const VEHICLE_OPTIONS: { value: string; label: string; meaning?: string }[] = [
  { value: '',                  label: '— Select vehicle —' },
  { value: 'acetone',           label: 'Acetone',                         meaning: 'CHEBI:15347' },
  { value: 'acetonitrile',      label: 'Acetonitrile',                    meaning: 'CHEBI:38472' },
  { value: 'bsa',               label: 'Bovine serum albumin (BSA)',      meaning: 'UMLS:C0036774' },
  { value: 'butanone_mek',      label: 'Butanone (MEK)',                  meaning: 'CHEBI:28398' },
  { value: 'cyclodextrin_hpbcd',label: 'Cyclodextrin (HPBCD)',            meaning: 'CHEBI:23456' },
  { value: 'dimethyl_formamide',label: 'Dimethyl formamide (DMF)',        meaning: 'CHEBI:17741' },
  { value: 'dmso',              label: 'Dimethyl sulfoxide (DMSO)',       meaning: 'CHEBI:28262' },
  { value: 'embryonic_media',   label: 'Embryonic Media (EM/E3)' },
  { value: 'ethanol',           label: 'Ethanol',                         meaning: 'CHEBI:16236' },
  { value: 'glycerol',          label: 'Glycerol',                        meaning: 'CHEBI:17754' },
  { value: 'isopropanol',       label: 'Isopropanol',                     meaning: 'CHEBI:17824' },
  { value: 'methanol',          label: 'Methanol',                        meaning: 'CHEBI:17790' },
  { value: 'methylcellulose',   label: 'Methylcellulose',                 meaning: 'CHEBI:53448' },
  { value: 'pbs',               label: 'Phosphate-buffered saline (PBS)', meaning: 'PUBCHEM.COMPOUND:24978514' },
  { value: 'polyethylene_glycol',label: 'Polyethylene glycol',            meaning: 'CHEBI:30742' },
  { value: 'propylene_glycol',  label: 'Propylene glycol',                meaning: 'CHEBI:16997' },
  { value: 'solketal',          label: 'Solketal',                        meaning: 'UNII:3XK098O8ZW' },
  { value: 'water',             label: 'Water',                           meaning: 'CHEBI:15377' },
  { value: 'other_not_listed', label: 'Other (not listed)' },
];

export const MANUFACTURER_OPTIONS: { value: string; label: string }[] = [
  { value: '',                                         label: '— Select manufacturer —' },
  // Core global suppliers
  { value: 'sigma_aldrich',                            label: 'Sigma-Aldrich' },
  { value: 'merck_kgaa',                               label: 'Merck KGaA' },
  { value: 'millipore_sigma',                          label: 'MilliporeSigma' },
  { value: 'thermo_fisher_scientific',                 label: 'Thermo Fisher Scientific' },
  { value: 'fisher_scientific',                        label: 'Fisher Scientific' },
  { value: 'avantor',                                  label: 'Avantor' },
  { value: 'vwr',                                      label: 'VWR' },
  // Molecular biology / life sciences
  { value: 'new_england_biolabs',                      label: 'New England Biolabs' },
  { value: 'bio_rad_laboratories',                     label: 'Bio-Rad Laboratories' },
  { value: 'promega_corporation',                      label: 'Promega Corporation' },
  { value: 'corning_life_sciences',                    label: 'Corning Life Sciences' },
  { value: 'lonza_group',                              label: 'Lonza Group' },
  // Chemical libraries / screening
  { value: 'tocris_bioscience',                        label: 'Tocris Bioscience' },
  { value: 'cayman_chemical_company',                  label: 'Cayman Chemical Company' },
  { value: 'selleck_chemicals',                        label: 'Selleck Chemicals' },
  { value: 'medchemexpress',                           label: 'MedChemExpress' },
  { value: 'enzo_life_sciences',                       label: 'Enzo Life Sciences' },
  // Zebrafish / aquatic systems
  { value: 'aquaneering_inc',                          label: 'Aquaneering Inc.' },
  { value: 'pentair_aquatic_eco_systems',              label: 'Pentair Aquatic Eco-Systems' },
  { value: 'tecniplast',                               label: 'Tecniplast' },
  { value: 'zebrafish_international_resource_center',  label: 'Zebrafish International Resource Center' },
  // Bulk / industrial chemicals
  { value: 'tokyo_chemical_industry',                  label: 'Tokyo Chemical Industry' },
  { value: 'alfa_aesar',                               label: 'Alfa Aesar' },
  { value: 'acros_organics',                           label: 'Acros Organics' },
  { value: 'honeywell',                                label: 'Honeywell' },
  // Specialty biotech
  { value: 'abcam',                                    label: 'Abcam' },
  { value: 'cell_signaling_technology',                label: 'Cell Signaling Technology' },
  { value: 'genscript',                                label: 'GenScript' },
  { value: 'addgene',                                  label: 'Addgene' },
  // Distributors
  { value: 'thomas_scientific',                        label: 'Thomas Scientific' },
  { value: 'cole_parmer',                              label: 'Cole-Parmer' },
  // Other
  { value: '__other__',                                label: 'Other (specify)' },
];
