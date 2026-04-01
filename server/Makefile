SCHEMA_DIR := src/zapp_atlas/schema
LINKML_SCHEMA := $(SCHEMA_DIR)/zebrafish_toxicology_atlas_schema.yaml
PYDANTIC_OUTPUT := $(SCHEMA_DIR)/_gen/pydantic.py
SQLA_OUTPUT := $(SCHEMA_DIR)/_gen/sqla.py

.PHONY: schema
schema: $(PYDANTIC_OUTPUT) $(SQLA_OUTPUT)

$(PYDANTIC_OUTPUT): $(LINKML_SCHEMA) $(SCHEMA_DIR)/generators/crud_pydanticgen.py
	mkdir -p $(@D)
	echo "# GENERATED FILE. DO NOT EDIT." > $@
	uv run gen-pydantic $< >> $@
	uv run ruff format $@

$(SQLA_OUTPUT): $(LINKML_SCHEMA)
	mkdir -p $(@D)
	echo "# GENERATED FILE. DO NOT EDIT." > $@
	uv run gen-sqla --declarative --sqla-style 2 $< >> $@
	uv run ruff format $@

.PHONY: test
test:
	uv run pytest
