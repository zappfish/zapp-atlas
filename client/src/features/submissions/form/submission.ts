/**
 * What the form collects. Shaped like the form rather than the LinkML schema,
 * which has no slot yet for about twenty of these fields; translating to a
 * Study is the step after the schema catches up.
 */

export interface ImageValues {
  file?: FileList;
  scaleBar: string;
  scaleBarUnit: string;
  /** What "Other" stands for, when the unit is none of the listed ones. */
  scaleBarUnitOther: string;
  magnification: string;
  magnificationUnit: string;
  magnificationUnitOther: string;
  resolution: string;
  resolutionUnit: string;
  resolutionUnitOther: string;
  microscope: string;
  notes: string;
}

export interface ExposureValues {
  substance: string;
  description: string;
  idType: string;
  identifier: string;
  concentration: string;
  concentrationUnit: string;
  supplier: string;
  additionalInformation: string;
  exposureDescription: string;
  route: string;
  regimen: string;
  duration: string;
  durationUnit: string;
  pattern: string[];
  durationPerExposure: string;
  durationPerExposureUnit: string;
  exposureCount: string;
  interval: string;
  intervalUnit: string;
  totalDuration: string;
  totalDurationUnit: string;
  startStage: string;
  startStageUnit: string;
  endStage: string;
  endStageUnit: string;
  notes: string;
}

export interface ControlValues {
  type: string;
  vehicle: string;
  strain: string;
  lineDescription: string;
  rearing: string;
  rearingComment: string;
  phenotypeDescription: string;
  notes: string;
  images: ImageValues[];
}

export interface ObservationValues {
  stage: string;
  stageUnit: string;
  phenotype: string;
  prevalence: string;
  severity: string;
}

export interface Submission {
  title: string;
  provenance: {
    principalInvestigatorOrcid: string;
    principalInvestigatorName: string;
    laboratory: string;
    sourceType: string;
    sourceValue: string;
    notes: string;
  };
  images: ImageValues[];
  fish: {
    existing: string;
    strain: string;
    lineDescription: string;
    additionalCondition: string;
    rearing: string;
    rearingComment: string;
    notes: string;
  };
  exposures: ExposureValues[];
  controls: ControlValues[];
  observations: ObservationValues[];
}

export const emptyImage = (): ImageValues => ({
  scaleBar: "",
  scaleBarUnit: "",
  scaleBarUnitOther: "",
  magnification: "",
  magnificationUnit: "",
  magnificationUnitOther: "",
  resolution: "",
  resolutionUnit: "",
  resolutionUnitOther: "",
  microscope: "",
  notes: "",
});

export const emptyExposure = (): ExposureValues => ({
  substance: "",
  description: "",
  idType: "CAS",
  identifier: "",
  concentration: "",
  concentrationUnit: "µM",
  supplier: "",
  additionalInformation: "",
  exposureDescription: "",
  route: "environment",
  regimen: "Continuous exposure",
  duration: "",
  durationUnit: "minute",
  pattern: [],
  durationPerExposure: "",
  durationPerExposureUnit: "minute",
  exposureCount: "",
  interval: "",
  intervalUnit: "minute",
  totalDuration: "",
  totalDurationUnit: "minute",
  startStage: "",
  startStageUnit: "hpf",
  endStage: "",
  endStageUnit: "hpf",
  notes: "",
});

export const emptyControl = (): ControlValues => ({
  type: "",
  vehicle: "",
  strain: "",
  lineDescription: "",
  rearing: "Standard",
  rearingComment: "",
  phenotypeDescription: "",
  notes: "",
  images: [],
});

export const emptyObservation = (): ObservationValues => ({
  stage: "",
  stageUnit: "hpf",
  phenotype: "",
  prevalence: "",
  severity: "",
});

export const emptySubmission = (): Submission => ({
  title: "",
  provenance: {
    principalInvestigatorOrcid: "",
    principalInvestigatorName: "",
    laboratory: "",
    sourceType: "",
    sourceValue: "",
    notes: "",
  },
  images: [emptyImage()],
  fish: {
    existing: "",
    strain: "",
    lineDescription: "",
    additionalCondition: "",
    rearing: "Standard",
    rearingComment: "",
    notes: "",
  },
  exposures: [emptyExposure()],
  controls: [emptyControl()],
  observations: [emptyObservation()],
});
