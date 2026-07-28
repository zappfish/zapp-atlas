SCHEMA_DIR := src/zapp_atlas/schema
LINKML_SCHEMA := $(SCHEMA_DIR)/zebrafish_toxicology_atlas_schema.yaml
PYDANTIC_OUTPUT := $(SCHEMA_DIR)/_gen/pydantic.py
PYDANTIC_CRUD_OUTPUT := $(SCHEMA_DIR)/_gen/pydantic_crud.py
SQLA_OUTPUT := $(SCHEMA_DIR)/_gen/sqla.py
TS_OUTPUT := ../client/src/schema/index.ts
JSON_SCHEMA_OUTPUT := ../client/src/schema/schema.json

# Files imported by the main schema — a change here must also trigger regen.
SCHEMA_IMPORTS := $(SCHEMA_DIR)/chemical_enums.yaml

.PHONY: schema
schema: $(PYDANTIC_OUTPUT) $(SQLA_OUTPUT) $(PYDANTIC_CRUD_OUTPUT) $(TS_OUTPUT) $(JSON_SCHEMA_OUTPUT)

$(PYDANTIC_OUTPUT): $(LINKML_SCHEMA) $(SCHEMA_IMPORTS)
	mkdir -p $(@D)
	echo "# GENERATED FILE. DO NOT EDIT." > $@
	uv run gen-pydantic $< >> $@

$(PYDANTIC_CRUD_OUTPUT): $(LINKML_SCHEMA) $(SCHEMA_IMPORTS)
	mkdir -p $(@D)
	echo "# GENERATED FILE. DO NOT EDIT." > $@
	uv run python -m zapp_atlas.schema.crud_pydanticgen $< >> $@

$(SQLA_OUTPUT): $(LINKML_SCHEMA) $(SCHEMA_IMPORTS)
	mkdir -p $(@D)
	echo "# GENERATED FILE. DO NOT EDIT." > $@
	uv run gen-sqla --declarative --sqla-style 2 $< >> $@

$(TS_OUTPUT): $(LINKML_SCHEMA)
	mkdir -p $(@D)
	echo "/*" > $@
	echo "GENERATED FILE. DO NOT EDIT." >> $@
	echo "*/" >> $@
	echo "" >> $@
	uv run gen-typescript $< >>$@

# JSON Schema for the client: runtime validation (Ajv) + type-safe unmarshalling.
# JSON has no comments, so the "do not edit" notice rides in the standard JSON Schema
# `$$comment` keyword, injected as the first key. ($$ escapes $ for Make.)
$(JSON_SCHEMA_OUTPUT): $(LINKML_SCHEMA)
	mkdir -p $(@D)
	uv run gen-json-schema $< \
		| jq '{"$$comment": "GENERATED FILE. DO NOT EDIT. Regenerate with `make schema`."} + .' > $@
