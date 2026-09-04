/*
GENERATED FILE. DO NOT EDIT.
*/

export type ZappEntityId = string;
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
export type ControlImageId = string;
export type PhenotypeTermTermUri = string;
export type ExposureRouteTermUri = string;
export type ExposureTypeTermUri = string;
export type FishId = string;
export type GenotypeId = string;
export type CrossId = string;
export type MutantAlleleId = string;
export type TransgenicAlleleId = string;
export type ResearchGroupId = string;
export type ResearchGroupMemberId = string;
export type ChemicalCabinetEntryId = string;
export type FishTankEntryId = string;
/**
* An enumeration of vehicles used to deliver stressors in exposure events.
*/
export enum VehicleEnum {
    
    /** Acetone */
    acetone = "acetone",
    /** Acetonitrile */
    acetonitrile = "acetonitrile",
    /** Bovine serum albumin (BSA) */
    bsa = "bsa",
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
    /** Other vehicle not in the controlled list */
    other_not_listed = "other_not_listed",
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
    /** Other manufacturer not in the controlled list */
    other_not_listed = "other_not_listed",
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
* How the genotype of the exposed animals was established from the cross. A het × het incross segregates 1:2:1, so an unsorted clutch is a mixture — without this, a reported phenotype prevalence cannot be distinguished from a Mendelian ratio.
*/
export enum ProgenySelectionEnum {
    
    /** Each animal was individually genotyped, so the genotype is certain. */
    genotyped = "genotyped",
    /** Animals were sorted by visible phenotype rather than genotyped. */
    phenotype_sorted = "phenotype_sorted",
    /** Parents were homozygous (or the line is stable), so all progeny are assumed to share the genotype. */
    assumed_uniform = "assumed_uniform",
    /** A segregating clutch used without selection — the stated genotype applies to only a fraction of the animals. */
    segregating = "segregating",
    /** Not stated in the source. */
    unknown = "unknown",
};
/**
* Zygosity of an allele in a fish or in one of its parents. Applies both to the fish's own allele zygosity and to parental (maternal / paternal) zygosity, which matters for maternal-effect phenotypes.
*/
export enum ZygosityEnum {
    
    /** Homozygous — the allele is present on both homologous chromosomes. */
    homozygous = "homozygous",
    /** Heterozygous — the allele is present on one of the two homologous chromosomes. */
    heterozygous = "heterozygous",
    /** Zygosity is unknown or unspecified. */
    unknown = "unknown",
    /** Wild type at this locus — carries zero copies of the allele (ZFIN's parental "W"). Chiefly meaningful for mother/father zygosity: a fish that is itself wild type for an allele would normally just not list it. */
    wild_type = "wild_type",
};
/**
* Common types of sequence alteration for an allele or transgenic feature. Each value is normalized to a Sequence Ontology (SO) term so curators pick a familiar label while the atlas stores the standard identifier.
*/
export enum SequenceAlterationTypeEnum {
    
    /** A single-nucleotide substitution. */
    point_mutation = "point_mutation",
    /** One or more nucleotides replaced by the same number of nucleotides. */
    substitution = "substitution",
    /** Loss of one or more nucleotides. */
    deletion = "deletion",
    /** Gain of one or more nucleotides. */
    insertion = "insertion",
    /** A combined insertion and deletion affecting 2 or more bases. NOTE: SO's canonical label for SO:1000032 is "delins"; "indel" is a registered SO synonym and is the term curators actually use at the bench (e.g. CRISPR indels), so it is deliberately the label shown here. Do not "correct" it. */
    indel = "indel",
    /** A segment reversed in orientation. */
    inversion = "inversion",
    /** One or more copies of a segment added. */
    duplication = "duplication",
    /** An engineered transgenic construct inserted into the genome. */
    transgenic_insertion = "transgenic_insertion",
    /** A substitution involving a different number of nucleotides. */
    complex_substitution = "complex_substitution",
    /** A large chromosomal deletion removing a whole segment (ZFIN's "Deficiency" Df(...) lines, 111 alleles). SO's canonical label for SO:1000029 is "chromosomal_deletion"; "deficiency" is the term zebrafish curators actually use, so it is the label shown here. */
    deficiency = "deficiency",
    /** A segment moved to a different chromosomal location. */
    translocation = "translocation",
    /** An allele carrying several distinct variants under one name (377 ZFIN alleles). Mirrors ZFIN's typing of these records with SO:0001023 — that SO term names the "allele" concept rather than an alteration class, but it is exactly what ZFIN stamps on such features, so mapping it keeps them filterable rather than label-only. */
    multiple_variants = "multiple_variants",
    /** Alteration of unspecified or other type (SO root term). */
    sequence_alteration = "sequence_alteration",
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
    /** Free-text name for a chemical or vehicle that could not be resolved to a standardized identifier. */
    unrecognized_chemical_name?: string,
    /** Human-readable name(s) for the chemical (non-CURIE), used for display and search. The canonical identity is chemical_id. */
    synonym?: string[],
    /** The manufacturer or supplier of the chemical. */
    manufacturer?: string,
    /** Free-text name for a manufacturer or supplier that is not in the controlled ManufacturerEnum list. */
    unrecognized_manufacturer_name?: string,
    /** The dose or concentration of the chemical to which the subject was exposed to. */
    concentration?: QuantityValue,
    /** Additional comments. */
    comment?: string,
}


/**
 * The substance or medium used to deliver a stressor to a subject during an exposure event.
 */
export interface VehicleOfTransmission extends ZappEntity {
    /** The type of vehicle used to deliver a stressor, drawn from a controlled vocabulary. */
    vehicle_type: string,
    /** Chemical identifier (e.g., a CHEBI or other ontology URI) for the chemical. */
    chemical_id?: string,
    /** CAS identifier for the chemical. */
    cas_id?: string,
    /** Free-text name for a chemical or vehicle that could not be resolved to a standardized identifier. */
    unrecognized_chemical_name?: string,
    /** Human-readable name(s) for the chemical (non-CURIE), used for display and search. The canonical identity is chemical_id. */
    synonym?: string[],
    /** The manufacturer or supplier of the chemical. */
    manufacturer?: string,
    /** Free-text name for a manufacturer or supplier that is not in the controlled ManufacturerEnum list. */
    unrecognized_manufacturer_name?: string,
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
 * A zebrafish subject in a study. Mirrors ZFIN's Fish object (GENO:0000525, "effective genotype"): a Fish is the combination of an intrinsic Genotype (mutant alleles, transgenics and wild-type background) and any transient gene-targeting reagents (STRs — morpholinos/CRISPRs). The STR / gene-targeting reagent component is out of scope for ZAPP at this time and is intentionally not modeled yet. The Fish carries its own ZFIN fish identifier (ZDB-FISH-…), which is distinct from the ZDB-GENO-… identifier of its Genotype; either may be absent for lab-specific fish not yet registered with ZFIN.
 */
export interface Fish extends ZappEntity {
    /** Name or label of an entity. */
    name: string,
    /** ZFIN fish identifier (ZDB-FISH-…) for the subject. Distinct from the genotype identifier; may be absent for lab-specific fish not yet registered. */
    fish_zfin_id?: string,
    /** The intrinsic genotype of the fish. */
    genotype?: Genotype,
    /** The mating that produced the experimental animals, and how their genotype was established. Defaults conceptually to an incross of the fish's own line. */
    cross?: Cross,
}


/**
 * The intrinsic genotype of a fish (GENO:0000000) — equivalently, a *line*: the heritable combination of a wild-type genetic background plus any mutant allele(s) and transgenic insertion(s). Carries its own ZFIN genotype identifier (ZDB-GENO-…), which may differ from the fish identifier and may be absent if not yet registered.
Note the recursion: ``background`` is itself a Genotype. A wild-type strain such as AB is simply a Genotype with no alterations (ZFIN models this the same way — a fish's "Background ID" is a ZDB-GENO). There is therefore one concept here, not two: a background *is* a line.
 */
export interface Genotype extends ZappEntity {
    /** ZFIN genotype identifier (ZDB-GENO-…) for the intrinsic genotype. May be absent for genotypes not yet registered with ZFIN. */
    genotype_zfin_id?: string,
    /** Display name of the genotype, e.g. "fgf8a<ti282a/ti282a>; rerea<tb210/tb210>". */
    genotype_name?: string,
    /** Mutant allele(s) carried by the genotype. */
    mutant_allele?: MutantAllele[],
    /** Transgenic insertion(s) carried by the genotype. */
    transgenic_allele?: TransgenicAllele[],
    /** The genetic background this line was bred into — itself a Genotype, normally a wild-type strain such as AB (i.e. a Genotype carrying no alterations). ZFIN models a fish's background the same way, as a ZDB-GENO reference. */
    background?: Genotype,
}


/**
 * How the experimental animals were produced: the mating that generated the clutch, plus how the resulting genotype was established. An incross is represented by the same line on both sides.
This matters because a genotype is not derivable from the parents alone — it follows from the cross *plus* selection. A het × het incross segregates 1:2:1, so an unsorted clutch has no single genotype, and an unqualified phenotype prevalence from such a clutch may be a Mendelian ratio rather than a toxicological effect. ``progeny_selection`` is what distinguishes those.
 */
export interface Cross extends ZappEntity {
    /** The line (Genotype) of the female parent. Determines maternal contribution. */
    maternal_line?: Genotype,
    /** The line (Genotype) of the male parent. */
    paternal_line?: Genotype,
    /** How the genotype of the exposed animals was established from the cross — essential for interpreting phenotype prevalence. */
    progeny_selection?: string,
}


/**
 * A mutant allele (genomic feature) carried by the fish, together with its zygosity and the gene it affects. The allele identifier is a ZFIN genomic feature id (ZDB-ALT-…); ZAPP additionally records the affected gene (affected genomic region).
 */
export interface MutantAllele extends ZappEntity {
    /** ZFIN genomic feature identifier (ZDB-ALT-…) for the allele. */
    allele_id?: string,
    /** The allele symbol / designation, e.g. "ti282a", "fh111", "w200Tg". */
    allele_symbol: string,
    /** The type of sequence alteration the allele represents, chosen from a controlled dropdown of common mutation / alteration types and normalized to a Sequence Ontology (SO) term. ZFIN records this as the feature's SO type. */
    alteration_type?: string,
    /** Identifier of the gene affected by the allele (affected genomic region), typically a ZFIN gene id (ZDB-GENE-…). */
    affected_gene_id?: string,
    /** Symbol of the gene affected by the allele, e.g. "snapc1b". */
    affected_gene_symbol?: string,
    /** Zygosity of the allele in the fish. */
    zygosity?: string,
    /** Zygosity of the allele in the maternal parent. */
    mother_zygosity?: string,
    /** Zygosity of the allele in the paternal parent. */
    father_zygosity?: string,
}


/**
 * A transgenic insertion (genomic feature) carried by the fish, together with its zygosity and the transgenic construct it derives from. The allele identifier is a ZFIN genomic feature id (ZDB-ALT-…); the construct is a ZFIN transgenic construct (ZDB-TGCONSTRCT-…) used mainly for name display. The gene slots record the construct's driver / reporter gene so the atlas can be searched by gene across mutant and transgenic alleles alike.
 */
export interface TransgenicAllele extends ZappEntity {
    /** ZFIN genomic feature identifier (ZDB-ALT-…) for the allele. */
    allele_id?: string,
    /** The allele symbol / designation, e.g. "ti282a", "fh111", "w200Tg". */
    allele_symbol: string,
    /** ZFIN transgenic construct identifier (ZDB-TGCONSTRCT-…) for a transgenic allele. */
    construct_id?: string,
    /** Name of the transgenic construct, e.g. "Tg(mpeg1:YFP)". */
    construct_name?: string,
    /** Type of alteration for a transgenic feature — usually a transgenic insertion (SO:0001218). Normalized to a Sequence Ontology term. */
    alteration_type?: string,
    /** Identifier of the gene whose regulatory region drives the transgene (e.g. fli1 in Tg(fli1:EGFP)), typically a ZFIN gene id (ZDB-GENE-…). */
    affected_gene_id?: string,
    /** Symbol of the transgene's driver / reporter gene, e.g. "fli1". */
    affected_gene_symbol?: string,
    /** Zygosity of the allele in the fish. */
    zygosity?: string,
    /** Zygosity of the allele in the maternal parent. */
    mother_zygosity?: string,
    /** Zygosity of the allele in the paternal parent. */
    father_zygosity?: string,
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



