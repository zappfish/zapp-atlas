/**
 * Hand-written mirror of the API read shapes. Narrow to what the UI
 * currently uses; expand as more pages come online.
 */

export interface QuantityValue {
  numeric_value?: string | null;
  unit?: string | null;
}

export interface Fish {
  zfin_id: string;
  name: string;
}

export interface ChemicalEntity {
  uri?: string | null;
  chebi_id?: string | null;
  cas_id?: string | null;
  chemical_name?: string | null;
}

export interface StressorChemical {
  id: number;
  chemical_id?: ChemicalEntity | null;
  concentration?: QuantityValue | null;
  manufacturer?: string | null;
}

export interface PhenotypeTerm {
  term_uri: string;
  term_label?: string | null;
}

export interface Phenotype {
  id: number;
  stage?: string | null;
  severity?: 'mild' | 'moderate' | 'severe' | null;
  prevalence?: QuantityValue | null;
  phenotype_term_id?: PhenotypeTerm | null;
}

export interface Image {
  id: number;
  magnification?: string | null;
  resolution?: string | null;
  scale_bar?: string | null;
}

export interface PhenotypeObservationSet {
  id: number;
  phenotype?: Phenotype[] | null;
  image?: Image[] | null;
}

export interface OntologyTerm {
  term_uri: string;
  term_label?: string | null;
}

export interface ExposureEvent {
  id: number;
  route?: string | null;
  route_label?: string | null;
  exposure_start_stage?: string | null;
  exposure_end_stage?: string | null;
  exposure_type?: string | null;
  exposure_type_label?: string | null;
  comment?: string | null;
  stressor?: StressorChemical[] | null;
  phenotype_observation?: PhenotypeObservationSet[] | null;
}

export interface Control {
  id: number;
  control_type?: string | null;
  vehicle_if_treated?: string | null;
  comment?: string | null;
}

export interface Experiment {
  id: number;
  standard_rearing_condition?: boolean | null;
  rearing_condition_comment?: string | null;
  fish?: Fish | null;
  control?: Control[] | null;
  exposure_event?: ExposureEvent[] | null;
}

export interface Study {
  id: number;
  publication?: string | null;
  lab?: string | null;
  annotator?: string[] | null;
  experiment?: Experiment[] | null;
}
