# GENERATED FILE. DO NOT EDIT.
from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    Time,
)
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


metadata = Base.metadata


class ZappEntity(Base):
    """
    Internal entities with auto-generated integer IDs.
    """

    __tablename__ = "ZappEntity"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)

    def __repr__(self):
        return f"ZappEntity(id={self.id},)"


class OntologyEntity(Base):
    """
    Entities representing ontology terms with URI identifiers.
    """

    __tablename__ = "OntologyEntity"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)

    def __repr__(self):
        return f"OntologyEntity(id={self.id},)"


class QuantityValue(Base):
    """
    A value of an attribute that is quantitative and measurable, expressed as a combination of a unit and a numeric value
    """

    __tablename__ = "QuantityValue"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True, autoincrement=True)
    unit: Mapped[str | None] = mapped_column(Text())
    numeric_value: Mapped[str | None] = mapped_column(Text())

    def __repr__(self):
        return f"QuantityValue(id={self.id},unit={self.unit},numeric_value={self.numeric_value},)"


class StudyAnnotator(Base):
    """
    None
    """

    __tablename__ = "Study_annotator"

    Study_id: Mapped[int] = mapped_column(Integer(), ForeignKey("Study.id"), primary_key=True)
    annotator: Mapped[str] = mapped_column(Text(), primary_key=True)

    def __repr__(self):
        return f"Study_annotator(Study_id={self.Study_id},annotator={self.annotator},)"


class StressorChemicalSynonym(Base):
    """
    None
    """

    __tablename__ = "StressorChemical_synonym"

    StressorChemical_id: Mapped[int] = mapped_column(Integer(), ForeignKey("StressorChemical.id"), primary_key=True)
    synonym: Mapped[str] = mapped_column(Text(), primary_key=True)

    def __repr__(self):
        return f"StressorChemical_synonym(StressorChemical_id={self.StressorChemical_id},synonym={self.synonym},)"


class VehicleOfTransmissionSynonym(Base):
    """
    None
    """

    __tablename__ = "VehicleOfTransmission_synonym"

    VehicleOfTransmission_id: Mapped[int] = mapped_column(Integer(), ForeignKey("VehicleOfTransmission.id"), primary_key=True)
    synonym: Mapped[str] = mapped_column(Text(), primary_key=True)

    def __repr__(self):
        return f"VehicleOfTransmission_synonym(VehicleOfTransmission_id={self.VehicleOfTransmission_id},synonym={self.synonym},)"


class Study(ZappEntity):
    """
    A toxicological investigation, including the experimental conditions and phenotypic outcomes, with information provenance.
    """

    __tablename__ = "Study"

    publication: Mapped[str | None] = mapped_column(Text())
    lab: Mapped[str | None] = mapped_column(Text())
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)

    # One-To-Many: OneToAnyMapping(source_class='Study', source_slot='experiment', mapping_type=None, target_class='Experiment', target_slot='Study_id', join_class=None, uses_join_table=None, multivalued=False)
    experiment: Mapped[list[Experiment]] = relationship(foreign_keys="[Experiment.Study_id]")

    annotator_rel: Mapped[list[StudyAnnotator]] = relationship()
    annotator: AssociationProxy[list[str]] = association_proxy(
        "annotator_rel",
        "annotator",
        creator=lambda x_: StudyAnnotator(annotator=x_),
    )

    def __repr__(self):
        return f"Study(publication={self.publication},lab={self.lab},id={self.id},)"

    __mapper_args__ = {"concrete": True}


class Experiment(ZappEntity):
    """
    A group of observations (phenotypic outcomes and their control) that are linked by a common exposure event and subject, and that are part of a study.
    """

    __tablename__ = "Experiment"

    standard_rearing_condition: Mapped[bool | None] = mapped_column(Boolean())
    rearing_condition_comment: Mapped[str | None] = mapped_column(Text())
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    Study_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("Study.id"))
    fish_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("Fish.id"))
    fish: Mapped[Fish | None] = relationship(foreign_keys=[fish_id])

    # One-To-Many: OneToAnyMapping(source_class='Experiment', source_slot='control', mapping_type=None, target_class='Control', target_slot='Experiment_id', join_class=None, uses_join_table=None, multivalued=False)
    control: Mapped[list[Control]] = relationship(foreign_keys="[Control.Experiment_id]")

    # One-To-Many: OneToAnyMapping(source_class='Experiment', source_slot='exposure_event', mapping_type=None, target_class='ExposureEvent', target_slot='Experiment_id', join_class=None, uses_join_table=None, multivalued=False)
    exposure_event: Mapped[list[ExposureEvent]] = relationship(foreign_keys="[ExposureEvent.Experiment_id]")

    def __repr__(self):
        return f"Experiment(standard_rearing_condition={self.standard_rearing_condition},rearing_condition_comment={self.rearing_condition_comment},id={self.id},Study_id={self.Study_id},fish_id={self.fish_id},)"

    __mapper_args__ = {"concrete": True}


class PhenotypeObservationSet(ZappEntity):
    """
    An observation set containing control and phenotypic outcome resulting from an exposure event.
    """

    __tablename__ = "PhenotypeObservationSet"

    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    ExposureEvent_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("ExposureEvent.id"))

    # One-To-Many: OneToAnyMapping(source_class='PhenotypeObservationSet', source_slot='image', mapping_type=None, target_class='Image', target_slot='PhenotypeObservationSet_id', join_class=None, uses_join_table=None, multivalued=False)
    image: Mapped[list[Image]] = relationship(foreign_keys="[Image.PhenotypeObservationSet_id]")

    # One-To-Many: OneToAnyMapping(source_class='PhenotypeObservationSet', source_slot='phenotype', mapping_type=None, target_class='Phenotype', target_slot='PhenotypeObservationSet_id', join_class=None, uses_join_table=None, multivalued=False)
    phenotype: Mapped[list[Phenotype]] = relationship(foreign_keys="[Phenotype.PhenotypeObservationSet_id]")

    # One-To-Many: OneToAnyMapping(source_class='PhenotypeObservationSet', source_slot='control_image', mapping_type=None, target_class='ControlImage', target_slot='PhenotypeObservationSet_id', join_class=None, uses_join_table=None, multivalued=False)
    control_image: Mapped[list[ControlImage]] = relationship(foreign_keys="[ControlImage.PhenotypeObservationSet_id]")

    def __repr__(self):
        return f"PhenotypeObservationSet(id={self.id},ExposureEvent_id={self.ExposureEvent_id},)"

    __mapper_args__ = {"concrete": True}


class Phenotype(ZappEntity):
    """
    Any measurable or visible trait change in the subject as a result of exposure.
    """

    __tablename__ = "Phenotype"

    stage: Mapped[str | None] = mapped_column(Text())
    severity: Mapped[str | None] = mapped_column(Enum('mild', 'moderate', 'severe', name='SeverityEnum'))
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    PhenotypeObservationSet_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("PhenotypeObservationSet.id"))
    prevalence_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("QuantityValue.id"))
    prevalence: Mapped[QuantityValue | None] = relationship(foreign_keys=[prevalence_id])
    phenotype_term_id_term_uri: Mapped[int | None] = mapped_column(Integer(), ForeignKey("PhenotypeTerm.term_uri"))
    phenotype_term_id: Mapped[PhenotypeTerm | None] = relationship(foreign_keys=[phenotype_term_id_term_uri])

    def __repr__(self):
        return f"Phenotype(stage={self.stage},severity={self.severity},id={self.id},PhenotypeObservationSet_id={self.PhenotypeObservationSet_id},prevalence_id={self.prevalence_id},phenotype_term_id_term_uri={self.phenotype_term_id_term_uri},)"

    __mapper_args__ = {"concrete": True}


class Control(ZappEntity):
    """
    A subject serves as a reference for assessing phenotypic outcome in the phenotype observation set.
    """

    __tablename__ = "Control"

    control_type: Mapped[str | None] = mapped_column(Text())
    comment: Mapped[str | None] = mapped_column(Text())
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    Experiment_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("Experiment.id"))
    vehicle_if_treated_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("VehicleOfTransmission.id"))
    vehicle_if_treated: Mapped[VehicleOfTransmission | None] = relationship(foreign_keys=[vehicle_if_treated_id])

    # One-To-Many: OneToAnyMapping(source_class='Control', source_slot='control_image', mapping_type=None, target_class='ControlImage', target_slot='Control_id', join_class=None, uses_join_table=None, multivalued=False)
    control_image: Mapped[list[ControlImage]] = relationship(foreign_keys="[ControlImage.Control_id]")

    def __repr__(self):
        return f"Control(control_type={self.control_type},comment={self.comment},id={self.id},Experiment_id={self.Experiment_id},vehicle_if_treated_id={self.vehicle_if_treated_id},)"

    __mapper_args__ = {"concrete": True}


class ExposureEvent(ZappEntity):
    """
    An occurrence in a study where a subject is exposed to a stressor under defined conditions.
    """

    __tablename__ = "ExposureEvent"

    exposure_start_stage: Mapped[str | None] = mapped_column(Text())
    exposure_end_stage: Mapped[str | None] = mapped_column(Text())
    comment: Mapped[str | None] = mapped_column(Text())
    additional_exposure_condition: Mapped[str | None] = mapped_column(Text())
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    Experiment_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("Experiment.id"))
    route_term_uri: Mapped[int | None] = mapped_column(Integer(), ForeignKey("ExposureRoute.term_uri"))
    route: Mapped[ExposureRoute | None] = relationship(foreign_keys=[route_term_uri])
    regimen_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("Regimen.id"))
    regimen: Mapped[Regimen | None] = relationship(foreign_keys=[regimen_id])
    exposure_type_term_uri: Mapped[int | None] = mapped_column(Integer(), ForeignKey("ExposureType.term_uri"))
    exposure_type: Mapped[ExposureType | None] = relationship(foreign_keys=[exposure_type_term_uri])

    # One-To-Many: OneToAnyMapping(source_class='ExposureEvent', source_slot='stressor', mapping_type=None, target_class='StressorChemical', target_slot='ExposureEvent_id', join_class=None, uses_join_table=None, multivalued=False)
    stressor: Mapped[list[StressorChemical]] = relationship(foreign_keys="[StressorChemical.ExposureEvent_id]")

    # One-To-Many: OneToAnyMapping(source_class='ExposureEvent', source_slot='vehicle', mapping_type=None, target_class='VehicleOfTransmission', target_slot='ExposureEvent_id', join_class=None, uses_join_table=None, multivalued=False)
    vehicle: Mapped[list[VehicleOfTransmission]] = relationship(foreign_keys="[VehicleOfTransmission.ExposureEvent_id]")

    # One-To-Many: OneToAnyMapping(source_class='ExposureEvent', source_slot='phenotype_observation', mapping_type=None, target_class='PhenotypeObservationSet', target_slot='ExposureEvent_id', join_class=None, uses_join_table=None, multivalued=False)
    phenotype_observation: Mapped[list[PhenotypeObservationSet]] = relationship(foreign_keys="[PhenotypeObservationSet.ExposureEvent_id]")

    def __repr__(self):
        return f"ExposureEvent(exposure_start_stage={self.exposure_start_stage},exposure_end_stage={self.exposure_end_stage},comment={self.comment},additional_exposure_condition={self.additional_exposure_condition},id={self.id},Experiment_id={self.Experiment_id},route_term_uri={self.route_term_uri},regimen_id={self.regimen_id},exposure_type_term_uri={self.exposure_type_term_uri},)"

    __mapper_args__ = {"concrete": True}


class Regimen(ZappEntity):
    """
    The schedule and pattern of an exposure event.
    """

    __tablename__ = "Regimen"

    exposure_regimen_type: Mapped[str | None] = mapped_column(Enum('continuous', 'repeated', name='ExposureRegimenTypeEnum'))
    number_of_individual_exposure: Mapped[int | None] = mapped_column(Integer())
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    interval_between_individual_exposures_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("QuantityValue.id"))
    interval_between_individual_exposures: Mapped[QuantityValue | None] = relationship(foreign_keys=[interval_between_individual_exposures_id])
    total_exposure_duration_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("QuantityValue.id"))
    total_exposure_duration: Mapped[QuantityValue | None] = relationship(foreign_keys=[total_exposure_duration_id])
    individual_exposure_duration_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("QuantityValue.id"))
    individual_exposure_duration: Mapped[QuantityValue | None] = relationship(foreign_keys=[individual_exposure_duration_id])

    def __repr__(self):
        return f"Regimen(exposure_regimen_type={self.exposure_regimen_type},number_of_individual_exposure={self.number_of_individual_exposure},id={self.id},interval_between_individual_exposures_id={self.interval_between_individual_exposures_id},total_exposure_duration_id={self.total_exposure_duration_id},individual_exposure_duration_id={self.individual_exposure_duration_id},)"

    __mapper_args__ = {"concrete": True}


class StressorChemical(ZappEntity):
    """
    A chemical that elicits a response (a phenotype) in a subject when encountered through exposure.
    """

    __tablename__ = "StressorChemical"

    chemical_id: Mapped[str | None] = mapped_column(Text())
    cas_id: Mapped[str | None] = mapped_column(Text())
    unrecognized_chemical_name: Mapped[str | None] = mapped_column(Text())
    manufacturer: Mapped[str | None] = mapped_column(Enum('sigma_aldrich', 'merck_kgaa', 'millipore_sigma', 'thermo_fisher_scientific', 'fisher_scientific', 'avantor', 'vwr', 'new_england_biolabs', 'bio_rad_laboratories', 'promega_corporation', 'corning_life_sciences', 'lonza_group', 'tocris_bioscience', 'cayman_chemical_company', 'selleck_chemicals', 'medchemexpress', 'enzo_life_sciences', 'aquaneering_inc', 'pentair_aquatic_eco_systems', 'tecniplast', 'zebrafish_international_resource_center', 'tokyo_chemical_industry', 'alfa_aesar', 'acros_organics', 'honeywell', 'abcam', 'cell_signaling_technology', 'genscript', 'addgene', 'thomas_scientific', 'cole_parmer', 'other_not_listed', name='ManufacturerEnum'))
    unrecognized_manufacturer_name: Mapped[str | None] = mapped_column(Text())
    comment: Mapped[str | None] = mapped_column(Text())
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    ExposureEvent_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("ExposureEvent.id"))
    concentration_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("QuantityValue.id"))
    concentration: Mapped[QuantityValue | None] = relationship(foreign_keys=[concentration_id])

    synonym_rel: Mapped[list[StressorChemicalSynonym]] = relationship()
    synonym: AssociationProxy[list[str]] = association_proxy(
        "synonym_rel",
        "synonym",
        creator=lambda x_: StressorChemicalSynonym(synonym=x_),
    )

    def __repr__(self):
        return f"StressorChemical(chemical_id={self.chemical_id},cas_id={self.cas_id},unrecognized_chemical_name={self.unrecognized_chemical_name},manufacturer={self.manufacturer},unrecognized_manufacturer_name={self.unrecognized_manufacturer_name},comment={self.comment},id={self.id},ExposureEvent_id={self.ExposureEvent_id},concentration_id={self.concentration_id},)"

    __mapper_args__ = {"concrete": True}


class VehicleOfTransmission(ZappEntity):
    """
    The substance or medium used to deliver a stressor to a subject during an exposure event.
    """

    __tablename__ = "VehicleOfTransmission"

    vehicle_type: Mapped[str] = mapped_column(Enum('acetone', 'acetonitrile', 'bsa', 'butanone_mek', 'cyclodextrin_hpbcd', 'dimethyl_formamide', 'dmso', 'embryonic_media', 'ethanol', 'glycerol', 'isopropanol', 'methanol', 'methylcellulose', 'pbs', 'polyethylene_glycol', 'propylene_glycol', 'solketal', 'water', 'other_not_listed', name='VehicleEnum'))
    chemical_id: Mapped[str | None] = mapped_column(Text())
    cas_id: Mapped[str | None] = mapped_column(Text())
    unrecognized_chemical_name: Mapped[str | None] = mapped_column(Text())
    manufacturer: Mapped[str | None] = mapped_column(Enum('sigma_aldrich', 'merck_kgaa', 'millipore_sigma', 'thermo_fisher_scientific', 'fisher_scientific', 'avantor', 'vwr', 'new_england_biolabs', 'bio_rad_laboratories', 'promega_corporation', 'corning_life_sciences', 'lonza_group', 'tocris_bioscience', 'cayman_chemical_company', 'selleck_chemicals', 'medchemexpress', 'enzo_life_sciences', 'aquaneering_inc', 'pentair_aquatic_eco_systems', 'tecniplast', 'zebrafish_international_resource_center', 'tokyo_chemical_industry', 'alfa_aesar', 'acros_organics', 'honeywell', 'abcam', 'cell_signaling_technology', 'genscript', 'addgene', 'thomas_scientific', 'cole_parmer', 'other_not_listed', name='ManufacturerEnum'))
    unrecognized_manufacturer_name: Mapped[str | None] = mapped_column(Text())
    comment: Mapped[str | None] = mapped_column(Text())
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    ExposureEvent_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("ExposureEvent.id"))
    concentration_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("QuantityValue.id"))
    concentration: Mapped[QuantityValue | None] = relationship(foreign_keys=[concentration_id])

    synonym_rel: Mapped[list[VehicleOfTransmissionSynonym]] = relationship()
    synonym: AssociationProxy[list[str]] = association_proxy(
        "synonym_rel",
        "synonym",
        creator=lambda x_: VehicleOfTransmissionSynonym(synonym=x_),
    )

    def __repr__(self):
        return f"VehicleOfTransmission(vehicle_type={self.vehicle_type},chemical_id={self.chemical_id},cas_id={self.cas_id},unrecognized_chemical_name={self.unrecognized_chemical_name},manufacturer={self.manufacturer},unrecognized_manufacturer_name={self.unrecognized_manufacturer_name},comment={self.comment},id={self.id},ExposureEvent_id={self.ExposureEvent_id},concentration_id={self.concentration_id},)"

    __mapper_args__ = {"concrete": True}


class Image(ZappEntity):
    """
    An image associated with a phenotype observation.
    """

    __tablename__ = "Image"

    magnification: Mapped[str | None] = mapped_column(Text())
    resolution: Mapped[str | None] = mapped_column(Text())
    scale_bar: Mapped[str | None] = mapped_column(Text())
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    PhenotypeObservationSet_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("PhenotypeObservationSet.id"))

    def __repr__(self):
        return f"Image(magnification={self.magnification},resolution={self.resolution},scale_bar={self.scale_bar},id={self.id},PhenotypeObservationSet_id={self.PhenotypeObservationSet_id},)"

    __mapper_args__ = {"concrete": True}


class ControlImage(ZappEntity):
    """
    An image associated with a control, taken at the same developmental stage as the corresponding phenotype observation.
    """

    __tablename__ = "ControlImage"

    phenotype_id: Mapped[str | None] = mapped_column(Text())
    magnification: Mapped[str | None] = mapped_column(Text())
    resolution: Mapped[str | None] = mapped_column(Text())
    scale_bar: Mapped[str | None] = mapped_column(Text())
    phenotype_comments: Mapped[str | None] = mapped_column(Text())
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    PhenotypeObservationSet_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("PhenotypeObservationSet.id"))
    Control_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("Control.id"))

    def __repr__(self):
        return f"ControlImage(phenotype_id={self.phenotype_id},magnification={self.magnification},resolution={self.resolution},scale_bar={self.scale_bar},phenotype_comments={self.phenotype_comments},id={self.id},PhenotypeObservationSet_id={self.PhenotypeObservationSet_id},Control_id={self.Control_id},)"

    __mapper_args__ = {"concrete": True}


class PhenotypeTerm(OntologyEntity):
    """
    A phenotype ontology term from the Zebrafish Phenotype ontology (ZP).
    """

    __tablename__ = "PhenotypeTerm"

    term_uri: Mapped[str] = mapped_column(Text(), primary_key=True)
    term_label: Mapped[str] = mapped_column(Text(), primary_key=True)

    def __repr__(self):
        return f"PhenotypeTerm(term_uri={self.term_uri},term_label={self.term_label},)"

    __mapper_args__ = {"concrete": True}


class ExposureRoute(OntologyEntity):
    """
    A route-of-exposure term. Term URIs are expected to be reachable from
EXO:0000154 (route of exposure) in the EXO ontology.

    """

    __tablename__ = "ExposureRoute"

    term_uri: Mapped[str] = mapped_column(Text(), primary_key=True)
    term_label: Mapped[str] = mapped_column(Text(), primary_key=True)

    def __repr__(self):
        return f"ExposureRoute(term_uri={self.term_uri},term_label={self.term_label},)"

    __mapper_args__ = {"concrete": True}


class ExposureType(OntologyEntity):
    """
    An exposure-type term from ECTO.

    """

    __tablename__ = "ExposureType"

    term_uri: Mapped[str] = mapped_column(Text(), primary_key=True)
    term_label: Mapped[str] = mapped_column(Text(), primary_key=True)

    def __repr__(self):
        return f"ExposureType(term_uri={self.term_uri},term_label={self.term_label},)"

    __mapper_args__ = {"concrete": True}


class Fish(ZappEntity):
    """
    A zebrafish subject in a study. Mirrors ZFIN's Fish object (GENO:0000525, "effective genotype"): a Fish is the combination of an intrinsic Genotype (mutant alleles, transgenics and wild-type background) and any transient gene-targeting reagents (STRs — morpholinos/CRISPRs). The STR / gene-targeting reagent component is out of scope for ZAPP at this time and is intentionally not modeled yet. The Fish carries its own ZFIN fish identifier (ZDB-FISH-…), which is distinct from the ZDB-GENO-… identifier of its Genotype; either may be absent for lab-specific fish not yet registered with ZFIN.
    """

    __tablename__ = "Fish"

    name: Mapped[str] = mapped_column(Text())
    fish_zfin_id: Mapped[str | None] = mapped_column(Text())
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    genotype_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("Genotype.id"))
    genotype: Mapped[Genotype | None] = relationship(foreign_keys=[genotype_id])
    cross_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("Cross.id"))
    cross: Mapped[Cross | None] = relationship(foreign_keys=[cross_id])

    def __repr__(self):
        return f"Fish(name={self.name},fish_zfin_id={self.fish_zfin_id},id={self.id},genotype_id={self.genotype_id},cross_id={self.cross_id},)"

    __mapper_args__ = {"concrete": True}


class Genotype(ZappEntity):
    """
    The intrinsic genotype of a fish (GENO:0000000) — equivalently, a *line*: the heritable combination of a wild-type genetic background plus any mutant allele(s) and transgenic insertion(s). Carries its own ZFIN genotype identifier (ZDB-GENO-…), which may differ from the fish identifier and may be absent if not yet registered.
Note the recursion: ``background`` is itself a Genotype. A wild-type strain such as AB is simply a Genotype with no alterations (ZFIN models this the same way — a fish's "Background ID" is a ZDB-GENO). There is therefore one concept here, not two: a background *is* a line.
    """

    __tablename__ = "Genotype"

    genotype_zfin_id: Mapped[str | None] = mapped_column(Text())
    genotype_name: Mapped[str | None] = mapped_column(Text())
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    background_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("Genotype.id"))
    background: Mapped[Genotype | None] = relationship(foreign_keys=[background_id], remote_side=[id])

    # One-To-Many: OneToAnyMapping(source_class='Genotype', source_slot='mutant_allele', mapping_type=None, target_class='MutantAllele', target_slot='Genotype_id', join_class=None, uses_join_table=None, multivalued=False)
    mutant_allele: Mapped[list[MutantAllele]] = relationship(foreign_keys="[MutantAllele.Genotype_id]")

    # One-To-Many: OneToAnyMapping(source_class='Genotype', source_slot='transgenic_allele', mapping_type=None, target_class='TransgenicAllele', target_slot='Genotype_id', join_class=None, uses_join_table=None, multivalued=False)
    transgenic_allele: Mapped[list[TransgenicAllele]] = relationship(foreign_keys="[TransgenicAllele.Genotype_id]")

    def __repr__(self):
        return f"Genotype(genotype_zfin_id={self.genotype_zfin_id},genotype_name={self.genotype_name},id={self.id},background_id={self.background_id},)"

    __mapper_args__ = {"concrete": True}


class Cross(ZappEntity):
    """
    How the experimental animals were produced: the mating that generated the clutch, plus how the resulting genotype was established. An incross is represented by the same line on both sides.
This matters because a genotype is not derivable from the parents alone — it follows from the cross *plus* selection. A het × het incross segregates 1:2:1, so an unsorted clutch has no single genotype, and an unqualified phenotype prevalence from such a clutch may be a Mendelian ratio rather than a toxicological effect. ``progeny_selection`` is what distinguishes those.
    """

    __tablename__ = "Cross"

    progeny_selection: Mapped[str | None] = mapped_column(Enum('genotyped', 'phenotype_sorted', 'assumed_uniform', 'segregating', 'unknown', name='ProgenySelectionEnum'))
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    maternal_line_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("Genotype.id"))
    maternal_line: Mapped[Genotype | None] = relationship(foreign_keys=[maternal_line_id])
    paternal_line_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("Genotype.id"))
    paternal_line: Mapped[Genotype | None] = relationship(foreign_keys=[paternal_line_id])

    def __repr__(self):
        return f"Cross(progeny_selection={self.progeny_selection},id={self.id},maternal_line_id={self.maternal_line_id},paternal_line_id={self.paternal_line_id},)"

    __mapper_args__ = {"concrete": True}


class MutantAllele(ZappEntity):
    """
    A mutant allele (genomic feature) carried by the fish, together with its zygosity and the gene it affects. The allele identifier is a ZFIN genomic feature id (ZDB-ALT-…); ZAPP additionally records the affected gene (affected genomic region).
    """

    __tablename__ = "MutantAllele"

    allele_id: Mapped[str | None] = mapped_column(Text())
    allele_symbol: Mapped[str] = mapped_column(Text())
    alteration_type: Mapped[str | None] = mapped_column(Enum('point_mutation', 'substitution', 'deletion', 'insertion', 'indel', 'inversion', 'duplication', 'transgenic_insertion', 'complex_substitution', 'sequence_alteration', name='SequenceAlterationTypeEnum'))
    affected_gene_id: Mapped[str | None] = mapped_column(Text())
    affected_gene_symbol: Mapped[str | None] = mapped_column(Text())
    zygosity: Mapped[str | None] = mapped_column(Enum('homozygous', 'heterozygous', 'unknown', 'wild_type', name='ZygosityEnum'))
    mother_zygosity: Mapped[str | None] = mapped_column(Enum('homozygous', 'heterozygous', 'unknown', 'wild_type', name='ZygosityEnum'))
    father_zygosity: Mapped[str | None] = mapped_column(Enum('homozygous', 'heterozygous', 'unknown', 'wild_type', name='ZygosityEnum'))
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    Genotype_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("Genotype.id"))

    def __repr__(self):
        return f"MutantAllele(allele_id={self.allele_id},allele_symbol={self.allele_symbol},alteration_type={self.alteration_type},affected_gene_id={self.affected_gene_id},affected_gene_symbol={self.affected_gene_symbol},zygosity={self.zygosity},mother_zygosity={self.mother_zygosity},father_zygosity={self.father_zygosity},id={self.id},Genotype_id={self.Genotype_id},)"

    __mapper_args__ = {"concrete": True}


class TransgenicAllele(ZappEntity):
    """
    A transgenic insertion (genomic feature) carried by the fish, together with its zygosity and the transgenic construct it derives from. The allele identifier is a ZFIN genomic feature id (ZDB-ALT-…); the construct is a ZFIN transgenic construct (ZDB-TGCONSTRCT-…) used mainly for name display. The gene slots record the construct's driver / reporter gene so the atlas can be searched by gene across mutant and transgenic alleles alike.
    """

    __tablename__ = "TransgenicAllele"

    allele_id: Mapped[str | None] = mapped_column(Text())
    allele_symbol: Mapped[str] = mapped_column(Text())
    construct_id: Mapped[str | None] = mapped_column(Text())
    construct_name: Mapped[str | None] = mapped_column(Text())
    alteration_type: Mapped[str | None] = mapped_column(Enum('point_mutation', 'substitution', 'deletion', 'insertion', 'indel', 'inversion', 'duplication', 'transgenic_insertion', 'complex_substitution', 'sequence_alteration', name='SequenceAlterationTypeEnum'))
    affected_gene_id: Mapped[str | None] = mapped_column(Text())
    affected_gene_symbol: Mapped[str | None] = mapped_column(Text())
    zygosity: Mapped[str | None] = mapped_column(Enum('homozygous', 'heterozygous', 'unknown', 'wild_type', name='ZygosityEnum'))
    mother_zygosity: Mapped[str | None] = mapped_column(Enum('homozygous', 'heterozygous', 'unknown', 'wild_type', name='ZygosityEnum'))
    father_zygosity: Mapped[str | None] = mapped_column(Enum('homozygous', 'heterozygous', 'unknown', 'wild_type', name='ZygosityEnum'))
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    Genotype_id: Mapped[int | None] = mapped_column(Integer(), ForeignKey("Genotype.id"))

    def __repr__(self):
        return f"TransgenicAllele(allele_id={self.allele_id},allele_symbol={self.allele_symbol},construct_id={self.construct_id},construct_name={self.construct_name},alteration_type={self.alteration_type},affected_gene_id={self.affected_gene_id},affected_gene_symbol={self.affected_gene_symbol},zygosity={self.zygosity},mother_zygosity={self.mother_zygosity},father_zygosity={self.father_zygosity},id={self.id},Genotype_id={self.Genotype_id},)"

    __mapper_args__ = {"concrete": True}


class ResearchGroup(ZappEntity):
    """
    A named collection of users that have shared editing access.
    """

    __tablename__ = "ResearchGroup"

    name: Mapped[str] = mapped_column(Text())
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)

    def __repr__(self):
        return f"ResearchGroup(name={self.name},id={self.id},)"

    __mapper_args__ = {"concrete": True}


class ResearchGroupMember(ZappEntity):
    """
    Membership of an ORCID identity in a research group.
    """

    __tablename__ = "ResearchGroupMember"

    research_group: Mapped[int] = mapped_column(Integer(), ForeignKey("ResearchGroup.id"))
    member: Mapped[str] = mapped_column(Text())
    role: Mapped[str] = mapped_column(Enum('admin', 'member', name='ResearchGroupRoleEnum'))
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)

    def __repr__(self):
        return f"ResearchGroupMember(research_group={self.research_group},member={self.member},role={self.role},id={self.id},)"

    __mapper_args__ = {"concrete": True}


class ChemicalCabinetEntry(ZappEntity):
    """
    A chemical a research group keeps on hand. Recorded once, then reused to pre-fill curation instead of re-searching the chemical each time.
    """

    __tablename__ = "ChemicalCabinetEntry"

    research_group: Mapped[int] = mapped_column(Integer(), ForeignKey("ResearchGroup.id"))
    chemical_id: Mapped[str] = mapped_column(Text())
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)

    def __repr__(self):
        return f"ChemicalCabinetEntry(research_group={self.research_group},chemical_id={self.chemical_id},id={self.id},)"

    __mapper_args__ = {"concrete": True}


class FishTankEntry(ZappEntity):
    """
    A fish line a research group maintains. Recorded once, then reused to pre-fill curation instead of re-searching the line each time.
    """

    __tablename__ = "FishTankEntry"

    research_group: Mapped[int] = mapped_column(Integer(), ForeignKey("ResearchGroup.id"))
    id: Mapped[int] = mapped_column(Integer(), primary_key=True)
    fish_id: Mapped[int] = mapped_column(Integer(), ForeignKey("Fish.id"))
    fish: Mapped[Fish | None] = relationship(foreign_keys=[fish_id])

    def __repr__(self):
        return f"FishTankEntry(research_group={self.research_group},id={self.id},fish_id={self.fish_id},)"

    __mapper_args__ = {"concrete": True}

