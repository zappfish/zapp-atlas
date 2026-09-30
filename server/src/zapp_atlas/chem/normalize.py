"""Client for the NCATS NodeNormalization and SRI Name Resolution services.

NodeNorm maps any chemical CURIE to its clique: a preferred identifier, a
label, and every equivalent identifier it knows. The Name Resolver maps free
text to candidate CURIEs, which are then normalized the same way. PubChem
supplies structures (SMILES) for identifiers the local ChEBI cache has none
for.

All of these are network calls; callers are expected to handle
``httpx.HTTPError`` and fall back to the local cache.
"""

from typing import Any

import httpx
import pubchempy as pcp

NODE_NORM_BASE = "https://nodenormalization-sri.renci.org"
NAME_RESOLVER_BASE = "https://name-resolution-sri.renci.org"
TIMEOUT = 15.0

# Biolink classes we consider chemical-relevant.
REL_BIOLINK = [
    "biolink:ChemicalEntity",
    "biolink:Drug",
    "biolink:ComplexMolecularMixture",
    "biolink:ChemicalOrDrugOrTreatment",
    "biolink:ChemicalMixture",
    "biolink:ChemicalEntityOrProteinOrPolypeptide",
    "biolink:SmallMolecule",
    "biolink:MacromolecularComplex",
    "biolink:MolecularEntity",
]

# CURIE prefixes accepted from the Name Resolver, mapped to NodeNorm's casing.
# Sourced from NodeNorm /get_curie_prefixes (babel_version 2025sep1).
NAMESPACES = {
    "PUBCHEM.COMPOUND": "PUBCHEM.COMPOUND",
    "INCHIKEY": "INCHIKEY",
    "CAS": "CAS",
    "HMDB": "HMDB",
    "CHEMBL.COMPOUND": "CHEMBL.COMPOUND",
    "UNII": "UNII",
    "CHEBI": "CHEBI",
    "MESH": "MESH",
    "UMLS": "UMLS",
    "DrugCentral": "DrugCentral",
    "DRUGCENTRAL": "DrugCentral",
    "GTOPDB": "GTOPDB",
    "RXCUI": "RXCUI",
    "DRUGBANK": "DRUGBANK",
    "KEGG.COMPOUND": "KEGG.COMPOUND",
    "UniProtKB": "UniProtKB",
    "UNIPROTKB": "UniProtKB",
    "ENSEMBL": "ENSEMBL",
    "PR": "PR",
}

# Namespaces PubChem can look a structure up by, mapped to pubchempy's names.
VISUALIZATION_NAMESPACES = {
    "PUBCHEM.COMPOUND": "cid",
    "SMILES": "smiles",
    "INCHIKEY": "inchikey",
}


def empty_result() -> dict[str, Any]:
    return {
        "normalized": False,
        "primary_id": None,
        "label": None,
        "description": None,
        "biolink_type": None,
        "equivalent_identifiers": [],
    }


def query_node_normalizer(curies: list[str]) -> dict[str, Any]:
    """Query NodeNorm /get_normalized_nodes for one or more CURIEs; return raw JSON."""
    r = httpx.get(
        f"{NODE_NORM_BASE}/get_normalized_nodes",
        params={
            "curie": curies,
            "conflate": "false",
            "drug_chemical_conflate": "false",
            "description": "true",
            "individual_types": "true",
        },
        timeout=TIMEOUT,
    )
    r.raise_for_status()
    return r.json()


def parse_node_norm(curie: str, raw: dict[str, Any]) -> dict[str, Any]:
    """Pull the result for one CURIE out of a raw NodeNorm response."""
    result = empty_result()
    hit = raw.get(curie)
    if not hit:
        return result
    primary = hit.get("id", {})
    result.update(
        {
            "normalized": True,
            "primary_id": primary.get("identifier"),
            "label": primary.get("label"),
            "description": primary.get("description"),
            "biolink_type": hit.get("type"),
            "equivalent_identifiers": [
                {
                    "identifier": eq.get("identifier"),
                    "label": eq.get("label"),
                    "description": eq.get("description"),
                }
                for eq in hit.get("equivalent_identifiers", [])
            ],
        }
    )
    return result


def normalize_curie(curie: str) -> dict[str, Any]:
    """Normalize a single CURIE, e.g. ``CHEBI:16236``, through NodeNorm."""
    return parse_node_norm(curie, query_node_normalizer([curie]))


def resolve_name(name: str, limit: int = 10) -> list[dict[str, Any]]:
    """Resolve a chemical name to normalized results, best match first.

    Every Name Resolver hit in an accepted namespace is normalized in one batch
    call, and hits that land in the same clique are collapsed, so the result is
    a list of distinct candidates.
    """
    r = httpx.get(
        f"{NAME_RESOLVER_BASE}/lookup",
        params={
            "string": name,
            "autocomplete": "false",
            "highlighting": "false",
            "offset": 0,
            "limit": limit,
            "biolink_type": REL_BIOLINK,
        },
        timeout=TIMEOUT,
    )
    r.raise_for_status()

    curies = []
    for hit in r.json():
        prefix, sep, local_id = hit.get("curie", "").partition(":")
        canonical = NAMESPACES.get(prefix) or NAMESPACES.get(prefix.upper())
        if sep and canonical:
            curies.append(f"{canonical}:{local_id}")
    if not curies:
        return []

    raw = query_node_normalizer(curies)
    results = []
    seen: set[str] = set()
    for curie in curies:
        result = parse_node_norm(curie, raw)
        primary_id = result["primary_id"]
        if result["normalized"] and primary_id and primary_id not in seen:
            seen.add(primary_id)
            results.append(result)
    return results


def find_visualizable_curie(equivalent_identifiers: list[dict[str, Any]]) -> str | None:
    """Return the first identifier PubChem can look a structure up by, if any."""
    return next(
        (
            eq["identifier"]
            for eq in equivalent_identifiers
            if eq.get("identifier")
            and eq["identifier"].split(":", 1)[0] in VISUALIZATION_NAMESPACES
        ),
        None,
    )


def fetch_smiles(curie: str) -> str | None:
    """Fetch a SMILES string for a visualizable CURIE from PubChem."""
    prefix, _, value = curie.partition(":")
    namespace = VISUALIZATION_NAMESPACES.get(prefix)
    if namespace is None:
        return None
    if namespace == "smiles":
        return value

    compounds = pcp.get_compounds(value, namespace=namespace)
    if not compounds:
        return None
    compound = compounds[0]
    # PubChem renamed its SMILES properties in 2025; newer pubchempy exposes
    # `smiles`, older releases only the isomeric/canonical pair.
    for attr in ("smiles", "isomeric_smiles", "canonical_smiles"):
        smiles = getattr(compound, attr, None)
        if isinstance(smiles, str) and smiles.strip():
            return smiles
    return None
