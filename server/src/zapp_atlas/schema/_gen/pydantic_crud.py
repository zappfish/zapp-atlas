# GENERATED FILE. DO NOT EDIT.
from __future__ import annotations

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal
from enum import Enum
from typing import (
    Any,
    ClassVar,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    SerializationInfo,
    SerializerFunctionWrapHandler,
    field_validator,
    model_serializer
)


metamodel_version = "1.7.0"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        serialize_by_alias = True,
        validate_by_name = True,
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )





class LinkMLMeta(RootModel):
    root: dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root



class ReadBaseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )
linkml_meta = LinkMLMeta({'default_prefix': 'zebrafish_toxicology_atlas_schema',
     'default_range': 'string',
     'description': 'Schema to represent metadatcha associated with the Zebrafish '
                    'Toxicology Atlas',
     'id': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema',
     'imports': ['linkml:types', 'chemical_enums'],
     'license': 'MIT',
     'name': 'zebrafish-toxicology-atlas-schema',
     'prefixes': {'CAS': {'prefix_prefix': 'CAS',
                          'prefix_reference': 'https://commonchemistry.cas.org/detail?cas_rn='},
                  'CHEBI': {'prefix_prefix': 'CHEBI',
                            'prefix_reference': 'http://purl.obolibrary.org/obo/CHEBI_'},
                  'ECTO': {'prefix_prefix': 'ECTO',
                           'prefix_reference': 'http://purl.obolibrary.org/obo/ECTO_'},
                  'EXO': {'prefix_prefix': 'EXO',
                          'prefix_reference': 'http://purl.obolibrary.org/obo/EXO_'},
                  'GENO': {'prefix_prefix': 'GENO',
                           'prefix_reference': 'http://purl.obolibrary.org/obo/GENO_'},
                  'ORCID': {'prefix_prefix': 'ORCID',
                            'prefix_reference': 'https://orcid.org/'},
                  'PATO': {'prefix_prefix': 'PATO',
                           'prefix_reference': 'http://purl.obolibrary.org/obo/PATO_'},
                  'PUBCHEM.COMPOUND': {'prefix_prefix': 'PUBCHEM.COMPOUND',
                                       'prefix_reference': 'https://identifiers.org/pubchem.compound/'},
                  'SO': {'prefix_prefix': 'SO',
                         'prefix_reference': 'http://purl.obolibrary.org/obo/SO_'},
                  'UMLS': {'prefix_prefix': 'UMLS',
                           'prefix_reference': 'https://uts.nlm.nih.gov/uts/umls/concept/'},
                  'UNII': {'prefix_prefix': 'UNII',
                           'prefix_reference': 'https://fdasis.nlm.nih.gov/srs/unii/'},
                  'ZFIN': {'prefix_prefix': 'ZFIN',
                           'prefix_reference': 'https://zfin.org/'},
                  'ZP': {'prefix_prefix': 'ZP',
                         'prefix_reference': 'http://purl.obolibrary.org/obo/ZP_'},
                  'biolink': {'prefix_prefix': 'biolink',
                              'prefix_reference': 'https://w3id.org/biolink/'},
                  'example': {'prefix_prefix': 'example',
                              'prefix_reference': 'https://example.org/'},
                  'linkml': {'prefix_prefix': 'linkml',
                             'prefix_reference': 'https://w3id.org/linkml/'},
                  'schema': {'prefix_prefix': 'schema',
                             'prefix_reference': 'http://schema.org/'},
                  'zebrafish_toxicology_atlas_schema': {'prefix_prefix': 'zebrafish_toxicology_atlas_schema',
                                                        'prefix_reference': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema/'}},
     'see_also': ['https://sierra-moxon.github.io/zebrafish-toxicology-atlas-schema'],
     'source_file': 'src/zapp_atlas/schema/zebrafish_toxicology_atlas_schema.yaml',
     'title': 'zebrafish-toxicology-atlas-schema'} )

class VehicleEnum(str, Enum):
    """
    An enumeration of vehicles used to deliver stressors in exposure events.
    """
    acetone = "acetone"
    """
    Acetone
    """
    acetonitrile = "acetonitrile"
    """
    Acetonitrile
    """
    bsa = "bsa"
    """
    Bovine serum albumin (BSA)
    """
    butanone_mek = "butanone_mek"
    """
    Butanone (MEK)
    """
    cyclodextrin_hpbcd = "cyclodextrin_hpbcd"
    """
    Cyclodextrin (HPBCD)
    """
    dimethyl_formamide = "dimethyl_formamide"
    """
    Dimethyl formamide (DMF)
    """
    dmso = "dmso"
    """
    Dimethyl sulfoxide (DMSO)
    """
    embryonic_media = "embryonic_media"
    """
    Embryonic Media (EM/E3)
    """
    ethanol = "ethanol"
    """
    Ethanol
    """
    glycerol = "glycerol"
    """
    Glycerol
    """
    isopropanol = "isopropanol"
    """
    Isopropanol
    """
    methanol = "methanol"
    """
    Methanol
    """
    methylcellulose = "methylcellulose"
    """
    Methylcellulose
    """
    pbs = "pbs"
    """
    Phosphate-buffered saline (PBS)
    """
    polyethylene_glycol = "polyethylene_glycol"
    """
    Polyethylene glycol
    """
    propylene_glycol = "propylene_glycol"
    """
    Propylene glycol
    """
    solketal = "solketal"
    """
    Solketal
    """
    water = "water"
    """
    Water
    """
    other_not_listed = "other_not_listed"
    """
    Other vehicle not in the controlled list
    """


class ManufacturerEnum(str, Enum):
    """
    An enumeration of manufacturers and suppliers of chemicals used in exposure events.
    """
    sigma_aldrich = "sigma_aldrich"
    """
    Sigma-Aldrich
    """
    merck_kgaa = "merck_kgaa"
    """
    Merck KGaA
    """
    millipore_sigma = "millipore_sigma"
    """
    MilliporeSigma
    """
    thermo_fisher_scientific = "thermo_fisher_scientific"
    """
    Thermo Fisher Scientific
    """
    fisher_scientific = "fisher_scientific"
    """
    Fisher Scientific
    """
    avantor = "avantor"
    """
    Avantor
    """
    vwr = "vwr"
    """
    VWR
    """
    new_england_biolabs = "new_england_biolabs"
    """
    New England Biolabs
    """
    bio_rad_laboratories = "bio_rad_laboratories"
    """
    Bio-Rad Laboratories
    """
    promega_corporation = "promega_corporation"
    """
    Promega Corporation
    """
    corning_life_sciences = "corning_life_sciences"
    """
    Corning Life Sciences
    """
    lonza_group = "lonza_group"
    """
    Lonza Group
    """
    tocris_bioscience = "tocris_bioscience"
    """
    Tocris Bioscience
    """
    cayman_chemical_company = "cayman_chemical_company"
    """
    Cayman Chemical Company
    """
    selleck_chemicals = "selleck_chemicals"
    """
    Selleck Chemicals
    """
    medchemexpress = "medchemexpress"
    """
    MedChemExpress
    """
    enzo_life_sciences = "enzo_life_sciences"
    """
    Enzo Life Sciences
    """
    aquaneering_inc = "aquaneering_inc"
    """
    Aquaneering Inc.
    """
    pentair_aquatic_eco_systems = "pentair_aquatic_eco_systems"
    """
    Pentair Aquatic Eco-Systems
    """
    tecniplast = "tecniplast"
    """
    Tecniplast
    """
    zebrafish_international_resource_center = "zebrafish_international_resource_center"
    """
    Zebrafish International Resource Center
    """
    tokyo_chemical_industry = "tokyo_chemical_industry"
    """
    Tokyo Chemical Industry
    """
    alfa_aesar = "alfa_aesar"
    """
    Alfa Aesar
    """
    acros_organics = "acros_organics"
    """
    Acros Organics
    """
    honeywell = "honeywell"
    """
    Honeywell
    """
    abcam = "abcam"
    """
    Abcam
    """
    cell_signaling_technology = "cell_signaling_technology"
    """
    Cell Signaling Technology
    """
    genscript = "genscript"
    """
    GenScript
    """
    addgene = "addgene"
    """
    Addgene
    """
    thomas_scientific = "thomas_scientific"
    """
    Thomas Scientific
    """
    cole_parmer = "cole_parmer"
    """
    Cole-Parmer
    """
    other_not_listed = "other_not_listed"
    """
    Other manufacturer not in the controlled list
    """


class ResearchGroupRoleEnum(str, Enum):
    """
    An enumeration of permission levels within a research group.
    """
    admin = "admin"
    """
    Can manage group membership as well as the group's data.
    """
    member = "member"
    """
    Can edit the group's data.
    """


class ProgenySelectionEnum(str, Enum):
    """
    How the genotype of the exposed animals was established from the cross. A het × het incross segregates 1:2:1, so an unsorted clutch is a mixture — without this, a reported phenotype prevalence cannot be distinguished from a Mendelian ratio.
    """
    genotyped = "genotyped"
    """
    Each animal was individually genotyped, so the genotype is certain.
    """
    phenotype_sorted = "phenotype_sorted"
    """
    Animals were sorted by visible phenotype rather than genotyped.
    """
    assumed_uniform = "assumed_uniform"
    """
    Parents were homozygous (or the line is stable), so all progeny are assumed to share the genotype.
    """
    segregating = "segregating"
    """
    A segregating clutch used without selection — the stated genotype applies to only a fraction of the animals.
    """
    unknown = "unknown"
    """
    Not stated in the source.
    """


class ZygosityEnum(str, Enum):
    """
    Zygosity of an allele in a fish or in one of its parents. Applies both to the fish's own allele zygosity and to parental (maternal / paternal) zygosity, which matters for maternal-effect phenotypes.
    """
    homozygous = "homozygous"
    """
    Homozygous — the allele is present on both homologous chromosomes.
    """
    heterozygous = "heterozygous"
    """
    Heterozygous — the allele is present on one of the two homologous chromosomes.
    """
    unknown = "unknown"
    """
    Zygosity is unknown or unspecified.
    """
    wild_type = "wild_type"
    """
    Wild type at this locus — carries zero copies of the allele (ZFIN's parental "W"). Chiefly meaningful for mother/father zygosity: a fish that is itself wild type for an allele would normally just not list it.
    """


class SequenceAlterationTypeEnum(str, Enum):
    """
    Common types of sequence alteration for an allele or transgenic feature. Each value is normalized to a Sequence Ontology (SO) term so curators pick a familiar label while the atlas stores the standard identifier.
    """
    point_mutation = "point_mutation"
    """
    A single-nucleotide substitution.
    """
    substitution = "substitution"
    """
    One or more nucleotides replaced by the same number of nucleotides.
    """
    deletion = "deletion"
    """
    Loss of one or more nucleotides.
    """
    insertion = "insertion"
    """
    Gain of one or more nucleotides.
    """
    indel = "indel"
    """
    A combined insertion and deletion affecting 2 or more bases. NOTE: SO's canonical label for SO:1000032 is "delins"; "indel" is a registered SO synonym and is the term curators actually use at the bench (e.g. CRISPR indels), so it is deliberately the label shown here. Do not "correct" it.
    """
    inversion = "inversion"
    """
    A segment reversed in orientation.
    """
    duplication = "duplication"
    """
    One or more copies of a segment added.
    """
    transgenic_insertion = "transgenic_insertion"
    """
    An engineered transgenic construct inserted into the genome.
    """
    complex_substitution = "complex_substitution"
    """
    A substitution involving a different number of nucleotides.
    """
    sequence_alteration = "sequence_alteration"
    """
    Alteration of unspecified or other type (SO root term).
    """


class SeverityEnum(str, Enum):
    """
    An enumeration of severity levels for phenotypes.
    """
    mild = "mild"
    """
    Mild severity
    """
    moderate = "moderate"
    """
    Moderate severity
    """
    severe = "severe"
    """
    Severe severity
    """


class ExposureRegimenTypeEnum(str, Enum):
    """
    An enumeration of exposure regimen types.
    """
    continuous = "continuous"
    """
    Continuous exposure
    """
    repeated = "repeated"
    """
    Repeated exposure
    """



class ZappEntity(ConfiguredBaseModel):
    """
    Internal entities with auto-generated integer IDs.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True,
         'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema'})

    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class OntologyEntity(ConfiguredBaseModel):
    """
    Entities representing ontology terms with URI identifiers.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'abstract': True,
         'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema'})

    pass


class Study(ZappEntity):
    """
    A toxicological investigation, including the experimental conditions and phenotypic outcomes, with information provenance.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema'})

    experiment: Optional[list[Experiment]] = Field(default=None, description="""The experiment in a study.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })
    publication: Optional[str] = Field(default=None, description="""The publication identifier (e.g., PMID, DOI) for the study or \"not published\" if the study is unpublished.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })
    annotator: Optional[list[str]] = Field(default=None, description="""ORCID identifier of the indidvidual submitting the study data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })
    lab: Optional[str] = Field(default=None, description="""ZFIN lab identifier of the laboratory that produced the study data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })

    @field_validator('annotator')
    def pattern_annotator(cls, v):
        pattern=re.compile(r"^ORCID:[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid annotator format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid annotator format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('lab')
    def pattern_lab(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-LAB-[0-9]+-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid lab format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid lab format: {v}"
            raise ValueError(err_msg)
        return v


class StudyCreate(ConfiguredBaseModel):
    """
    Create schema for Study — id is server-generated.
    """
    experiment: Optional[list[ExperimentCreate]] = Field(default=None, description="""The experiment in a study.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })
    publication: Optional[str] = Field(default=None, description="""The publication identifier (e.g., PMID, DOI) for the study or \"not published\" if the study is unpublished.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })
    annotator: Optional[list[str]] = Field(default=None, description="""ORCID identifier of the indidvidual submitting the study data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })
    lab: Optional[str] = Field(default=None, description="""ZFIN lab identifier of the laboratory that produced the study data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })

    @field_validator('annotator')
    def pattern_annotator(cls, v):
        pattern=re.compile(r"^ORCID:[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid annotator format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid annotator format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('lab')
    def pattern_lab(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-LAB-[0-9]+-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid lab format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid lab format: {v}"
            raise ValueError(err_msg)
        return v


class StudyUpdate(ConfiguredBaseModel):
    """
    Update schema for Study — all fields optional for partial updates.
    """
    experiment: Optional[list[ExperimentCreate]] = Field(default=None, description="""The experiment in a study.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })
    publication: Optional[str] = Field(default=None, description="""The publication identifier (e.g., PMID, DOI) for the study or \"not published\" if the study is unpublished.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })
    annotator: Optional[list[str]] = Field(default=None, description="""ORCID identifier of the indidvidual submitting the study data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })
    lab: Optional[str] = Field(default=None, description="""ZFIN lab identifier of the laboratory that produced the study data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })

    @field_validator('annotator')
    def pattern_annotator(cls, v):
        pattern=re.compile(r"^ORCID:[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid annotator format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid annotator format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('lab')
    def pattern_lab(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-LAB-[0-9]+-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid lab format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid lab format: {v}"
            raise ValueError(err_msg)
        return v


class StudyRead(ReadBaseModel):
    """
    Read schema for Study — from_attributes=True, extra=ignore.
    """
    experiment: Optional[list[ExperimentRead]] = Field(default=None, description="""The experiment in a study.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })
    publication: Optional[str] = Field(default=None, description="""The publication identifier (e.g., PMID, DOI) for the study or \"not published\" if the study is unpublished.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })
    annotator: Optional[list[str]] = Field(default=None, description="""ORCID identifier of the indidvidual submitting the study data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })
    lab: Optional[str] = Field(default=None, description="""ZFIN lab identifier of the laboratory that produced the study data.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Study']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })

    @field_validator('annotator')
    def pattern_annotator(cls, v):
        pattern=re.compile(r"^ORCID:[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid annotator format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid annotator format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('lab')
    def pattern_lab(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-LAB-[0-9]+-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid lab format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid lab format: {v}"
            raise ValueError(err_msg)
        return v


class Experiment(ZappEntity):
    """
    A group of observations (phenotypic outcomes and their control) that are linked by a common exposure event and subject, and that are part of a study.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema'})

    standard_rearing_condition: Optional[bool] = Field(default=None, description="""An indication of whether the subject was maintained under standard conditions, which are the established, consistent environmental and husbandry parameters (such as temperature, lighting, diet, and housing) designed to minimize variability and ensure reproducibility in experiments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })
    rearing_condition_comment: Optional[str] = Field(default=None, description="""Comments on rearing conditions, for example, about how conditions deviated from standard parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })
    fish: Optional[Fish] = Field(default=None, description="""The fish subject of the experiment.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment', 'FishTankEntry']} })
    control: Optional[list[Control]] = Field(default=None, description="""An observation that serves as the reference for assessing phenotypic outcome.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })
    exposure_event: Optional[list[ExposureEvent]] = Field(default=None, description="""The exposure event in an experiment.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class ExperimentCreate(ConfiguredBaseModel):
    """
    Create schema for Experiment — id is server-generated.
    """
    standard_rearing_condition: Optional[bool] = Field(default=None, description="""An indication of whether the subject was maintained under standard conditions, which are the established, consistent environmental and husbandry parameters (such as temperature, lighting, diet, and housing) designed to minimize variability and ensure reproducibility in experiments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })
    rearing_condition_comment: Optional[str] = Field(default=None, description="""Comments on rearing conditions, for example, about how conditions deviated from standard parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })
    fish: Optional[FishCreate] = Field(default=None, description="""The fish subject of the experiment.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment', 'FishTankEntry']} })
    control: Optional[list[ControlCreate]] = Field(default=None, description="""An observation that serves as the reference for assessing phenotypic outcome.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })
    exposure_event: Optional[list[ExposureEventCreate]] = Field(default=None, description="""The exposure event in an experiment.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })


class ExperimentUpdate(ConfiguredBaseModel):
    """
    Update schema for Experiment — all fields optional for partial updates.
    """
    standard_rearing_condition: Optional[bool] = Field(default=None, description="""An indication of whether the subject was maintained under standard conditions, which are the established, consistent environmental and husbandry parameters (such as temperature, lighting, diet, and housing) designed to minimize variability and ensure reproducibility in experiments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })
    rearing_condition_comment: Optional[str] = Field(default=None, description="""Comments on rearing conditions, for example, about how conditions deviated from standard parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })
    fish: Optional[FishCreate] = Field(default=None, description="""The fish subject of the experiment.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment', 'FishTankEntry']} })
    control: Optional[list[ControlCreate]] = Field(default=None, description="""An observation that serves as the reference for assessing phenotypic outcome.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })
    exposure_event: Optional[list[ExposureEventCreate]] = Field(default=None, description="""The exposure event in an experiment.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })


class ExperimentRead(ReadBaseModel):
    """
    Read schema for Experiment — from_attributes=True, extra=ignore.
    """
    standard_rearing_condition: Optional[bool] = Field(default=None, description="""An indication of whether the subject was maintained under standard conditions, which are the established, consistent environmental and husbandry parameters (such as temperature, lighting, diet, and housing) designed to minimize variability and ensure reproducibility in experiments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })
    rearing_condition_comment: Optional[str] = Field(default=None, description="""Comments on rearing conditions, for example, about how conditions deviated from standard parameters.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })
    fish: Optional[FishRead] = Field(default=None, description="""The fish subject of the experiment.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment', 'FishTankEntry']} })
    control: Optional[list[ControlRead]] = Field(default=None, description="""An observation that serves as the reference for assessing phenotypic outcome.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })
    exposure_event: Optional[list[ExposureEventRead]] = Field(default=None, description="""The exposure event in an experiment.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class PhenotypeObservationSet(ZappEntity):
    """
    An observation set containing control and phenotypic outcome resulting from an exposure event.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema'})

    image: Optional[list[Image]] = Field(default=None, description="""Images associated with this observation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet']} })
    phenotype: Optional[list[Phenotype]] = Field(default=None, description="""The phenotype observed.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet']} })
    control_image: Optional[list[ControlImage]] = Field(default=None, description="""Image associated with this control.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet', 'Control']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class PhenotypeObservationSetCreate(ConfiguredBaseModel):
    """
    Create schema for PhenotypeObservationSet — id is server-generated.
    """
    image: Optional[list[ImageCreate]] = Field(default=None, description="""Images associated with this observation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet']} })
    phenotype: Optional[list[PhenotypeCreate]] = Field(default=None, description="""The phenotype observed.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet']} })
    control_image: Optional[list[ControlImageCreate]] = Field(default=None, description="""Image associated with this control.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet', 'Control']} })


class PhenotypeObservationSetUpdate(ConfiguredBaseModel):
    """
    Update schema for PhenotypeObservationSet — all fields optional for partial updates.
    """
    image: Optional[list[ImageCreate]] = Field(default=None, description="""Images associated with this observation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet']} })
    phenotype: Optional[list[PhenotypeCreate]] = Field(default=None, description="""The phenotype observed.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet']} })
    control_image: Optional[list[ControlImageCreate]] = Field(default=None, description="""Image associated with this control.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet', 'Control']} })


class PhenotypeObservationSetRead(ReadBaseModel):
    """
    Read schema for PhenotypeObservationSet — from_attributes=True, extra=ignore.
    """
    image: Optional[list[ImageRead]] = Field(default=None, description="""Images associated with this observation.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet']} })
    phenotype: Optional[list[PhenotypeRead]] = Field(default=None, description="""The phenotype observed.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet']} })
    control_image: Optional[list[ControlImageRead]] = Field(default=None, description="""Image associated with this control.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet', 'Control']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class Phenotype(ZappEntity):
    """
    Any measurable or visible trait change in the subject as a result of exposure.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema'})

    stage: Optional[str] = Field(default=None, description="""The developmental stage of fish when the phenotype was observed.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })
    prevalence: Optional[QuantityValue] = Field(default=None, description="""The percentage of subject exhibiting this phenotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })
    severity: Optional[SeverityEnum] = Field(default=None, description="""The intensity of the observed phenotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })
    phenotype_term_id: Optional[PhenotypeTerm] = Field(default=None, description="""The phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class PhenotypeCreate(ConfiguredBaseModel):
    """
    Create schema for Phenotype — id is server-generated.
    """
    stage: Optional[str] = Field(default=None, description="""The developmental stage of fish when the phenotype was observed.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })
    prevalence: Optional[QuantityValue] = Field(default=None, description="""The percentage of subject exhibiting this phenotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })
    severity: Optional[SeverityEnum] = Field(default=None, description="""The intensity of the observed phenotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })
    phenotype_term_id: Optional[PhenotypeTerm] = Field(default=None, description="""The phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })


class PhenotypeUpdate(ConfiguredBaseModel):
    """
    Update schema for Phenotype — all fields optional for partial updates.
    """
    stage: Optional[str] = Field(default=None, description="""The developmental stage of fish when the phenotype was observed.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })
    prevalence: Optional[QuantityValue] = Field(default=None, description="""The percentage of subject exhibiting this phenotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })
    severity: Optional[SeverityEnum] = Field(default=None, description="""The intensity of the observed phenotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })
    phenotype_term_id: Optional[PhenotypeTerm] = Field(default=None, description="""The phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })


class PhenotypeRead(ReadBaseModel):
    """
    Read schema for Phenotype — from_attributes=True, extra=ignore.
    """
    stage: Optional[str] = Field(default=None, description="""The developmental stage of fish when the phenotype was observed.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })
    prevalence: Optional[QuantityValueRead] = Field(default=None, description="""The percentage of subject exhibiting this phenotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })
    severity: Optional[SeverityEnum] = Field(default=None, description="""The intensity of the observed phenotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })
    phenotype_term_id: Optional[PhenotypeTermRead] = Field(default=None, description="""The phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Phenotype']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class Control(ZappEntity):
    """
    A subject serves as a reference for assessing phenotypic outcome in the phenotype observation set.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema'})

    control_type: Optional[str] = Field(default=None, description="""Type of control (e.g., wildtype vs mutant, treated vs untreated).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control']} })
    vehicle_if_treated: Optional[VehicleOfTransmission] = Field(default=None, description="""The vehicle used in a control.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })
    control_image: Optional[list[ControlImage]] = Field(default=None, description="""Image associated with this control.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet', 'Control']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class ControlCreate(ConfiguredBaseModel):
    """
    Create schema for Control — id is server-generated.
    """
    control_type: Optional[str] = Field(default=None, description="""Type of control (e.g., wildtype vs mutant, treated vs untreated).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control']} })
    vehicle_if_treated: Optional[VehicleOfTransmissionCreate] = Field(default=None, description="""The vehicle used in a control.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })
    control_image: Optional[list[ControlImageCreate]] = Field(default=None, description="""Image associated with this control.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet', 'Control']} })


class ControlUpdate(ConfiguredBaseModel):
    """
    Update schema for Control — all fields optional for partial updates.
    """
    control_type: Optional[str] = Field(default=None, description="""Type of control (e.g., wildtype vs mutant, treated vs untreated).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control']} })
    vehicle_if_treated: Optional[VehicleOfTransmissionCreate] = Field(default=None, description="""The vehicle used in a control.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })
    control_image: Optional[list[ControlImageCreate]] = Field(default=None, description="""Image associated with this control.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet', 'Control']} })


class ControlRead(ReadBaseModel):
    """
    Read schema for Control — from_attributes=True, extra=ignore.
    """
    control_type: Optional[str] = Field(default=None, description="""Type of control (e.g., wildtype vs mutant, treated vs untreated).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control']} })
    vehicle_if_treated: Optional[VehicleOfTransmissionRead] = Field(default=None, description="""The vehicle used in a control.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })
    control_image: Optional[list[ControlImageRead]] = Field(default=None, description="""Image associated with this control.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeObservationSet', 'Control']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class ExposureEvent(ZappEntity):
    """
    An occurrence in a study where a subject is exposed to a stressor under defined conditions.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'exact_mappings': ['biolink:ExposureEvent'],
         'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema'})

    stressor: Optional[list[StressorChemical]] = Field(default=None, description="""Substance, chemical or toxicant that elicits a response (a phenotype) in a subject when encountered through exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    vehicle: Optional[list[VehicleOfTransmission]] = Field(default=None, description="""The substance or medium used to deliver a stressor.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    route: Optional[ExposureRoute] = Field(default=None, description="""The route of exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    regimen: Optional[Regimen] = Field(default=None, description="""The regimen for the exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    exposure_start_stage: Optional[str] = Field(default=None, description="""The developmental stage of fish when exposure started.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    exposure_end_stage: Optional[str] = Field(default=None, description="""The developmental stage of fish when exposure ended.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })
    exposure_type: Optional[ExposureType] = Field(default=None, description="""An instance of exposure specifying the type of stressor a subject was exposed to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    additional_exposure_condition: Optional[str] = Field(default=None, description="""Additional information about the conditions under which exposure event occurred.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    phenotype_observation: Optional[list[PhenotypeObservationSet]] = Field(default=None, description="""The phenotype observation resulting from an exposure event.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class ExposureEventCreate(ConfiguredBaseModel):
    """
    Create schema for ExposureEvent — id is server-generated.
    """
    stressor: Optional[list[StressorChemicalCreate]] = Field(default=None, description="""Substance, chemical or toxicant that elicits a response (a phenotype) in a subject when encountered through exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    vehicle: Optional[list[VehicleOfTransmissionCreate]] = Field(default=None, description="""The substance or medium used to deliver a stressor.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    route: Optional[ExposureRoute] = Field(default=None, description="""The route of exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    regimen: Optional[RegimenCreate] = Field(default=None, description="""The regimen for the exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    exposure_start_stage: Optional[str] = Field(default=None, description="""The developmental stage of fish when exposure started.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    exposure_end_stage: Optional[str] = Field(default=None, description="""The developmental stage of fish when exposure ended.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })
    exposure_type: Optional[ExposureType] = Field(default=None, description="""An instance of exposure specifying the type of stressor a subject was exposed to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    additional_exposure_condition: Optional[str] = Field(default=None, description="""Additional information about the conditions under which exposure event occurred.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    phenotype_observation: Optional[list[PhenotypeObservationSetCreate]] = Field(default=None, description="""The phenotype observation resulting from an exposure event.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })


class ExposureEventUpdate(ConfiguredBaseModel):
    """
    Update schema for ExposureEvent — all fields optional for partial updates.
    """
    stressor: Optional[list[StressorChemicalCreate]] = Field(default=None, description="""Substance, chemical or toxicant that elicits a response (a phenotype) in a subject when encountered through exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    vehicle: Optional[list[VehicleOfTransmissionCreate]] = Field(default=None, description="""The substance or medium used to deliver a stressor.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    route: Optional[ExposureRoute] = Field(default=None, description="""The route of exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    regimen: Optional[RegimenCreate] = Field(default=None, description="""The regimen for the exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    exposure_start_stage: Optional[str] = Field(default=None, description="""The developmental stage of fish when exposure started.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    exposure_end_stage: Optional[str] = Field(default=None, description="""The developmental stage of fish when exposure ended.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })
    exposure_type: Optional[ExposureType] = Field(default=None, description="""An instance of exposure specifying the type of stressor a subject was exposed to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    additional_exposure_condition: Optional[str] = Field(default=None, description="""Additional information about the conditions under which exposure event occurred.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    phenotype_observation: Optional[list[PhenotypeObservationSetCreate]] = Field(default=None, description="""The phenotype observation resulting from an exposure event.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })


class ExposureEventRead(ReadBaseModel):
    """
    Read schema for ExposureEvent — from_attributes=True, extra=ignore.
    """
    stressor: Optional[list[StressorChemicalRead]] = Field(default=None, description="""Substance, chemical or toxicant that elicits a response (a phenotype) in a subject when encountered through exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    vehicle: Optional[list[VehicleOfTransmissionRead]] = Field(default=None, description="""The substance or medium used to deliver a stressor.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    route: Optional[ExposureRouteRead] = Field(default=None, description="""The route of exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    regimen: Optional[RegimenRead] = Field(default=None, description="""The regimen for the exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    exposure_start_stage: Optional[str] = Field(default=None, description="""The developmental stage of fish when exposure started.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    exposure_end_stage: Optional[str] = Field(default=None, description="""The developmental stage of fish when exposure ended.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })
    exposure_type: Optional[ExposureTypeRead] = Field(default=None, description="""An instance of exposure specifying the type of stressor a subject was exposed to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    additional_exposure_condition: Optional[str] = Field(default=None, description="""Additional information about the conditions under which exposure event occurred.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    phenotype_observation: Optional[list[PhenotypeObservationSetRead]] = Field(default=None, description="""The phenotype observation resulting from an exposure event.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ExposureEvent']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class Regimen(ZappEntity):
    """
    The schedule and pattern of an exposure event.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema'})

    exposure_regimen_type: Optional[ExposureRegimenTypeEnum] = Field(default=None, description="""The type of exposure regimen (e.g., continuous or repeated).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    interval_between_individual_exposures: Optional[QuantityValue] = Field(default=None, description="""Interval between individual exposures.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    total_exposure_duration: Optional[QuantityValue] = Field(default=None, description="""Time between first and last individual exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    individual_exposure_duration: Optional[QuantityValue] = Field(default=None, description="""Individual exposure duration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    number_of_individual_exposure: Optional[int] = Field(default=None, description="""Total number of individual exposures.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class RegimenCreate(ConfiguredBaseModel):
    """
    Create schema for Regimen — id is server-generated.
    """
    exposure_regimen_type: Optional[ExposureRegimenTypeEnum] = Field(default=None, description="""The type of exposure regimen (e.g., continuous or repeated).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    interval_between_individual_exposures: Optional[QuantityValue] = Field(default=None, description="""Interval between individual exposures.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    total_exposure_duration: Optional[QuantityValue] = Field(default=None, description="""Time between first and last individual exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    individual_exposure_duration: Optional[QuantityValue] = Field(default=None, description="""Individual exposure duration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    number_of_individual_exposure: Optional[int] = Field(default=None, description="""Total number of individual exposures.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })


class RegimenUpdate(ConfiguredBaseModel):
    """
    Update schema for Regimen — all fields optional for partial updates.
    """
    exposure_regimen_type: Optional[ExposureRegimenTypeEnum] = Field(default=None, description="""The type of exposure regimen (e.g., continuous or repeated).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    interval_between_individual_exposures: Optional[QuantityValue] = Field(default=None, description="""Interval between individual exposures.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    total_exposure_duration: Optional[QuantityValue] = Field(default=None, description="""Time between first and last individual exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    individual_exposure_duration: Optional[QuantityValue] = Field(default=None, description="""Individual exposure duration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    number_of_individual_exposure: Optional[int] = Field(default=None, description="""Total number of individual exposures.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })


class RegimenRead(ReadBaseModel):
    """
    Read schema for Regimen — from_attributes=True, extra=ignore.
    """
    exposure_regimen_type: Optional[ExposureRegimenTypeEnum] = Field(default=None, description="""The type of exposure regimen (e.g., continuous or repeated).""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    interval_between_individual_exposures: Optional[QuantityValueRead] = Field(default=None, description="""Interval between individual exposures.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    total_exposure_duration: Optional[QuantityValueRead] = Field(default=None, description="""Time between first and last individual exposure.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    individual_exposure_duration: Optional[QuantityValueRead] = Field(default=None, description="""Individual exposure duration.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    number_of_individual_exposure: Optional[int] = Field(default=None, description="""Total number of individual exposures.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Regimen']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class StressorChemical(ZappEntity):
    """
    A chemical that elicits a response (a phenotype) in a subject when encountered through exposure.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema',
         'rules': [{'description': 'A chemical entry must be identifiable: at least '
                                   'one of chemical_id (a standardized identifier / '
                                   'CURIE) or unrecognized_chemical_name (the '
                                   'free-text fallback for a chemical that could not '
                                   'be resolved) must be present.',
                    'postconditions': {'any_of': [{'slot_conditions': {'chemical_id': {'name': 'chemical_id',
                                                                                       'required': True}}},
                                                  {'slot_conditions': {'unrecognized_chemical_name': {'name': 'unrecognized_chemical_name',
                                                                                                      'required': True}}}]}},
                   {'description': 'Picking the other_not_listed manufacturer escape '
                                   'hatch means the supplier has to be named in free '
                                   'text; without it the entry records no recoverable '
                                   'supplier at all.',
                    'postconditions': {'slot_conditions': {'unrecognized_manufacturer_name': {'name': 'unrecognized_manufacturer_name',
                                                                                              'required': True}}},
                    'preconditions': {'slot_conditions': {'manufacturer': {'equals_string': 'other_not_listed',
                                                                           'name': 'manufacturer'}}}}]})

    chemical_id: Optional[str] = Field(default=None, description="""Chemical identifier (e.g., a CHEBI or other ontology URI) for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical',
                       'VehicleOfTransmission',
                       'ChemicalCabinetEntry']} })
    cas_id: Optional[str] = Field(default=None, description="""CAS identifier for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_chemical_name: Optional[str] = Field(default=None, description="""Free-text name for a chemical or vehicle that could not be resolved to a standardized identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    synonym: Optional[list[str]] = Field(default=None, description="""Human-readable name(s) for the chemical (non-CURIE), used for display and search. The canonical identity is chemical_id.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    manufacturer: Optional[ManufacturerEnum] = Field(default=None, description="""The manufacturer or supplier of the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_manufacturer_name: Optional[str] = Field(default=None, description="""Free-text name for a manufacturer or supplier that is not in the controlled ManufacturerEnum list.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    concentration: Optional[QuantityValue] = Field(default=None, description="""The dose or concentration of the chemical to which the subject was exposed to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class StressorChemicalCreate(ConfiguredBaseModel):
    """
    Create schema for StressorChemical — id is server-generated.
    """
    chemical_id: Optional[str] = Field(default=None, description="""Chemical identifier (e.g., a CHEBI or other ontology URI) for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical',
                       'VehicleOfTransmission',
                       'ChemicalCabinetEntry']} })
    cas_id: Optional[str] = Field(default=None, description="""CAS identifier for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_chemical_name: Optional[str] = Field(default=None, description="""Free-text name for a chemical or vehicle that could not be resolved to a standardized identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    synonym: Optional[list[str]] = Field(default=None, description="""Human-readable name(s) for the chemical (non-CURIE), used for display and search. The canonical identity is chemical_id.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    manufacturer: Optional[ManufacturerEnum] = Field(default=None, description="""The manufacturer or supplier of the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_manufacturer_name: Optional[str] = Field(default=None, description="""Free-text name for a manufacturer or supplier that is not in the controlled ManufacturerEnum list.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    concentration: Optional[QuantityValue] = Field(default=None, description="""The dose or concentration of the chemical to which the subject was exposed to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })


class StressorChemicalUpdate(ConfiguredBaseModel):
    """
    Update schema for StressorChemical — all fields optional for partial updates.
    """
    chemical_id: Optional[str] = Field(default=None, description="""Chemical identifier (e.g., a CHEBI or other ontology URI) for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical',
                       'VehicleOfTransmission',
                       'ChemicalCabinetEntry']} })
    cas_id: Optional[str] = Field(default=None, description="""CAS identifier for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_chemical_name: Optional[str] = Field(default=None, description="""Free-text name for a chemical or vehicle that could not be resolved to a standardized identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    synonym: Optional[list[str]] = Field(default=None, description="""Human-readable name(s) for the chemical (non-CURIE), used for display and search. The canonical identity is chemical_id.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    manufacturer: Optional[ManufacturerEnum] = Field(default=None, description="""The manufacturer or supplier of the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_manufacturer_name: Optional[str] = Field(default=None, description="""Free-text name for a manufacturer or supplier that is not in the controlled ManufacturerEnum list.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    concentration: Optional[QuantityValue] = Field(default=None, description="""The dose or concentration of the chemical to which the subject was exposed to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })


class StressorChemicalRead(ReadBaseModel):
    """
    Read schema for StressorChemical — from_attributes=True, extra=ignore.
    """
    chemical_id: Optional[str] = Field(default=None, description="""Chemical identifier (e.g., a CHEBI or other ontology URI) for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical',
                       'VehicleOfTransmission',
                       'ChemicalCabinetEntry']} })
    cas_id: Optional[str] = Field(default=None, description="""CAS identifier for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_chemical_name: Optional[str] = Field(default=None, description="""Free-text name for a chemical or vehicle that could not be resolved to a standardized identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    synonym: Optional[list[str]] = Field(default=None, description="""Human-readable name(s) for the chemical (non-CURIE), used for display and search. The canonical identity is chemical_id.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    manufacturer: Optional[ManufacturerEnum] = Field(default=None, description="""The manufacturer or supplier of the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_manufacturer_name: Optional[str] = Field(default=None, description="""Free-text name for a manufacturer or supplier that is not in the controlled ManufacturerEnum list.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    concentration: Optional[QuantityValueRead] = Field(default=None, description="""The dose or concentration of the chemical to which the subject was exposed to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class VehicleOfTransmission(ZappEntity):
    """
    The substance or medium used to deliver a stressor to a subject during an exposure event.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema',
         'rules': [{'description': 'Picking the other_not_listed vehicle escape hatch '
                                   'means the vehicle has to be named in free text; '
                                   'without it the entry records no recoverable '
                                   'vehicle at all.',
                    'postconditions': {'slot_conditions': {'unrecognized_chemical_name': {'name': 'unrecognized_chemical_name',
                                                                                          'required': True}}},
                    'preconditions': {'slot_conditions': {'vehicle_type': {'equals_string': 'other_not_listed',
                                                                           'name': 'vehicle_type'}}}},
                   {'description': 'Picking the other_not_listed manufacturer escape '
                                   'hatch means the supplier has to be named in free '
                                   'text; without it the entry records no recoverable '
                                   'supplier at all.',
                    'postconditions': {'slot_conditions': {'unrecognized_manufacturer_name': {'name': 'unrecognized_manufacturer_name',
                                                                                              'required': True}}},
                    'preconditions': {'slot_conditions': {'manufacturer': {'equals_string': 'other_not_listed',
                                                                           'name': 'manufacturer'}}}}]})

    vehicle_type: VehicleEnum = Field(default=..., description="""The type of vehicle used to deliver a stressor, drawn from a controlled vocabulary.""", json_schema_extra = { "linkml_meta": {'domain_of': ['VehicleOfTransmission']} })
    chemical_id: Optional[str] = Field(default=None, description="""Chemical identifier (e.g., a CHEBI or other ontology URI) for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical',
                       'VehicleOfTransmission',
                       'ChemicalCabinetEntry']} })
    cas_id: Optional[str] = Field(default=None, description="""CAS identifier for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_chemical_name: Optional[str] = Field(default=None, description="""Free-text name for a chemical or vehicle that could not be resolved to a standardized identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    synonym: Optional[list[str]] = Field(default=None, description="""Human-readable name(s) for the chemical (non-CURIE), used for display and search. The canonical identity is chemical_id.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    manufacturer: Optional[ManufacturerEnum] = Field(default=None, description="""The manufacturer or supplier of the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_manufacturer_name: Optional[str] = Field(default=None, description="""Free-text name for a manufacturer or supplier that is not in the controlled ManufacturerEnum list.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    concentration: Optional[QuantityValue] = Field(default=None, description="""The dose or concentration of the chemical to which the subject was exposed to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class VehicleOfTransmissionCreate(ConfiguredBaseModel):
    """
    Create schema for VehicleOfTransmission — id is server-generated.
    """
    vehicle_type: VehicleEnum = Field(default=..., description="""The type of vehicle used to deliver a stressor, drawn from a controlled vocabulary.""", json_schema_extra = { "linkml_meta": {'domain_of': ['VehicleOfTransmission']} })
    chemical_id: Optional[str] = Field(default=None, description="""Chemical identifier (e.g., a CHEBI or other ontology URI) for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical',
                       'VehicleOfTransmission',
                       'ChemicalCabinetEntry']} })
    cas_id: Optional[str] = Field(default=None, description="""CAS identifier for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_chemical_name: Optional[str] = Field(default=None, description="""Free-text name for a chemical or vehicle that could not be resolved to a standardized identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    synonym: Optional[list[str]] = Field(default=None, description="""Human-readable name(s) for the chemical (non-CURIE), used for display and search. The canonical identity is chemical_id.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    manufacturer: Optional[ManufacturerEnum] = Field(default=None, description="""The manufacturer or supplier of the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_manufacturer_name: Optional[str] = Field(default=None, description="""Free-text name for a manufacturer or supplier that is not in the controlled ManufacturerEnum list.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    concentration: Optional[QuantityValue] = Field(default=None, description="""The dose or concentration of the chemical to which the subject was exposed to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })


class VehicleOfTransmissionUpdate(ConfiguredBaseModel):
    """
    Update schema for VehicleOfTransmission — all fields optional for partial updates.
    """
    vehicle_type: Optional[VehicleEnum] = Field(default=None, description="""The type of vehicle used to deliver a stressor, drawn from a controlled vocabulary.""", json_schema_extra = { "linkml_meta": {'domain_of': ['VehicleOfTransmission']} })
    chemical_id: Optional[str] = Field(default=None, description="""Chemical identifier (e.g., a CHEBI or other ontology URI) for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical',
                       'VehicleOfTransmission',
                       'ChemicalCabinetEntry']} })
    cas_id: Optional[str] = Field(default=None, description="""CAS identifier for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_chemical_name: Optional[str] = Field(default=None, description="""Free-text name for a chemical or vehicle that could not be resolved to a standardized identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    synonym: Optional[list[str]] = Field(default=None, description="""Human-readable name(s) for the chemical (non-CURIE), used for display and search. The canonical identity is chemical_id.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    manufacturer: Optional[ManufacturerEnum] = Field(default=None, description="""The manufacturer or supplier of the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_manufacturer_name: Optional[str] = Field(default=None, description="""Free-text name for a manufacturer or supplier that is not in the controlled ManufacturerEnum list.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    concentration: Optional[QuantityValue] = Field(default=None, description="""The dose or concentration of the chemical to which the subject was exposed to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })


class VehicleOfTransmissionRead(ReadBaseModel):
    """
    Read schema for VehicleOfTransmission — from_attributes=True, extra=ignore.
    """
    vehicle_type: VehicleEnum = Field(default=..., description="""The type of vehicle used to deliver a stressor, drawn from a controlled vocabulary.""", json_schema_extra = { "linkml_meta": {'domain_of': ['VehicleOfTransmission']} })
    chemical_id: Optional[str] = Field(default=None, description="""Chemical identifier (e.g., a CHEBI or other ontology URI) for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical',
                       'VehicleOfTransmission',
                       'ChemicalCabinetEntry']} })
    cas_id: Optional[str] = Field(default=None, description="""CAS identifier for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_chemical_name: Optional[str] = Field(default=None, description="""Free-text name for a chemical or vehicle that could not be resolved to a standardized identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    synonym: Optional[list[str]] = Field(default=None, description="""Human-readable name(s) for the chemical (non-CURIE), used for display and search. The canonical identity is chemical_id.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    manufacturer: Optional[ManufacturerEnum] = Field(default=None, description="""The manufacturer or supplier of the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    unrecognized_manufacturer_name: Optional[str] = Field(default=None, description="""Free-text name for a manufacturer or supplier that is not in the controlled ManufacturerEnum list.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    concentration: Optional[QuantityValueRead] = Field(default=None, description="""The dose or concentration of the chemical to which the subject was exposed to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical', 'VehicleOfTransmission']} })
    comment: Optional[str] = Field(default=None, description="""Additional comments.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Control',
                       'ExposureEvent',
                       'StressorChemical',
                       'VehicleOfTransmission']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class Image(ZappEntity):
    """
    An image associated with a phenotype observation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema'})

    magnification: Optional[str] = Field(default=None, description="""The factor by which a microscope enlarges the apparent size of a subject compared to its actual size.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    resolution: Optional[str] = Field(default=None, description="""The level of detail in the image.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    scale_bar: Optional[str] = Field(default=None, description="""Scale bar information, including the physical length it represents and the unit of measurement.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class ImageCreate(ConfiguredBaseModel):
    """
    Create schema for Image — id is server-generated.
    """
    magnification: Optional[str] = Field(default=None, description="""The factor by which a microscope enlarges the apparent size of a subject compared to its actual size.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    resolution: Optional[str] = Field(default=None, description="""The level of detail in the image.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    scale_bar: Optional[str] = Field(default=None, description="""Scale bar information, including the physical length it represents and the unit of measurement.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })


class ImageUpdate(ConfiguredBaseModel):
    """
    Update schema for Image — all fields optional for partial updates.
    """
    magnification: Optional[str] = Field(default=None, description="""The factor by which a microscope enlarges the apparent size of a subject compared to its actual size.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    resolution: Optional[str] = Field(default=None, description="""The level of detail in the image.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    scale_bar: Optional[str] = Field(default=None, description="""Scale bar information, including the physical length it represents and the unit of measurement.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })


class ImageRead(ReadBaseModel):
    """
    Read schema for Image — from_attributes=True, extra=ignore.
    """
    magnification: Optional[str] = Field(default=None, description="""The factor by which a microscope enlarges the apparent size of a subject compared to its actual size.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    resolution: Optional[str] = Field(default=None, description="""The level of detail in the image.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    scale_bar: Optional[str] = Field(default=None, description="""Scale bar information, including the physical length it represents and the unit of measurement.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class ControlImage(ZappEntity):
    """
    An image associated with a control, taken at the same developmental stage as the corresponding phenotype observation.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema'})

    phenotype_id: Optional[str] = Field(default=None, description="""Foreign key reference to the PhenotypeObservationSet uuid (for database representation).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlImage']} })
    magnification: Optional[str] = Field(default=None, description="""The factor by which a microscope enlarges the apparent size of a subject compared to its actual size.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    resolution: Optional[str] = Field(default=None, description="""The level of detail in the image.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    scale_bar: Optional[str] = Field(default=None, description="""Scale bar information, including the physical length it represents and the unit of measurement.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    phenotype_comments: Optional[str] = Field(default=None, description="""Comments about the phenotype in the control image.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlImage']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class ControlImageCreate(ConfiguredBaseModel):
    """
    Create schema for ControlImage — id is server-generated.
    """
    phenotype_id: Optional[str] = Field(default=None, description="""Foreign key reference to the PhenotypeObservationSet uuid (for database representation).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlImage']} })
    magnification: Optional[str] = Field(default=None, description="""The factor by which a microscope enlarges the apparent size of a subject compared to its actual size.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    resolution: Optional[str] = Field(default=None, description="""The level of detail in the image.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    scale_bar: Optional[str] = Field(default=None, description="""Scale bar information, including the physical length it represents and the unit of measurement.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    phenotype_comments: Optional[str] = Field(default=None, description="""Comments about the phenotype in the control image.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlImage']} })


class ControlImageUpdate(ConfiguredBaseModel):
    """
    Update schema for ControlImage — all fields optional for partial updates.
    """
    phenotype_id: Optional[str] = Field(default=None, description="""Foreign key reference to the PhenotypeObservationSet uuid (for database representation).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlImage']} })
    magnification: Optional[str] = Field(default=None, description="""The factor by which a microscope enlarges the apparent size of a subject compared to its actual size.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    resolution: Optional[str] = Field(default=None, description="""The level of detail in the image.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    scale_bar: Optional[str] = Field(default=None, description="""Scale bar information, including the physical length it represents and the unit of measurement.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    phenotype_comments: Optional[str] = Field(default=None, description="""Comments about the phenotype in the control image.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlImage']} })


class ControlImageRead(ReadBaseModel):
    """
    Read schema for ControlImage — from_attributes=True, extra=ignore.
    """
    phenotype_id: Optional[str] = Field(default=None, description="""Foreign key reference to the PhenotypeObservationSet uuid (for database representation).""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlImage']} })
    magnification: Optional[str] = Field(default=None, description="""The factor by which a microscope enlarges the apparent size of a subject compared to its actual size.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    resolution: Optional[str] = Field(default=None, description="""The level of detail in the image.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    scale_bar: Optional[str] = Field(default=None, description="""Scale bar information, including the physical length it represents and the unit of measurement.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Image', 'ControlImage']} })
    phenotype_comments: Optional[str] = Field(default=None, description="""Comments about the phenotype in the control image.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ControlImage']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class PhenotypeTerm(OntologyEntity):
    """
    A phenotype ontology term from the Zebrafish Phenotype ontology (ZP).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'exact_mappings': ['biolink:PhenotypicFeature'],
         'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema'})

    term_uri: str = Field(default=..., description="""The URI of the phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeTerm', 'ExposureRoute', 'ExposureType']} })
    term_label: Optional[str] = Field(default=None, description="""The human-readable label for the phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeTerm', 'ExposureRoute', 'ExposureType']} })


class PhenotypeTermRead(ReadBaseModel):
    """
    Read schema for PhenotypeTerm — from_attributes=True, extra=ignore.
    """
    term_uri: str = Field(default=..., description="""The URI of the phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeTerm', 'ExposureRoute', 'ExposureType']} })
    term_label: Optional[str] = Field(default=None, description="""The human-readable label for the phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeTerm', 'ExposureRoute', 'ExposureType']} })


class ExposureRoute(OntologyEntity):
    """
    A route-of-exposure term. Term URIs are expected to be reachable from
    EXO:0000154 (route of exposure) in the EXO ontology.

    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema',
         'slot_usage': {'term_label': {'name': 'term_label', 'required': True}}})

    term_uri: str = Field(default=..., description="""The URI of the phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeTerm', 'ExposureRoute', 'ExposureType']} })
    term_label: str = Field(default=..., description="""The human-readable label for the phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeTerm', 'ExposureRoute', 'ExposureType']} })


class ExposureRouteRead(ReadBaseModel):
    """
    Read schema for ExposureRoute — from_attributes=True, extra=ignore.
    """
    term_uri: str = Field(default=..., description="""The URI of the phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeTerm', 'ExposureRoute', 'ExposureType']} })
    term_label: str = Field(default=..., description="""The human-readable label for the phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeTerm', 'ExposureRoute', 'ExposureType']} })


class ExposureType(OntologyEntity):
    """
    An exposure-type term from ECTO.

    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema',
         'slot_usage': {'term_label': {'name': 'term_label', 'required': True}}})

    term_uri: str = Field(default=..., description="""The URI of the phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeTerm', 'ExposureRoute', 'ExposureType']} })
    term_label: str = Field(default=..., description="""The human-readable label for the phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeTerm', 'ExposureRoute', 'ExposureType']} })


class ExposureTypeRead(ReadBaseModel):
    """
    Read schema for ExposureType — from_attributes=True, extra=ignore.
    """
    term_uri: str = Field(default=..., description="""The URI of the phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeTerm', 'ExposureRoute', 'ExposureType']} })
    term_label: str = Field(default=..., description="""The human-readable label for the phenotype ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['PhenotypeTerm', 'ExposureRoute', 'ExposureType']} })


class Fish(ZappEntity):
    """
    A zebrafish subject in a study. Mirrors ZFIN's Fish object (GENO:0000525, \"effective genotype\"): a Fish is the combination of an intrinsic Genotype (mutant alleles, transgenics and wild-type background) and any transient gene-targeting reagents (STRs — morpholinos/CRISPRs). The STR / gene-targeting reagent component is out of scope for ZAPP at this time and is intentionally not modeled yet. The Fish carries its own ZFIN fish identifier (ZDB-FISH-…), which is distinct from the ZDB-GENO-… identifier of its Genotype; either may be absent for lab-specific fish not yet registered with ZFIN.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'exact_mappings': ['GENO:0000525'],
         'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema',
         'slot_usage': {'name': {'name': 'name', 'required': True}}})

    name: str = Field(default=..., description="""Name or label of an entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish', 'ResearchGroup']} })
    fish_zfin_id: Optional[str] = Field(default=None, description="""ZFIN fish identifier (ZDB-FISH-…) for the subject. Distinct from the genotype identifier; may be absent for lab-specific fish not yet registered.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish']} })
    genotype: Optional[Genotype] = Field(default=None, description="""The intrinsic genotype of the fish.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish']} })
    cross: Optional[Cross] = Field(default=None, description="""The mating that produced the experimental animals, and how their genotype was established. Defaults conceptually to an incross of the fish's own line.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })

    @field_validator('fish_zfin_id')
    def pattern_fish_zfin_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-FISH-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid fish_zfin_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid fish_zfin_id format: {v}"
            raise ValueError(err_msg)
        return v


class FishCreate(ConfiguredBaseModel):
    """
    Create schema for Fish — id is server-generated.
    """
    name: str = Field(default=..., description="""Name or label of an entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish', 'ResearchGroup']} })
    fish_zfin_id: Optional[str] = Field(default=None, description="""ZFIN fish identifier (ZDB-FISH-…) for the subject. Distinct from the genotype identifier; may be absent for lab-specific fish not yet registered.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish']} })
    genotype: Optional[GenotypeCreate] = Field(default=None, description="""The intrinsic genotype of the fish.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish']} })
    cross: Optional[CrossCreate] = Field(default=None, description="""The mating that produced the experimental animals, and how their genotype was established. Defaults conceptually to an incross of the fish's own line.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish']} })

    @field_validator('fish_zfin_id')
    def pattern_fish_zfin_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-FISH-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid fish_zfin_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid fish_zfin_id format: {v}"
            raise ValueError(err_msg)
        return v


class FishUpdate(ConfiguredBaseModel):
    """
    Update schema for Fish — all fields optional for partial updates.
    """
    name: Optional[str] = Field(default=None, description="""Name or label of an entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish', 'ResearchGroup']} })
    fish_zfin_id: Optional[str] = Field(default=None, description="""ZFIN fish identifier (ZDB-FISH-…) for the subject. Distinct from the genotype identifier; may be absent for lab-specific fish not yet registered.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish']} })
    genotype: Optional[GenotypeCreate] = Field(default=None, description="""The intrinsic genotype of the fish.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish']} })
    cross: Optional[CrossCreate] = Field(default=None, description="""The mating that produced the experimental animals, and how their genotype was established. Defaults conceptually to an incross of the fish's own line.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish']} })

    @field_validator('fish_zfin_id')
    def pattern_fish_zfin_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-FISH-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid fish_zfin_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid fish_zfin_id format: {v}"
            raise ValueError(err_msg)
        return v


class FishRead(ReadBaseModel):
    """
    Read schema for Fish — from_attributes=True, extra=ignore.
    """
    name: str = Field(default=..., description="""Name or label of an entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish', 'ResearchGroup']} })
    fish_zfin_id: Optional[str] = Field(default=None, description="""ZFIN fish identifier (ZDB-FISH-…) for the subject. Distinct from the genotype identifier; may be absent for lab-specific fish not yet registered.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish']} })
    genotype: Optional[GenotypeRead] = Field(default=None, description="""The intrinsic genotype of the fish.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish']} })
    cross: Optional[CrossRead] = Field(default=None, description="""The mating that produced the experimental animals, and how their genotype was established. Defaults conceptually to an incross of the fish's own line.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })

    @field_validator('fish_zfin_id')
    def pattern_fish_zfin_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-FISH-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid fish_zfin_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid fish_zfin_id format: {v}"
            raise ValueError(err_msg)
        return v


class Genotype(ZappEntity):
    """
    The intrinsic genotype of a fish (GENO:0000000) — equivalently, a *line*: the heritable combination of a wild-type genetic background plus any mutant allele(s) and transgenic insertion(s). Carries its own ZFIN genotype identifier (ZDB-GENO-…), which may differ from the fish identifier and may be absent if not yet registered.
    Note the recursion: ``background`` is itself a Genotype. A wild-type strain such as AB is simply a Genotype with no alterations (ZFIN models this the same way — a fish's \"Background ID\" is a ZDB-GENO). There is therefore one concept here, not two: a background *is* a line.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'exact_mappings': ['GENO:0000000'],
         'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema'})

    genotype_zfin_id: Optional[str] = Field(default=None, description="""ZFIN genotype identifier (ZDB-GENO-…) for the intrinsic genotype. May be absent for genotypes not yet registered with ZFIN.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    genotype_name: Optional[str] = Field(default=None, description="""Display name of the genotype, e.g. \"fgf8a<ti282a/ti282a>; rerea<tb210/tb210>\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    mutant_allele: Optional[list[MutantAllele]] = Field(default=None, description="""Mutant allele(s) carried by the genotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    transgenic_allele: Optional[list[TransgenicAllele]] = Field(default=None, description="""Transgenic insertion(s) carried by the genotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    background: Optional[Genotype] = Field(default=None, description="""The genetic background this line was bred into — itself a Genotype, normally a wild-type strain such as AB (i.e. a Genotype carrying no alterations). ZFIN models a fish's background the same way, as a ZDB-GENO reference.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })

    @field_validator('genotype_zfin_id')
    def pattern_genotype_zfin_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-GENO-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid genotype_zfin_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid genotype_zfin_id format: {v}"
            raise ValueError(err_msg)
        return v


class GenotypeCreate(ConfiguredBaseModel):
    """
    Create schema for Genotype — id is server-generated.
    """
    genotype_zfin_id: Optional[str] = Field(default=None, description="""ZFIN genotype identifier (ZDB-GENO-…) for the intrinsic genotype. May be absent for genotypes not yet registered with ZFIN.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    genotype_name: Optional[str] = Field(default=None, description="""Display name of the genotype, e.g. \"fgf8a<ti282a/ti282a>; rerea<tb210/tb210>\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    mutant_allele: Optional[list[MutantAlleleCreate]] = Field(default=None, description="""Mutant allele(s) carried by the genotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    transgenic_allele: Optional[list[TransgenicAlleleCreate]] = Field(default=None, description="""Transgenic insertion(s) carried by the genotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    background: Optional[GenotypeCreate] = Field(default=None, description="""The genetic background this line was bred into — itself a Genotype, normally a wild-type strain such as AB (i.e. a Genotype carrying no alterations). ZFIN models a fish's background the same way, as a ZDB-GENO reference.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })

    @field_validator('genotype_zfin_id')
    def pattern_genotype_zfin_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-GENO-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid genotype_zfin_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid genotype_zfin_id format: {v}"
            raise ValueError(err_msg)
        return v


class GenotypeUpdate(ConfiguredBaseModel):
    """
    Update schema for Genotype — all fields optional for partial updates.
    """
    genotype_zfin_id: Optional[str] = Field(default=None, description="""ZFIN genotype identifier (ZDB-GENO-…) for the intrinsic genotype. May be absent for genotypes not yet registered with ZFIN.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    genotype_name: Optional[str] = Field(default=None, description="""Display name of the genotype, e.g. \"fgf8a<ti282a/ti282a>; rerea<tb210/tb210>\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    mutant_allele: Optional[list[MutantAlleleCreate]] = Field(default=None, description="""Mutant allele(s) carried by the genotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    transgenic_allele: Optional[list[TransgenicAlleleCreate]] = Field(default=None, description="""Transgenic insertion(s) carried by the genotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    background: Optional[GenotypeCreate] = Field(default=None, description="""The genetic background this line was bred into — itself a Genotype, normally a wild-type strain such as AB (i.e. a Genotype carrying no alterations). ZFIN models a fish's background the same way, as a ZDB-GENO reference.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })

    @field_validator('genotype_zfin_id')
    def pattern_genotype_zfin_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-GENO-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid genotype_zfin_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid genotype_zfin_id format: {v}"
            raise ValueError(err_msg)
        return v


class GenotypeRead(ReadBaseModel):
    """
    Read schema for Genotype — from_attributes=True, extra=ignore.
    """
    genotype_zfin_id: Optional[str] = Field(default=None, description="""ZFIN genotype identifier (ZDB-GENO-…) for the intrinsic genotype. May be absent for genotypes not yet registered with ZFIN.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    genotype_name: Optional[str] = Field(default=None, description="""Display name of the genotype, e.g. \"fgf8a<ti282a/ti282a>; rerea<tb210/tb210>\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    mutant_allele: Optional[list[MutantAlleleRead]] = Field(default=None, description="""Mutant allele(s) carried by the genotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    transgenic_allele: Optional[list[TransgenicAlleleRead]] = Field(default=None, description="""Transgenic insertion(s) carried by the genotype.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    background: Optional[GenotypeRead] = Field(default=None, description="""The genetic background this line was bred into — itself a Genotype, normally a wild-type strain such as AB (i.e. a Genotype carrying no alterations). ZFIN models a fish's background the same way, as a ZDB-GENO reference.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Genotype']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })

    @field_validator('genotype_zfin_id')
    def pattern_genotype_zfin_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-GENO-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid genotype_zfin_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid genotype_zfin_id format: {v}"
            raise ValueError(err_msg)
        return v


class Cross(ZappEntity):
    """
    How the experimental animals were produced: the mating that generated the clutch, plus how the resulting genotype was established. An incross is represented by the same line on both sides.
    This matters because a genotype is not derivable from the parents alone — it follows from the cross *plus* selection. A het × het incross segregates 1:2:1, so an unsorted clutch has no single genotype, and an unqualified phenotype prevalence from such a clutch may be a Mendelian ratio rather than a toxicological effect. ``progeny_selection`` is what distinguishes those.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema'})

    maternal_line: Optional[Genotype] = Field(default=None, description="""The line (Genotype) of the female parent. Determines maternal contribution.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Cross']} })
    paternal_line: Optional[Genotype] = Field(default=None, description="""The line (Genotype) of the male parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Cross']} })
    progeny_selection: Optional[ProgenySelectionEnum] = Field(default=None, description="""How the genotype of the exposed animals was established from the cross — essential for interpreting phenotype prevalence.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Cross']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class CrossCreate(ConfiguredBaseModel):
    """
    Create schema for Cross — id is server-generated.
    """
    maternal_line: Optional[GenotypeCreate] = Field(default=None, description="""The line (Genotype) of the female parent. Determines maternal contribution.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Cross']} })
    paternal_line: Optional[GenotypeCreate] = Field(default=None, description="""The line (Genotype) of the male parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Cross']} })
    progeny_selection: Optional[ProgenySelectionEnum] = Field(default=None, description="""How the genotype of the exposed animals was established from the cross — essential for interpreting phenotype prevalence.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Cross']} })


class CrossUpdate(ConfiguredBaseModel):
    """
    Update schema for Cross — all fields optional for partial updates.
    """
    maternal_line: Optional[GenotypeCreate] = Field(default=None, description="""The line (Genotype) of the female parent. Determines maternal contribution.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Cross']} })
    paternal_line: Optional[GenotypeCreate] = Field(default=None, description="""The line (Genotype) of the male parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Cross']} })
    progeny_selection: Optional[ProgenySelectionEnum] = Field(default=None, description="""How the genotype of the exposed animals was established from the cross — essential for interpreting phenotype prevalence.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Cross']} })


class CrossRead(ReadBaseModel):
    """
    Read schema for Cross — from_attributes=True, extra=ignore.
    """
    maternal_line: Optional[GenotypeRead] = Field(default=None, description="""The line (Genotype) of the female parent. Determines maternal contribution.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Cross']} })
    paternal_line: Optional[GenotypeRead] = Field(default=None, description="""The line (Genotype) of the male parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Cross']} })
    progeny_selection: Optional[ProgenySelectionEnum] = Field(default=None, description="""How the genotype of the exposed animals was established from the cross — essential for interpreting phenotype prevalence.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Cross']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class MutantAllele(ZappEntity):
    """
    A mutant allele (genomic feature) carried by the fish, together with its zygosity and the gene it affects. The allele identifier is a ZFIN genomic feature id (ZDB-ALT-…); ZAPP additionally records the affected gene (affected genomic region).
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema',
         'slot_usage': {'allele_symbol': {'name': 'allele_symbol', 'required': True}}})

    allele_id: Optional[str] = Field(default=None, description="""ZFIN genomic feature identifier (ZDB-ALT-…) for the allele.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    allele_symbol: str = Field(default=..., description="""The allele symbol / designation, e.g. \"ti282a\", \"fh111\", \"w200Tg\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    alteration_type: Optional[SequenceAlterationTypeEnum] = Field(default=None, description="""The type of sequence alteration the allele represents, chosen from a controlled dropdown of common mutation / alteration types and normalized to a Sequence Ontology (SO) term. ZFIN records this as the feature's SO type.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_id: Optional[str] = Field(default=None, description="""Identifier of the gene affected by the allele (affected genomic region), typically a ZFIN gene id (ZDB-GENE-…).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_symbol: Optional[str] = Field(default=None, description="""Symbol of the gene affected by the allele, e.g. \"snapc1b\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the fish.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    mother_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the maternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    father_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the paternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })

    @field_validator('allele_id')
    def pattern_allele_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-ALT-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid allele_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid allele_id format: {v}"
            raise ValueError(err_msg)
        return v


class MutantAlleleCreate(ConfiguredBaseModel):
    """
    Create schema for MutantAllele — id is server-generated.
    """
    allele_id: Optional[str] = Field(default=None, description="""ZFIN genomic feature identifier (ZDB-ALT-…) for the allele.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    allele_symbol: str = Field(default=..., description="""The allele symbol / designation, e.g. \"ti282a\", \"fh111\", \"w200Tg\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    alteration_type: Optional[SequenceAlterationTypeEnum] = Field(default=None, description="""The type of sequence alteration the allele represents, chosen from a controlled dropdown of common mutation / alteration types and normalized to a Sequence Ontology (SO) term. ZFIN records this as the feature's SO type.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_id: Optional[str] = Field(default=None, description="""Identifier of the gene affected by the allele (affected genomic region), typically a ZFIN gene id (ZDB-GENE-…).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_symbol: Optional[str] = Field(default=None, description="""Symbol of the gene affected by the allele, e.g. \"snapc1b\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the fish.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    mother_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the maternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    father_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the paternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })

    @field_validator('allele_id')
    def pattern_allele_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-ALT-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid allele_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid allele_id format: {v}"
            raise ValueError(err_msg)
        return v


class MutantAlleleUpdate(ConfiguredBaseModel):
    """
    Update schema for MutantAllele — all fields optional for partial updates.
    """
    allele_id: Optional[str] = Field(default=None, description="""ZFIN genomic feature identifier (ZDB-ALT-…) for the allele.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    allele_symbol: Optional[str] = Field(default=None, description="""The allele symbol / designation, e.g. \"ti282a\", \"fh111\", \"w200Tg\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    alteration_type: Optional[SequenceAlterationTypeEnum] = Field(default=None, description="""The type of sequence alteration the allele represents, chosen from a controlled dropdown of common mutation / alteration types and normalized to a Sequence Ontology (SO) term. ZFIN records this as the feature's SO type.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_id: Optional[str] = Field(default=None, description="""Identifier of the gene affected by the allele (affected genomic region), typically a ZFIN gene id (ZDB-GENE-…).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_symbol: Optional[str] = Field(default=None, description="""Symbol of the gene affected by the allele, e.g. \"snapc1b\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the fish.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    mother_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the maternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    father_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the paternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })

    @field_validator('allele_id')
    def pattern_allele_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-ALT-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid allele_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid allele_id format: {v}"
            raise ValueError(err_msg)
        return v


class MutantAlleleRead(ReadBaseModel):
    """
    Read schema for MutantAllele — from_attributes=True, extra=ignore.
    """
    allele_id: Optional[str] = Field(default=None, description="""ZFIN genomic feature identifier (ZDB-ALT-…) for the allele.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    allele_symbol: str = Field(default=..., description="""The allele symbol / designation, e.g. \"ti282a\", \"fh111\", \"w200Tg\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    alteration_type: Optional[SequenceAlterationTypeEnum] = Field(default=None, description="""The type of sequence alteration the allele represents, chosen from a controlled dropdown of common mutation / alteration types and normalized to a Sequence Ontology (SO) term. ZFIN records this as the feature's SO type.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_id: Optional[str] = Field(default=None, description="""Identifier of the gene affected by the allele (affected genomic region), typically a ZFIN gene id (ZDB-GENE-…).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_symbol: Optional[str] = Field(default=None, description="""Symbol of the gene affected by the allele, e.g. \"snapc1b\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the fish.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    mother_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the maternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    father_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the paternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })

    @field_validator('allele_id')
    def pattern_allele_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-ALT-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid allele_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid allele_id format: {v}"
            raise ValueError(err_msg)
        return v


class TransgenicAllele(ZappEntity):
    """
    A transgenic insertion (genomic feature) carried by the fish, together with its zygosity and the transgenic construct it derives from. The allele identifier is a ZFIN genomic feature id (ZDB-ALT-…); the construct is a ZFIN transgenic construct (ZDB-TGCONSTRCT-…) used mainly for name display. The gene slots record the construct's driver / reporter gene so the atlas can be searched by gene across mutant and transgenic alleles alike.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema',
         'slot_usage': {'affected_gene_id': {'description': 'Identifier of the gene '
                                                            'whose regulatory region '
                                                            'drives the transgene '
                                                            '(e.g. fli1 in '
                                                            'Tg(fli1:EGFP)), typically '
                                                            'a ZFIN gene id '
                                                            '(ZDB-GENE-…).',
                                             'name': 'affected_gene_id'},
                        'affected_gene_symbol': {'description': 'Symbol of the '
                                                                "transgene's driver / "
                                                                'reporter gene, e.g. '
                                                                '"fli1".',
                                                 'name': 'affected_gene_symbol'},
                        'allele_symbol': {'name': 'allele_symbol', 'required': True},
                        'alteration_type': {'description': 'Type of alteration for a '
                                                           'transgenic feature — '
                                                           'usually a transgenic '
                                                           'insertion (SO:0001218). '
                                                           'Normalized to a Sequence '
                                                           'Ontology term.',
                                            'name': 'alteration_type'}}})

    allele_id: Optional[str] = Field(default=None, description="""ZFIN genomic feature identifier (ZDB-ALT-…) for the allele.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    allele_symbol: str = Field(default=..., description="""The allele symbol / designation, e.g. \"ti282a\", \"fh111\", \"w200Tg\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    construct_id: Optional[str] = Field(default=None, description="""ZFIN transgenic construct identifier (ZDB-TGCONSTRCT-…) for a transgenic allele.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TransgenicAllele']} })
    construct_name: Optional[str] = Field(default=None, description="""Name of the transgenic construct, e.g. \"Tg(mpeg1:YFP)\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['TransgenicAllele']} })
    alteration_type: Optional[SequenceAlterationTypeEnum] = Field(default=None, description="""Type of alteration for a transgenic feature — usually a transgenic insertion (SO:0001218). Normalized to a Sequence Ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_id: Optional[str] = Field(default=None, description="""Identifier of the gene whose regulatory region drives the transgene (e.g. fli1 in Tg(fli1:EGFP)), typically a ZFIN gene id (ZDB-GENE-…).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_symbol: Optional[str] = Field(default=None, description="""Symbol of the transgene's driver / reporter gene, e.g. \"fli1\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the fish.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    mother_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the maternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    father_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the paternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })

    @field_validator('allele_id')
    def pattern_allele_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-ALT-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid allele_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid allele_id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('construct_id')
    def pattern_construct_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-TGCONSTRCT-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid construct_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid construct_id format: {v}"
            raise ValueError(err_msg)
        return v


class TransgenicAlleleCreate(ConfiguredBaseModel):
    """
    Create schema for TransgenicAllele — id is server-generated.
    """
    allele_id: Optional[str] = Field(default=None, description="""ZFIN genomic feature identifier (ZDB-ALT-…) for the allele.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    allele_symbol: str = Field(default=..., description="""The allele symbol / designation, e.g. \"ti282a\", \"fh111\", \"w200Tg\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    construct_id: Optional[str] = Field(default=None, description="""ZFIN transgenic construct identifier (ZDB-TGCONSTRCT-…) for a transgenic allele.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TransgenicAllele']} })
    construct_name: Optional[str] = Field(default=None, description="""Name of the transgenic construct, e.g. \"Tg(mpeg1:YFP)\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['TransgenicAllele']} })
    alteration_type: Optional[SequenceAlterationTypeEnum] = Field(default=None, description="""Type of alteration for a transgenic feature — usually a transgenic insertion (SO:0001218). Normalized to a Sequence Ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_id: Optional[str] = Field(default=None, description="""Identifier of the gene whose regulatory region drives the transgene (e.g. fli1 in Tg(fli1:EGFP)), typically a ZFIN gene id (ZDB-GENE-…).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_symbol: Optional[str] = Field(default=None, description="""Symbol of the transgene's driver / reporter gene, e.g. \"fli1\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the fish.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    mother_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the maternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    father_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the paternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })

    @field_validator('allele_id')
    def pattern_allele_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-ALT-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid allele_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid allele_id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('construct_id')
    def pattern_construct_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-TGCONSTRCT-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid construct_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid construct_id format: {v}"
            raise ValueError(err_msg)
        return v


class TransgenicAlleleUpdate(ConfiguredBaseModel):
    """
    Update schema for TransgenicAllele — all fields optional for partial updates.
    """
    allele_id: Optional[str] = Field(default=None, description="""ZFIN genomic feature identifier (ZDB-ALT-…) for the allele.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    allele_symbol: Optional[str] = Field(default=None, description="""The allele symbol / designation, e.g. \"ti282a\", \"fh111\", \"w200Tg\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    construct_id: Optional[str] = Field(default=None, description="""ZFIN transgenic construct identifier (ZDB-TGCONSTRCT-…) for a transgenic allele.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TransgenicAllele']} })
    construct_name: Optional[str] = Field(default=None, description="""Name of the transgenic construct, e.g. \"Tg(mpeg1:YFP)\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['TransgenicAllele']} })
    alteration_type: Optional[SequenceAlterationTypeEnum] = Field(default=None, description="""Type of alteration for a transgenic feature — usually a transgenic insertion (SO:0001218). Normalized to a Sequence Ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_id: Optional[str] = Field(default=None, description="""Identifier of the gene whose regulatory region drives the transgene (e.g. fli1 in Tg(fli1:EGFP)), typically a ZFIN gene id (ZDB-GENE-…).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_symbol: Optional[str] = Field(default=None, description="""Symbol of the transgene's driver / reporter gene, e.g. \"fli1\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the fish.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    mother_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the maternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    father_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the paternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })

    @field_validator('allele_id')
    def pattern_allele_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-ALT-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid allele_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid allele_id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('construct_id')
    def pattern_construct_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-TGCONSTRCT-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid construct_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid construct_id format: {v}"
            raise ValueError(err_msg)
        return v


class TransgenicAlleleRead(ReadBaseModel):
    """
    Read schema for TransgenicAllele — from_attributes=True, extra=ignore.
    """
    allele_id: Optional[str] = Field(default=None, description="""ZFIN genomic feature identifier (ZDB-ALT-…) for the allele.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    allele_symbol: str = Field(default=..., description="""The allele symbol / designation, e.g. \"ti282a\", \"fh111\", \"w200Tg\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    construct_id: Optional[str] = Field(default=None, description="""ZFIN transgenic construct identifier (ZDB-TGCONSTRCT-…) for a transgenic allele.""", json_schema_extra = { "linkml_meta": {'domain_of': ['TransgenicAllele']} })
    construct_name: Optional[str] = Field(default=None, description="""Name of the transgenic construct, e.g. \"Tg(mpeg1:YFP)\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['TransgenicAllele']} })
    alteration_type: Optional[SequenceAlterationTypeEnum] = Field(default=None, description="""Type of alteration for a transgenic feature — usually a transgenic insertion (SO:0001218). Normalized to a Sequence Ontology term.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_id: Optional[str] = Field(default=None, description="""Identifier of the gene whose regulatory region drives the transgene (e.g. fli1 in Tg(fli1:EGFP)), typically a ZFIN gene id (ZDB-GENE-…).""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    affected_gene_symbol: Optional[str] = Field(default=None, description="""Symbol of the transgene's driver / reporter gene, e.g. \"fli1\".""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the fish.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    mother_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the maternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    father_zygosity: Optional[ZygosityEnum] = Field(default=None, description="""Zygosity of the allele in the paternal parent.""", json_schema_extra = { "linkml_meta": {'domain_of': ['MutantAllele', 'TransgenicAllele']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })

    @field_validator('allele_id')
    def pattern_allele_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-ALT-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid allele_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid allele_id format: {v}"
            raise ValueError(err_msg)
        return v

    @field_validator('construct_id')
    def pattern_construct_id(cls, v):
        pattern=re.compile(r"^ZFIN:ZDB-TGCONSTRCT-[0-9]{6}-[0-9]+$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid construct_id format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid construct_id format: {v}"
            raise ValueError(err_msg)
        return v


class ResearchGroup(ZappEntity):
    """
    A named collection of users that have shared editing access.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema',
         'slot_usage': {'name': {'name': 'name', 'required': True}}})

    name: str = Field(default=..., description="""Name or label of an entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish', 'ResearchGroup']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class ResearchGroupCreate(ConfiguredBaseModel):
    """
    Create schema for ResearchGroup — id is server-generated.
    """
    name: str = Field(default=..., description="""Name or label of an entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish', 'ResearchGroup']} })


class ResearchGroupUpdate(ConfiguredBaseModel):
    """
    Update schema for ResearchGroup — all fields optional for partial updates.
    """
    name: Optional[str] = Field(default=None, description="""Name or label of an entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish', 'ResearchGroup']} })


class ResearchGroupRead(ReadBaseModel):
    """
    Read schema for ResearchGroup — from_attributes=True, extra=ignore.
    """
    name: str = Field(default=..., description="""Name or label of an entity.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Fish', 'ResearchGroup']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class ResearchGroupMember(ZappEntity):
    """
    Membership of an ORCID identity in a research group.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'timestamped': {'tag': 'timestamped', 'value': True}},
         'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema',
         'unique_keys': {'membership_grain': {'unique_key_name': 'membership_grain',
                                              'unique_key_slots': ['research_group',
                                                                   'member']}}})

    research_group: int = Field(default=..., description="""The research group an entry belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember', 'ChemicalCabinetEntry', 'FishTankEntry']} })
    member: str = Field(default=..., description="""ORCID identifier of a research group member.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember']} })
    role: ResearchGroupRoleEnum = Field(default=..., description="""A member's permission level within a research group.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })

    @field_validator('member')
    def pattern_member(cls, v):
        pattern=re.compile(r"^ORCID:[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid member format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid member format: {v}"
            raise ValueError(err_msg)
        return v


class ResearchGroupMemberCreate(ConfiguredBaseModel):
    """
    Create schema for ResearchGroupMember — id is server-generated.
    """
    research_group: int = Field(default=..., description="""The research group an entry belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember', 'ChemicalCabinetEntry', 'FishTankEntry']} })
    member: str = Field(default=..., description="""ORCID identifier of a research group member.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember']} })
    role: ResearchGroupRoleEnum = Field(default=..., description="""A member's permission level within a research group.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember']} })

    @field_validator('member')
    def pattern_member(cls, v):
        pattern=re.compile(r"^ORCID:[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid member format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid member format: {v}"
            raise ValueError(err_msg)
        return v


class ResearchGroupMemberUpdate(ConfiguredBaseModel):
    """
    Update schema for ResearchGroupMember — all fields optional for partial updates.
    """
    research_group: Optional[int] = Field(default=None, description="""The research group an entry belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember', 'ChemicalCabinetEntry', 'FishTankEntry']} })
    member: Optional[str] = Field(default=None, description="""ORCID identifier of a research group member.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember']} })
    role: Optional[ResearchGroupRoleEnum] = Field(default=None, description="""A member's permission level within a research group.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember']} })

    @field_validator('member')
    def pattern_member(cls, v):
        pattern=re.compile(r"^ORCID:[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid member format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid member format: {v}"
            raise ValueError(err_msg)
        return v


class ResearchGroupMemberRead(ReadBaseModel):
    """
    Read schema for ResearchGroupMember — from_attributes=True, extra=ignore.
    """
    research_group: int = Field(default=..., description="""The research group an entry belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember', 'ChemicalCabinetEntry', 'FishTankEntry']} })
    member: str = Field(default=..., description="""ORCID identifier of a research group member.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember']} })
    role: ResearchGroupRoleEnum = Field(default=..., description="""A member's permission level within a research group.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })

    @field_validator('member')
    def pattern_member(cls, v):
        pattern=re.compile(r"^ORCID:[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$")
        if isinstance(v, list):
            for element in v:
                if isinstance(element, str) and not pattern.match(element):
                    err_msg = f"Invalid member format: {element}"
                    raise ValueError(err_msg)
        elif isinstance(v, str) and not pattern.match(v):
            err_msg = f"Invalid member format: {v}"
            raise ValueError(err_msg)
        return v


class ChemicalCabinetEntry(ZappEntity):
    """
    A chemical a research group keeps on hand. Recorded once, then reused to pre-fill curation instead of re-searching the chemical each time.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'timestamped': {'tag': 'timestamped', 'value': True}},
         'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema',
         'slot_usage': {'chemical_id': {'name': 'chemical_id', 'required': True}},
         'unique_keys': {'cabinet_grain': {'unique_key_name': 'cabinet_grain',
                                           'unique_key_slots': ['research_group',
                                                                'chemical_id']}}})

    research_group: int = Field(default=..., description="""The research group an entry belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember', 'ChemicalCabinetEntry', 'FishTankEntry']} })
    chemical_id: str = Field(default=..., description="""Chemical identifier (e.g., a CHEBI or other ontology URI) for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical',
                       'VehicleOfTransmission',
                       'ChemicalCabinetEntry']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class ChemicalCabinetEntryCreate(ConfiguredBaseModel):
    """
    Create schema for ChemicalCabinetEntry — id is server-generated.
    """
    research_group: int = Field(default=..., description="""The research group an entry belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember', 'ChemicalCabinetEntry', 'FishTankEntry']} })
    chemical_id: str = Field(default=..., description="""Chemical identifier (e.g., a CHEBI or other ontology URI) for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical',
                       'VehicleOfTransmission',
                       'ChemicalCabinetEntry']} })


class ChemicalCabinetEntryUpdate(ConfiguredBaseModel):
    """
    Update schema for ChemicalCabinetEntry — all fields optional for partial updates.
    """
    research_group: Optional[int] = Field(default=None, description="""The research group an entry belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember', 'ChemicalCabinetEntry', 'FishTankEntry']} })
    chemical_id: Optional[str] = Field(default=None, description="""Chemical identifier (e.g., a CHEBI or other ontology URI) for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical',
                       'VehicleOfTransmission',
                       'ChemicalCabinetEntry']} })


class ChemicalCabinetEntryRead(ReadBaseModel):
    """
    Read schema for ChemicalCabinetEntry — from_attributes=True, extra=ignore.
    """
    research_group: int = Field(default=..., description="""The research group an entry belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember', 'ChemicalCabinetEntry', 'FishTankEntry']} })
    chemical_id: str = Field(default=..., description="""Chemical identifier (e.g., a CHEBI or other ontology URI) for the chemical.""", json_schema_extra = { "linkml_meta": {'domain_of': ['StressorChemical',
                       'VehicleOfTransmission',
                       'ChemicalCabinetEntry']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class FishTankEntry(ZappEntity):
    """
    A fish line a research group maintains. Recorded once, then reused to pre-fill curation instead of re-searching the line each time.
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'annotations': {'timestamped': {'tag': 'timestamped', 'value': True}},
         'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema',
         'slot_usage': {'fish': {'description': 'The fish line the group maintains.',
                                 'name': 'fish',
                                 'required': True}},
         'unique_keys': {'tank_grain': {'unique_key_name': 'tank_grain',
                                        'unique_key_slots': ['research_group',
                                                             'fish']}}})

    research_group: int = Field(default=..., description="""The research group an entry belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember', 'ChemicalCabinetEntry', 'FishTankEntry']} })
    fish: Fish = Field(default=..., description="""The fish line the group maintains.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment', 'FishTankEntry']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class FishTankEntryCreate(ConfiguredBaseModel):
    """
    Create schema for FishTankEntry — id is server-generated.
    """
    research_group: int = Field(default=..., description="""The research group an entry belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember', 'ChemicalCabinetEntry', 'FishTankEntry']} })
    fish: FishCreate = Field(default=..., description="""The fish line the group maintains.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment', 'FishTankEntry']} })


class FishTankEntryUpdate(ConfiguredBaseModel):
    """
    Update schema for FishTankEntry — all fields optional for partial updates.
    """
    research_group: Optional[int] = Field(default=None, description="""The research group an entry belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember', 'ChemicalCabinetEntry', 'FishTankEntry']} })
    fish: Optional[FishCreate] = Field(default=None, description="""The fish line the group maintains.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment', 'FishTankEntry']} })


class FishTankEntryRead(ReadBaseModel):
    """
    Read schema for FishTankEntry — from_attributes=True, extra=ignore.
    """
    research_group: int = Field(default=..., description="""The research group an entry belongs to.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ResearchGroupMember', 'ChemicalCabinetEntry', 'FishTankEntry']} })
    fish: FishRead = Field(default=..., description="""The fish line the group maintains.""", json_schema_extra = { "linkml_meta": {'domain_of': ['Experiment', 'FishTankEntry']} })
    id: int = Field(default=..., description="""Auto-generated integer identifier.""", json_schema_extra = { "linkml_meta": {'domain_of': ['ZappEntity']} })


class QuantityValue(ConfiguredBaseModel):
    """
    A value of an attribute that is quantitative and measurable, expressed as a combination of a unit and a numeric value
    """
    linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://w3id.org/sierra-moxon/zebrafish-toxicology-atlas-schema'})

    unit: Optional[str] = Field(default=None, description="""The unit of the quantity value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['QuantityValue']} })
    numeric_value: Optional[str] = Field(default=None, description="""The numeric value of the quantity value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['QuantityValue']} })


class QuantityValueRead(ReadBaseModel):
    """
    Read schema for QuantityValue — from_attributes=True, extra=ignore.
    """
    unit: Optional[str] = Field(default=None, description="""The unit of the quantity value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['QuantityValue']} })
    numeric_value: Optional[str] = Field(default=None, description="""The numeric value of the quantity value.""", json_schema_extra = { "linkml_meta": {'domain_of': ['QuantityValue']} })


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ZappEntity.model_rebuild()
OntologyEntity.model_rebuild()
Study.model_rebuild()
StudyCreate.model_rebuild()
StudyUpdate.model_rebuild()
StudyRead.model_rebuild()
Experiment.model_rebuild()
ExperimentCreate.model_rebuild()
ExperimentUpdate.model_rebuild()
ExperimentRead.model_rebuild()
PhenotypeObservationSet.model_rebuild()
PhenotypeObservationSetCreate.model_rebuild()
PhenotypeObservationSetUpdate.model_rebuild()
PhenotypeObservationSetRead.model_rebuild()
Phenotype.model_rebuild()
PhenotypeCreate.model_rebuild()
PhenotypeUpdate.model_rebuild()
PhenotypeRead.model_rebuild()
Control.model_rebuild()
ControlCreate.model_rebuild()
ControlUpdate.model_rebuild()
ControlRead.model_rebuild()
ExposureEvent.model_rebuild()
ExposureEventCreate.model_rebuild()
ExposureEventUpdate.model_rebuild()
ExposureEventRead.model_rebuild()
Regimen.model_rebuild()
RegimenCreate.model_rebuild()
RegimenUpdate.model_rebuild()
RegimenRead.model_rebuild()
StressorChemical.model_rebuild()
StressorChemicalCreate.model_rebuild()
StressorChemicalUpdate.model_rebuild()
StressorChemicalRead.model_rebuild()
VehicleOfTransmission.model_rebuild()
VehicleOfTransmissionCreate.model_rebuild()
VehicleOfTransmissionUpdate.model_rebuild()
VehicleOfTransmissionRead.model_rebuild()
Image.model_rebuild()
ImageCreate.model_rebuild()
ImageUpdate.model_rebuild()
ImageRead.model_rebuild()
ControlImage.model_rebuild()
ControlImageCreate.model_rebuild()
ControlImageUpdate.model_rebuild()
ControlImageRead.model_rebuild()
PhenotypeTerm.model_rebuild()
PhenotypeTermRead.model_rebuild()
ExposureRoute.model_rebuild()
ExposureRouteRead.model_rebuild()
ExposureType.model_rebuild()
ExposureTypeRead.model_rebuild()
Fish.model_rebuild()
FishCreate.model_rebuild()
FishUpdate.model_rebuild()
FishRead.model_rebuild()
Genotype.model_rebuild()
GenotypeCreate.model_rebuild()
GenotypeUpdate.model_rebuild()
GenotypeRead.model_rebuild()
Cross.model_rebuild()
CrossCreate.model_rebuild()
CrossUpdate.model_rebuild()
CrossRead.model_rebuild()
MutantAllele.model_rebuild()
MutantAlleleCreate.model_rebuild()
MutantAlleleUpdate.model_rebuild()
MutantAlleleRead.model_rebuild()
TransgenicAllele.model_rebuild()
TransgenicAlleleCreate.model_rebuild()
TransgenicAlleleUpdate.model_rebuild()
TransgenicAlleleRead.model_rebuild()
ResearchGroup.model_rebuild()
ResearchGroupCreate.model_rebuild()
ResearchGroupUpdate.model_rebuild()
ResearchGroupRead.model_rebuild()
ResearchGroupMember.model_rebuild()
ResearchGroupMemberCreate.model_rebuild()
ResearchGroupMemberUpdate.model_rebuild()
ResearchGroupMemberRead.model_rebuild()
ChemicalCabinetEntry.model_rebuild()
ChemicalCabinetEntryCreate.model_rebuild()
ChemicalCabinetEntryUpdate.model_rebuild()
ChemicalCabinetEntryRead.model_rebuild()
FishTankEntry.model_rebuild()
FishTankEntryCreate.model_rebuild()
FishTankEntryUpdate.model_rebuild()
FishTankEntryRead.model_rebuild()
QuantityValue.model_rebuild()
QuantityValueRead.model_rebuild()

