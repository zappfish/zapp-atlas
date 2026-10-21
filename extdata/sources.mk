# Pinned upstream inputs for the extdata bundle.
#
# Every URL here names a fixed release, never "latest": the bundle is
# identified by a hash of the files in this directory (see hash.sh), so an
# input that could change behind a stable URL would change the data without
# changing its name.

# Zebrafish Phenotype Ontology: the ZAPP subset, and the fish-to-phenotype
# annotations the ZFIN usage counts are derived from.
ZP_RELEASE := v2026-10-08
ZP_BASE    := https://github.com/obophenotype/zebrafish-phenotype-ontology/releases/download/$(ZP_RELEASE)
ZAPP_URL   := $(ZP_BASE)/zapp.owl
FISH_TO_PHENOTYPE_URL := $(ZP_BASE)/fish_to_phenotype.tsv

# Zebrafish Anatomy Ontology.
ZFA_URL := http://purl.obolibrary.org/obo/zfa/releases/2026-07-16/zfa.owl

# ChEBI "lite" (labels and hierarchy only), latest archived release.
CHEBI_URL := https://ftp.ebi.ac.uk/pub/databases/chebi/archive/rel255/ontology/chebi_lite.owl.gz

# TEMPORARY: the uPheno ROBOT plugin, used to add UPHENO:0000003
# ("phenotype is associated with entity") edges that the ZAPP subset should
# already carry. Remove it, and the step that uses it in the Makefile, once a
# ZP release includes those edges.
UPHENO_PLUGIN_URL := https://github.com/monarch-initiative/monarch-robot-plugins/releases/download/v0.0.3/monarch-robot-extensions.jar
