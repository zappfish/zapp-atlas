SCHEMA_DIR := src/zapp_atlas/schema
LINKML_SCHEMA := $(SCHEMA_DIR)/zebrafish_toxicology_atlas_schema.yaml
PYDANTIC_OUTPUT := $(SCHEMA_DIR)/_gen/pydantic.py
PYDANTIC_CRUD_OUTPUT := $(SCHEMA_DIR)/_gen/pydantic_crud.py
SQLA_OUTPUT := $(SCHEMA_DIR)/_gen/sqla.py

.PHONY: schema
schema: $(PYDANTIC_OUTPUT) $(SQLA_OUTPUT) $(PYDANTIC_CRUD_OUTPUT)

$(PYDANTIC_OUTPUT): $(LINKML_SCHEMA)
	mkdir -p $(@D)
	echo "# GENERATED FILE. DO NOT EDIT." > $@
	uv run gen-pydantic $< >> $@

$(PYDANTIC_CRUD_OUTPUT): $(LINKML_SCHEMA)
	mkdir -p $(@D)
	echo "# GENERATED FILE. DO NOT EDIT." > $@
	uv run python -m zapp_atlas.schema.crud_pydanticgen $< >> $@

$(SQLA_OUTPUT): $(LINKML_SCHEMA)
	mkdir -p $(@D)
	echo "# GENERATED FILE. DO NOT EDIT." > $@
	uv run gen-sqla --declarative --sqla-style 2 $< >> $@
