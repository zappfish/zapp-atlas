/**
 * What the observation form collects, shaped like the form. It is not sent
 * anywhere yet: the experiment page holds the schema's own shapes, and this
 * follows when observations and their images are saved.
 */

export interface ImageValues {
  file?: FileList;
  scaleBar: string;
  scaleBarUnit: string;
  /** What "Other" stands for, when the unit is none of the listed ones. */
  scaleBarUnitOther: string;
  magnification: string;
  resolution: string;
  resolutionUnit: string;
  resolutionUnitOther: string;
  microscope: string;
  notes: string;
}

export interface ObservationValues {
  stage: string;
  stageUnit: string;
  phenotype: string;
  /** ZP CURIE. */
  phenotypeId: string;
  prevalence: string;
  severity: string;
}

export interface Submission {
  images: ImageValues[];
  observations: ObservationValues[];
}

export const emptyImage = (): ImageValues => ({
  scaleBar: "",
  scaleBarUnit: "",
  scaleBarUnitOther: "",
  magnification: "",
  resolution: "",
  resolutionUnit: "",
  resolutionUnitOther: "",
  microscope: "",
  notes: "",
});

export const emptyObservation = (): ObservationValues => ({
  stage: "",
  stageUnit: "hpf",
  phenotype: "",
  phenotypeId: "",
  prevalence: "",
  severity: "",
});
