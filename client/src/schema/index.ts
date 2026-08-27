/*
GENERATED FILE. DO NOT EDIT.
*/

export type ZappEntityId = string;
export type ZfinEntityZfinId = string;
export type StudyId = string;
export type ExperimentId = string;
export type PhenotypeObservationSetId = string;
export type PhenotypeId = string;
export type ControlId = string;
export type ExposureEventId = string;
export type RegimenId = string;
export type StressorChemicalId = string;
export type VehicleOfTransmissionId = string;
export type ImageId = string;
export type ImageLabelId = string;
export type ControlImageId = string;
export type PhenotypeTermTermUri = string;
export type ExposureRouteTermUri = string;
export type ExposureTypeTermUri = string;
export type FishZfinId = string;
export type ResearchGroupId = string;
export type ResearchGroupMemberId = string;
export type ChemicalCabinetEntryId = string;
export type FishTankEntryId = string;
/**
* An enumeration of how much of the organism an image shows.
*/
export enum ImageScopeEnum {
    
    /** The entire fish, head to tail. */
    whole_organism = "whole_organism",
    /** A specific region, organ, or structure (e.g., head, heart, fin, eye). */
    partial_organism = "partial_organism",
};
/**
* An enumeration of image acquisition modalities.
*/
export enum ImageModalityEnum {
    
    /** Brightfield microscopy. */
    brightfield = "brightfield",
    /** Fluorescence microscopy. */
    fluorescence = "fluorescence",
    /** Another acquisition modality, described in the image comment. */
    other = "other",
};
/**
* An enumeration of kinds of reagents or signals shown in an image.
*/
export enum LabelKindEnum {
    
    /** A transgenic reporter, e.g. Tg(-6.35drl:EGFP). */
    transgene_reporter = "transgene_reporter",
    /** An in situ hybridization probe, e.g. myl7. */
    ish_probe = "ish_probe",
    /** An antibody used for immunostaining. */
    antibody = "antibody",
    /** A chemical stain, e.g. Alcian blue or Alizarin red. */
    chemical_stain = "chemical_stain",
    /** A vital dye, e.g. BODIPY or acridine orange. */
    vital_dye = "vital_dye",
    /** Another kind of label, described in the label comment. */
    other = "other",
};
/**
* An enumeration of permission levels within a research group.
*/
export enum ResearchGroupRoleEnum {
    
    /** Can manage group membership as well as the group's data. */
    admin = "admin",
    /** Can edit the group's data. */
    member = "member",
};
/**
* An enumeration of severity levels for phenotypes.
*/
export enum SeverityEnum {
    
    /** Mild severity */
    mild = "mild",
    /** Moderate severity */
    moderate = "moderate",
    /** Severe severity */
    severe = "severe",
};
/**
* An enumeration of exposure regimen types.
*/
export enum ExposureRegimenTypeEnum {
    
    /** Continuous exposure */
    continuous = "continuous",
    /** Repeated exposure */
    repeated = "repeated",
};
/**
* An enumeration of vehicles used to deliver stressors in exposure events.
*/
export enum VehicleEnum {
    
    /** Acetone */
    acetone = "acetone",
    /** Acetonitrile */
    acetonitrile = "acetonitrile",
    /** Albumin (BSA) */
    albumin_bsa = "albumin_bsa",
    /** Butanone (MEK) */
    butanone_mek = "butanone_mek",
    /** Cyclodextrin (HPBCD) */
    cyclodextrin_hpbcd = "cyclodextrin_hpbcd",
    /** Dimethyl formamide (DMF) */
    dimethyl_formamide = "dimethyl_formamide",
    /** Dimethyl sulfoxide (DMSO) */
    dmso = "dmso",
    /** Embryonic Media (EM/E3) */
    embryonic_media = "embryonic_media",
    /** Ethanol */
    ethanol = "ethanol",
    /** Glycerol */
    glycerol = "glycerol",
    /** Isopropanol */
    isopropanol = "isopropanol",
    /** Methanol */
    methanol = "methanol",
    /** Methylcellulose */
    methylcellulose = "methylcellulose",
    /** Phosphate-buffered saline (PBS) */
    pbs = "pbs",
    /** Polyethylene glycol */
    polyethylene_glycol = "polyethylene_glycol",
    /** Propylene glycol */
    propylene_glycol = "propylene_glycol",
    /** Solketal */
    solketal = "solketal",
    /** Water */
    water = "water",
};
/**
* An enumeration of manufacturers and suppliers of chemicals used in exposure events.
*/
export enum ManufacturerEnum {
    
    /** Sigma-Aldrich */
    sigma_aldrich = "sigma_aldrich",
    /** Merck KGaA */
    merck_kgaa = "merck_kgaa",
    /** MilliporeSigma */
    millipore_sigma = "millipore_sigma",
    /** Thermo Fisher Scientific */
    thermo_fisher_scientific = "thermo_fisher_scientific",
    /** Fisher Scientific */
    fisher_scientific = "fisher_scientific",
    /** Avantor */
    avantor = "avantor",
    /** VWR */
    vwr = "vwr",
    /** New England Biolabs */
    new_england_biolabs = "new_england_biolabs",
    /** Bio-Rad Laboratories */
    bio_rad_laboratories = "bio_rad_laboratories",
    /** Promega Corporation */
    promega_corporation = "promega_corporation",
    /** Corning Life Sciences */
    corning_life_sciences = "corning_life_sciences",
    /** Lonza Group */
    lonza_group = "lonza_group",
    /** Tocris Bioscience */
    tocris_bioscience = "tocris_bioscience",
    /** Cayman Chemical Company */
    cayman_chemical_company = "cayman_chemical_company",
    /** Selleck Chemicals */
    selleck_chemicals = "selleck_chemicals",
    /** MedChemExpress */
    medchemexpress = "medchemexpress",
    /** Enzo Life Sciences */
    enzo_life_sciences = "enzo_life_sciences",
    /** Aquaneering Inc. */
    aquaneering_inc = "aquaneering_inc",
    /** Pentair Aquatic Eco-Systems */
    pentair_aquatic_eco_systems = "pentair_aquatic_eco_systems",
    /** Tecniplast */
    tecniplast = "tecniplast",
    /** Zebrafish International Resource Center */
    zebrafish_international_resource_center = "zebrafish_international_resource_center",
    /** Tokyo Chemical Industry */
    tokyo_chemical_industry = "tokyo_chemical_industry",
    /** Alfa Aesar */
    alfa_aesar = "alfa_aesar",
    /** Acros Organics */
    acros_organics = "acros_organics",
    /** Honeywell */
    honeywell = "honeywell",
    /** Abcam */
    abcam = "abcam",
    /** Cell Signaling Technology */
    cell_signaling_technology = "cell_signaling_technology",
    /** GenScript */
    genscript = "genscript",
    /** Addgene */
    addgene = "addgene",
    /** Thomas Scientific */
    thomas_scientific = "thomas_scientific",
    /** Cole-Parmer */
    cole_parmer = "cole_parmer",
};


/**
 * Internal entities with auto-generated integer IDs.
 */
export interface ZappEntity {
    /** Auto-generated integer identifier. */
    id: number,
}


/**
 * Entities representing ontology terms with URI identifiers.
 */
export interface OntologyEntity {
}


/**
 * Entities with ZFIN database identifiers.
 */
export interface ZfinEntity {
    /** ZFIN database identifier. */
    zfin_id: string,
}


/**
 * A toxicological investigation, including the experimental conditions and phenotypic outcomes, with information provenance.
 */
export interface Study extends ZappEntity {
    /** The experiment in a study. */
    experiment?: Experiment[],
    /** The publication identifier (e.g., PMID, DOI) for the study or "not published" if the study is unpublished. */
    publication?: string,
    /** ORCID identifier of the indidvidual submitting the study data. */
    annotator?: string[],
    /** ZFIN lab identifier of the laboratory that produced the study data. */
    lab?: string,
}


/**
 * A group of observations (phenotypic outcomes and their control) that are linked by a common exposure event and subject, and that are part of a study.
 */
export interface Experiment extends ZappEntity {
    /** An indication of whether the subject was maintained under standard conditions, which are the established, consistent environmental and husbandry parameters (such as temperature, lighting, diet, and housing) designed to minimize variability and ensure reproducibility in experiments. */
    standard_rearing_condition?: boolean,
    /** Comments on rearing conditions, for example, about how conditions deviated from standard parameters. */
    rearing_condition_comment?: string,
    /** The fish subject of the experiment. */
    fish?: Fish,
    /** An observation that serves as the reference for assessing phenotypic outcome. */
    control?: Control[],
    /** The exposure event in an experiment. */
    exposure_event?: ExposureEvent[],
}


/**
 * An observation set containing control and phenotypic outcome resulting from an exposure event.
 */
export interface PhenotypeObservationSet extends ZappEntity {
    /** Images associated with this observation. */
    image?: Image[],
    /** The phenotype observed. */
    phenotype?: Phenotype[],
    /** Image associated with this control. */
    control_image?: ControlImage[],
}


/**
 * Any measurable or visible trait change in the subject as a result of exposure.
 */
export interface Phenotype extends ZappEntity {
    /** The developmental stage of fish when the phenotype was observed. */
    stage?: string,
    /** The percentage of subject exhibiting this phenotype. */
    prevalence?: QuantityValue,
    /** The intensity of the observed phenotype. */
    severity?: string,
    /** The phenotype ontology term. */
    phenotype_term_id?: PhenotypeTerm,
}


/**
 * A subject serves as a reference for assessing phenotypic outcome in the phenotype observation set.
 */
export interface Control extends ZappEntity {
    /** Type of control (e.g., wildtype vs mutant, treated vs untreated). */
    control_type?: string,
    /** The vehicle used in a control. */
    vehicle_if_treated?: VehicleOfTransmission,
    /** Additional comments. */
    comment?: string,
    /** Image associated with this control. */
    control_image?: ControlImage[],
}


/**
 * An occurrence in a study where a subject is exposed to a stressor under defined conditions.
 */
export interface ExposureEvent extends ZappEntity {
    /** Substance, chemical or toxicant that elicits a response (a phenotype) in a subject when encountered through exposure. */
    stressor?: StressorChemical[],
    /** The substance or medium used to deliver a stressor. */
    vehicle?: VehicleOfTransmission[],
    /** The route of exposure. */
    route?: ExposureRoute,
    /** The regimen for the exposure. */
    regimen?: Regimen,
    /** The developmental stage of fish when exposure started. */
    exposure_start_stage?: string,
    /** The developmental stage of fish when exposure ended. */
    exposure_end_stage?: string,
    /** Additional comments. */
    comment?: string,
    /** An instance of exposure specifying the type of stressor a subject was exposed to. */
    exposure_type?: ExposureType,
    /** Additional information about the conditions under which exposure event occurred. */
    additional_exposure_condition?: string,
    /** The phenotype observation resulting from an exposure event. */
    phenotype_observation?: PhenotypeObservationSet[],
}


/**
 * The schedule and pattern of an exposure event.
 */
export interface Regimen extends ZappEntity {
    /** The type of exposure regimen (e.g., continuous or repeated). */
    exposure_regimen_type?: string,
    /** Interval between individual exposures. */
    interval_between_individual_exposures?: QuantityValue,
    /** Time between first and last individual exposure. */
    total_exposure_duration?: QuantityValue,
    /** Individual exposure duration. */
    individual_exposure_duration?: QuantityValue,
    /** Total number of individual exposures. */
    number_of_individual_exposure?: number,
}


/**
 * A chemical that elicits a response (a phenotype) in a subject when encountered through exposure.
 */
export interface StressorChemical extends ZappEntity {
    /** Chemical identifier (e.g., a CHEBI or other ontology URI) for the chemical. */
    chemical_id?: string,
    /** CAS identifier for the chemical. */
    cas_id?: string,
    /** Name of the chemical. */
    chemical_name?: string,
    /** Other names for the chemical. */
    synonym?: string[],
    /** The manufacturer or supplier of the chemical. */
    manufacturer?: string,
    /** The dose or concentration of the chemical to which the subject was exposed to. */
    concentration: QuantityValue,
    /** Additional comments. */
    comment?: string,
}


/**
 * The substance or medium used to deliver a stressor to a subject during an exposure event.
 */
export interface VehicleOfTransmission extends ZappEntity {
    /** The type of vehicle used to deliver a stressor, drawn from a controlled vocabulary. */
    vehicle_type: string,
    /** The manufacturer or supplier of the chemical. */
    manufacturer?: string,
    /** The dose or concentration of the chemical to which the subject was exposed to. */
    concentration?: QuantityValue,
    /** Additional comments. */
    comment?: string,
}


/**
 * An image associated with a phenotype observation.
 */
export interface Image extends ZappEntity {
    /** The factor by which a microscope enlarges the apparent size of a subject compared to its actual size. */
    magnification?: string,
    /** The level of detail in the image. */
    resolution?: string,
    /** Scale bar information, including the physical length it represents and the unit of measurement. */
    scale_bar?: string,
    /** Whether the image shows the entire organism or only a region, organ, or structure. Phenotype annotations on a partial-organism image should be limited to what is visible in the imaged region. */
    image_scope?: string,
    /** How the image was acquired. The biology shown (reporters, probes, antibodies, stains) is carried by the label list, not the modality. */
    modality?: string,
    /** The labels (reagents or signals) shown in this image. */
    label?: ImageLabel[],
}


/**
 * A reagent or signal shown in an image: a transgenic reporter, in situ probe, antibody, chemical stain, or vital dye. An image may carry several (multi-channel fluorescence, Alcian blue + Alizarin red double staining).
 */
export interface ImageLabel extends ZappEntity {
    /** The kind of reagent or signal this label is. */
    label_kind: string,
    /** Name of the label as reported, e.g. Tg(-6.35drl:EGFP), myl7, anti-MF20, Alcian blue. */
    name: string,
    /** Identifier for the label where one exists, e.g. a ZFIN construct ID for a transgenic reporter (ZFIN:ZDB-TGCONSTRCT-160129-1), a ZFIN gene ID for an in situ probe (ZFIN:ZDB-GENE-991019-3), an RRID for an antibody, or a CHEBI ID for a chemical stain. */
    label_id?: string,
    /** Additional comments. */
    comment?: string,
}


/**
 * An image associated with a control, taken at the same developmental stage as the corresponding phenotype observation.
 */
export interface ControlImage extends ZappEntity {
    /** Foreign key reference to the PhenotypeObservationSet uuid (for database representation). */
    phenotype_id?: string,
    /** The factor by which a microscope enlarges the apparent size of a subject compared to its actual size. */
    magnification?: string,
    /** The level of detail in the image. */
    resolution?: string,
    /** Scale bar information, including the physical length it represents and the unit of measurement. */
    scale_bar?: string,
    /** Comments about the phenotype in the control image. */
    phenotype_comments?: string,
}


/**
 * A phenotype ontology term from the Zebrafish Phenotype ontology (ZP).
 */
export interface PhenotypeTerm extends OntologyEntity {
    /** The URI of the phenotype ontology term. */
    term_uri: string,
    /** The human-readable label for the phenotype ontology term. */
    term_label?: string,
}


/**
 * A route-of-exposure term. Term URIs are expected to be reachable from
EXO:0000154 (route of exposure) in the EXO ontology.

 */
export interface ExposureRoute extends OntologyEntity {
    /** The URI of the phenotype ontology term. */
    term_uri: string,
    /** The human-readable label for the phenotype ontology term. */
    term_label: string,
}


/**
 * An exposure-type term from ECTO.

 */
export interface ExposureType extends OntologyEntity {
    /** The URI of the phenotype ontology term. */
    term_uri: string,
    /** The human-readable label for the phenotype ontology term. */
    term_label: string,
}


/**
 * Zebrafish used as subject in the study.
 */
export interface Fish extends ZfinEntity {
    /** Name or label of an entity. */
    name: string,
}


/**
 * A named collection of users that have shared editing access.
 */
export interface ResearchGroup extends ZappEntity {
    /** Name or label of an entity. */
    name: string,
}


/**
 * Membership of an ORCID identity in a research group.
 */
export interface ResearchGroupMember extends ZappEntity {
    /** The research group an entry belongs to. */
    research_group: ResearchGroupId,
    /** ORCID identifier of a research group member. */
    member: string,
    /** A member's permission level within a research group. */
    role: string,
}


/**
 * A chemical a research group keeps on hand. Recorded once, then reused to pre-fill curation instead of re-searching the chemical each time.
 */
export interface ChemicalCabinetEntry extends ZappEntity {
    /** The research group an entry belongs to. */
    research_group: ResearchGroupId,
    /** Chemical identifier (e.g., a CHEBI or other ontology URI) for the chemical. */
    chemical_id: string,
}


/**
 * A fish line a research group maintains. Recorded once, then reused to pre-fill curation instead of re-searching the line each time.
 */
export interface FishTankEntry extends ZappEntity {
    /** The research group an entry belongs to. */
    research_group: ResearchGroupId,
    /** The fish line the group maintains. */
    fish: Fish,
}


/**
 * A value of an attribute that is quantitative and measurable, expressed as a combination of a unit and a numeric value
 */
export interface QuantityValue {
    /** The unit of the quantity value. */
    unit?: string,
    /** The numeric value of the quantity value. */
    numeric_value?: string,
}



