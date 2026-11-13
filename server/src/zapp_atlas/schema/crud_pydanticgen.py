"""Pydantic model generator for the API's request and response shapes.

Extends LinkML's PydanticGenerator to emit, beside each class, the variants the
API speaks in:

* ``Input`` -- what the API accepts for a class: no server-generated ``id``,
  nested entities as their own Input variants, and -- for a class the API layout
  names as a level -- no slot holding the next level down, which is a resource
  of its own.
* ``Read`` -- what the API returns: every field, nested classes as their Read
  variants, built straight from ORM rows (``from_attributes=True``).
* ``Summary`` -- a Read that stops where the Input does, for listing a level
  without everything beneath it.
"""

import re
from dataclasses import dataclass

import click
from linkml.generators.pydanticgen.pydanticgen import PydanticGenerator
from linkml.generators.pydanticgen.template import (
    PydanticAttribute,
    PydanticClass,
    PydanticModule,
)
from linkml_runtime.utils.schemaview import SchemaView

from zapp_atlas.api.layout import Layout, SlotKind

READBASEMODEL_SRC = """class ReadBaseModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="ignore",
        arbitrary_types_allowed=True,
        use_enum_values=True,
    )"""


def _descendants(template: PydanticModule, sv: SchemaView, bases: set[str]) -> set[str]:
    """The concrete classes descending from any of ``bases``."""
    return {
        name
        for name in template.classes
        if not sv.get_class(name).abstract and bases & set(sv.class_ancestors(name))
    }


def _variant(
    cls: PydanticClass,
    suffix: str,
    *,
    base: str,
    description: str,
    without: set[str],
    nested: set[str],
    nested_suffix: str,
) -> PydanticClass:
    """A copy of ``cls`` minus some attributes, its nested classes swapped for theirs."""
    return PydanticClass(
        name=f"{cls.name}{suffix}",
        bases=base,
        description=description,
        attributes={
            name: _with_nested_variants(attr, nested, nested_suffix)
            for name, attr in (cls.attributes or {}).items()
            if name not in without
        }
        or None,
    )


def _with_nested_variants(
    attr: PydanticAttribute, class_names: set[str], suffix: str
) -> PydanticAttribute:
    """Point the class references in an attribute's type at their suffixed variants."""
    if not attr.range:
        return attr.model_copy()
    # One pass over whole words, so ``Control`` is not rewritten inside ``ControlImage``.
    swapped = re.sub(
        r"\b\w+\b",
        lambda word: word[0] + suffix if word[0] in class_names else word[0],
        attr.range,
    )
    return attr.model_copy(update={"range": swapped})


@dataclass
class CrudPydanticGenerator(PydanticGenerator):
    """PydanticGenerator subclass that adds the Input, Read and Summary variants."""

    def before_render_template(self, template: PydanticModule, sv: SchemaView) -> PydanticModule:
        layout = Layout(sv)
        entities = _descendants(template, sv, {"ZappEntity"})
        readable = _descendants(template, sv, {"ZappEntity", "OntologyEntity", "ZfinEntity"}) | {
            "QuantityValue"
        }

        classes: dict[str, PydanticClass] = {}
        for name, cls in template.classes.items():
            classes[name] = cls
            next_level = {s.name for s in layout.slots(name) if s.kind is SlotKind.LEVEL}

            if name in entities:
                classes[f"{name}Input"] = _variant(
                    cls,
                    "Input",
                    base="ConfiguredBaseModel",
                    description=f"What the API accepts for {name}.",
                    without=next_level | {"id"},
                    nested=entities,
                    nested_suffix="Input",
                )
            if name in readable:
                classes[f"{name}Read"] = _variant(
                    cls,
                    "Read",
                    base="ReadBaseModel",
                    description=f"What the API returns for {name}, with everything beneath it.",
                    without=set(),
                    nested=readable,
                    nested_suffix="Read",
                )
            if next_level:
                classes[f"{name}Summary"] = _variant(
                    cls,
                    "Summary",
                    base="ReadBaseModel",
                    description=f"What the API returns for {name} alone, without the next level.",
                    without=next_level,
                    nested=readable,
                    nested_suffix="Read",
                )

        template.injected_classes = [*(template.injected_classes or []), READBASEMODEL_SRC]
        template.classes = classes
        return template


@click.command()
@click.argument("yamlfile")
def cli(yamlfile: str) -> None:
    """Generate Pydantic models with the API's variants."""
    gen = CrudPydanticGenerator(schema=yamlfile)
    print(gen.serialize())


if __name__ == "__main__":
    cli()
