# Build the extdata bundle: ontology files the app ships read-only.
#
#   make            build everything into dist/
#   make clean      remove dist/ and tmp/
#
# Runs on the host and needs only docker and uv. ROBOT runs inside its pinned
# Docker image; the small Python steps run with `uv run --script`.
# Downloads and intermediates go in tmp/, the bundle in dist/. See README.md.

include sources.mk

ROBOT_IMAGE := obolibrary/robot:v1.9.10
ROBOT = docker run --rm -u $(shell id -u):$(shell id -g) -v $(CURDIR):/work -w /work \
	-e ROBOT_JAVA_ARGS=-Xmx8G -e ROBOT_PLUGINS_DIRECTORY=/work/tmp/plugins \
	$(ROBOT_IMAGE) robot
PY = uv run --quiet --script

# The bundle's name: a hash of this directory's inputs (see hash.sh).
EXTDATA_HASH ?= $(shell ./hash.sh)

DIST := dist
TMP := tmp

# Every rule that transforms data depends on this file, which holds its
# recipe: the bundle's hash covers the Makefile, so a recipe change must
# rebuild what it produces, not just relabel stale output with a new hash.
# Downloads don't depend on it; they only change when sources.mk does.
RECIPES := Makefile

BUNDLE := \
	$(DIST)/zp.json $(DIST)/zp.json.gz \
	$(DIST)/zfa.json $(DIST)/zfa.json.gz \
	$(DIST)/zfin_counts.tsv \
	$(DIST)/labels.db

.PHONY: all clean
.DELETE_ON_ERROR:

all: $(DIST)/manifest.json

clean:
	rm -rf $(DIST) $(TMP)

$(DIST) $(TMP) $(TMP)/plugins:
	mkdir -p $@

# --- Downloads ---------------------------------------------------------------

$(TMP)/zapp.owl: sources.mk | $(TMP)
	curl -fsSL -o $@ $(ZAPP_URL)

$(TMP)/fish_to_phenotype.tsv: sources.mk | $(TMP)
	curl -fsSL -o $@ $(FISH_TO_PHENOTYPE_URL)

$(TMP)/zfa.owl: sources.mk | $(TMP)
	curl -fsSL -o $@ $(ZFA_URL)

$(TMP)/chebi_lite.owl.gz: sources.mk | $(TMP)
	curl -fsSL -o $@ $(CHEBI_URL)

# ROBOT finds plugins by file name: this one is invoked as `robot upheno:...`.
$(TMP)/plugins/upheno.jar: sources.mk | $(TMP)/plugins
	curl -fsSL -o $@ $(UPHENO_PLUGIN_URL)

# --- Filtering ---------------------------------------------------------------
#
# Each ontology is filtered down to what the phenotype picker reads: labels,
# definitions, synonyms (with no axiom annotations), and the relationships
# that build its hierarchies. Obsolete terms and logical axioms are dropped.
# The same filtered OWL produces both the OBO JSON and the server's labels,
# so the client and server agree on which terms exist.

KEEP_ANNOTATIONS := annotations-to-keep.txt

# TEMPORARY: the uPheno plugin step adds the UPHENO:0000003 edges ZP should
# already carry; it must run before the equivalence axioms it reads are
# removed. Drop it (and UPHENO_PLUGIN_URL) once a ZP release includes them.
$(TMP)/zp.owl: $(TMP)/zapp.owl $(TMP)/plugins/upheno.jar \
		sparql/zapp-preferred-label.ru $(KEEP_ANNOTATIONS) $(RECIPES)
	$(ROBOT) \
		upheno:extract-upheno-relations --input $< \
			--relation UPHENO:0000003 \
			--root-phenotype http://purl.obolibrary.org/obo/ZP_0000000 \
		query --update sparql/zapp-preferred-label.ru \
		remove --select "owl:deprecated='true'^^xsd:boolean" \
		remove --axioms "equivalent disjoint" \
		remove --term http://purl.obolibrary.org/obo/BFO_0000051 \
			--axioms subclass --signature true \
		filter --select "<http://purl.obolibrary.org/obo/ZP_*>" \
			--trim false --drop-axiom-annotations all \
		remove --select annotation-properties --exclude-terms $(KEEP_ANNOTATIONS) \
		remove --select object-properties \
			--exclude-term http://purl.obolibrary.org/obo/UPHENO_0000003 \
		--output $@

# part_of (BFO:0000050) is the other parent relation frogpot builds the
# anatomy hierarchy from, alongside is_a.
$(TMP)/zfa-filtered.owl: $(TMP)/zfa.owl $(KEEP_ANNOTATIONS) $(RECIPES)
	$(ROBOT) \
		remove --input $< --select "owl:deprecated='true'^^xsd:boolean" \
		remove --axioms "equivalent disjoint" \
		filter --select "<http://purl.obolibrary.org/obo/ZFA_*>" \
			--trim false --drop-axiom-annotations all \
		remove --select annotation-properties --exclude-terms $(KEEP_ANNOTATIONS) \
		remove --select object-properties \
			--exclude-term http://purl.obolibrary.org/obo/BFO_0000050 \
		--output $@

# ChEBI is only used to render labels, so keep nothing else.
#
# Decompressed first: ROBOT 1.9.10 fails on gzipped input looking for a
# catalog file (fixed in 1.9.11, which has no Docker image yet).
$(TMP)/chebi.owl: $(TMP)/chebi_lite.owl.gz sparql/labels-only.rq $(RECIPES)
	gzip -dc $< > $(TMP)/chebi_lite.owl
	$(ROBOT) query --input $(TMP)/chebi_lite.owl --format ttl \
		--construct sparql/labels-only.rq $(TMP)/chebi.ttl
	$(ROBOT) convert --input $(TMP)/chebi.ttl --output $@
	rm $(TMP)/chebi_lite.owl $(TMP)/chebi.ttl

# --- Outputs -----------------------------------------------------------------

$(DIST)/zp.json: $(TMP)/zp.owl $(RECIPES) | $(DIST)
	$(ROBOT) convert --input $< --format json --output $@

$(DIST)/zfa.json: $(TMP)/zfa-filtered.owl $(RECIPES) | $(DIST)
	$(ROBOT) convert --input $< --format json --output $@

$(DIST)/%.json.gz: $(DIST)/%.json $(RECIPES)
	gzip -9 --no-name --keep --force $<

# ID and label of every class, for the server's label lookups. Classes with
# no label (the GO and other terms ZP refers to, ChEBI's obsolete terms) are
# skipped when the table is built.
$(TMP)/%-labels.tsv: $(TMP)/%.owl $(RECIPES)
	$(ROBOT) export --input $< --include classes --header "ID|LABEL" --export $@

$(DIST)/labels.db: $(TMP)/zp-labels.tsv $(TMP)/zfa-filtered-labels.tsv $(TMP)/chebi-labels.tsv \
		scripts/labels_db.py $(RECIPES) | $(DIST)
	$(PY) scripts/labels_db.py $@ $(filter %.tsv,$^)

$(DIST)/zfin_counts.tsv: $(TMP)/fish_to_phenotype.tsv scripts/zfin_counts.py $(RECIPES) | $(DIST)
	$(PY) scripts/zfin_counts.py $< $@

# Always rewritten (it takes a moment): it records the current hash, which can
# change without any data file needing a rebuild, e.g. after a comment edit.
.PHONY: $(DIST)/manifest.json
$(DIST)/manifest.json: $(BUNDLE) scripts/manifest.py
	printf '%s\t%s\t%s\n' \
		zp '$(ZAPP_URL)' $(TMP)/zapp.owl \
		zfin_fish_to_phenotype '$(FISH_TO_PHENOTYPE_URL)' $(TMP)/fish_to_phenotype.tsv \
		zfa '$(ZFA_URL)' $(TMP)/zfa.owl \
		chebi '$(CHEBI_URL)' $(TMP)/chebi_lite.owl.gz \
		upheno_plugin '$(UPHENO_PLUGIN_URL)' $(TMP)/plugins/upheno.jar \
		> $(TMP)/sources.tsv
	$(PY) scripts/manifest.py $(DIST) --hash $(EXTDATA_HASH) --sources $(TMP)/sources.tsv
