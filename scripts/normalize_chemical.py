"""
normalize_chemical.py
---------------------
CLI wrapper around the NCATS NodeNormalization API for chemical identifiers.
Intended to be called by a submission form backend; outputs JSON to stdout.

Usage
-----
    python normalize_chemical.py --id 16236 --namespace CHEBI
    python normalize_chemical.py --id 702 --namespace PUBCHEM.COMPOUND
    python normalize_chemical.py --id 50-00-0 --namespace CAS
    python normalize_chemical.py --id 16236 --namespace CHEBI --save-image ethanol.png
    python normalize_chemical.py --id 16236 --namespace CHEBI --skip-prefetch

Exit codes
----------
    0  success (even if the chemical was not found -- check result.normalized)
    1  bad arguments or namespace not allowed
    2  network / API error
"""

import argparse
import json
import sys
import requests
import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import Draw

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

NODE_NORM_BASE = "https://nodenormalization-sri.renci.org"

# Biolink classes we consider chemical-relevant
REL_BIOLINK = [
    "biolink:ChemicalEntity",
    "biolink:Drug",
    "biolink:ComplexMolecularMixture",
    "biolink:ChemicalOrDrugOrTreatment",
    "biolink:ChemicalMixture",
    "biolink:ChemicalEntityOrProteinOrPolypeptide",
    "biolink:SmallMolecule",
]

# Fallback namespace map when --skip-prefetch is used.
# Sourced from NodeNorm /get_curie_prefixes output captured in notebook cell 9
# (babel_version 2025sep1). Maps input prefix -> canonical prefix, preserving
# the original casing that NodeNorm uses (e.g. DrugCentral, UniProtKB).
FALLBACK_NAMESPACES = {
    "PUBCHEM.COMPOUND":  "PUBCHEM.COMPOUND",
    "INCHIKEY":          "INCHIKEY",
    "CAS":               "CAS",
    "HMDB":              "HMDB",
    "CHEMBL.COMPOUND":   "CHEMBL.COMPOUND",
    "UNII":              "UNII",
    "CHEBI":             "CHEBI",
    "MESH":              "MESH",
    "UMLS":              "UMLS",
    "DrugCentral":       "DrugCentral",
    "DRUGCENTRAL":       "DrugCentral",
    "GTOPDB":            "GTOPDB",
    "RXCUI":             "RXCUI",
    "DRUGBANK":          "DRUGBANK",
    "KEGG.COMPOUND":     "KEGG.COMPOUND",
    "UniProtKB":         "UniProtKB",
    "UNIPROTKB":         "UniProtKB",
    "ENSEMBL":           "ENSEMBL",
    "PR":                "PR",
}

# Pubchempy-compliant namespace names used for visualization lookups.
# https://docs.pubchempy.org/en/latest/api.html
ALLOWED_VISUALIZATION_NAMESPACES = {
    "PUBCHEM.COMPOUND": "cid",
    "SMILES":           "smiles",
    "SDF":              "sdf",
    "INCHIKEY":         "inchi",
}

# ---------------------------------------------------------------------------
# Node Norm API helpers
# ---------------------------------------------------------------------------

def get_node_norm_version_info():
    """Return babel version + biolink model metadata from /status."""
    r = requests.get("{}/status".format(NODE_NORM_BASE), timeout=15)
    r.raise_for_status()
    res = r.json()
    return {
        "babel_version":     res.get("babel_version"),
        "babel_version_url": res.get("babel_version_url"),
        "biolink_model_url": res.get("biolink_model", {}).get("url"),
    }


def get_curie_prefixes(semantic_types=None):
    """Return {biolink_type: {curie_prefix: {PREFIX: count}}} from /get_curie_prefixes."""
    params = {}
    if semantic_types:
        params["semantic_type"] = semantic_types if isinstance(semantic_types, list) else [semantic_types]
    r = requests.get("{}/get_curie_prefixes".format(NODE_NORM_BASE), params=params, timeout=15)
    r.raise_for_status()
    return r.json()


def fetch_allowed_namespaces(biolink_classes=None):
    """
    Query the live NodeNorm prefix list for the given biolink classes and return
    a dict mapping input prefix (and uppercase variant) -> canonical prefix,
    matching the same structure as FALLBACK_NAMESPACES.
    """
    prefs = get_curie_prefixes(semantic_types=biolink_classes or REL_BIOLINK)
    namespaces = {}
    for btype_data in prefs.values():
        for prefix in btype_data.get("curie_prefix", {}).keys():
            namespaces[prefix] = prefix
            namespaces[prefix.upper()] = prefix
    return namespaces


def query_node_normalizer(curies):
    """Query /get_normalized_nodes with one or more CURIEs. Returns raw JSON dict."""
    if isinstance(curies, str):
        curies = [curies]
    r = requests.get(
        "{}/get_normalized_nodes".format(NODE_NORM_BASE),
        params={
            "curie":                  curies,
            "conflate":               "false",
            "drug_chemical_conflate": "false",
            "description":            "true",
            "individual_types":       "false",
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def parse_norm_result(curie, raw):
    """
    Parse the raw NodeNorm response for a single CURIE into a clean dict.

    Returns
    -------
    dict with keys:
        normalized              bool
        primary_id              str | None
        label                   str | None
        description             str | None
        equivalent_identifiers  list[dict]  -- each has identifier / label / description
    """
    hit = raw.get(curie)
    if not hit:
        return {
            "normalized":             False,
            "primary_id":             None,
            "label":                  None,
            "description":            None,
            "equivalent_identifiers": [],
        }

    primary = hit.get("id", {})
    eqs = []
    for eq in hit.get("equivalent_identifiers", []):
        eqs.append({
            "identifier":  eq.get("identifier"),
            "label":       eq.get("label"),
            "description": eq.get("description"),
        })

    return {
        "normalized":             True,
        "primary_id":             primary.get("identifier"),
        "label":                  primary.get("label"),
        "description":            primary.get("description"),
        "equivalent_identifiers": eqs,
    }

# ---------------------------------------------------------------------------
# Visualization  (adapted from zapp_chemical_mappings.ipynb)
# ---------------------------------------------------------------------------

def get_visualization_data(norm_result, save_path=None):
    """
    Find the first visualizable identifier in norm_result's equivalent_identifiers,
    fetch from PubChem, build an RDKit mol, and optionally save a PNG.
    Returns a dict with: available, iupac_name, cid, repr, value, image_saved_to.
    """
    candidate = next(
        (eq["identifier"] for eq in norm_result.get("equivalent_identifiers", [])
         if eq.get("identifier") and eq["identifier"].split(":")[0] in ALLOWED_VISUALIZATION_NAMESPACES),
        None
    )

    if not candidate:
        return {"available": False, "reason": "No visualizable identifier in equivalent_identifiers"}

    nspace, val = candidate.split(":", 1)
    results = pcp.get_compounds(val, namespace=ALLOWED_VISUALIZATION_NAMESPACES[nspace])

    if not results:
        return {"available": False, "reason": "Compound not found in PubChem"}

    c = results[0]
    smiles = next(
        (s for s in [getattr(c, "isomeric_smiles", None), getattr(c, "canonical_smiles", None)]
         if isinstance(s, str) and s.strip()),
        None
    )

    mol, mol_repr, mol_value = Chem.MolFromSmiles(smiles) if smiles else None, "smiles", smiles
    if mol is None:
        inchi = getattr(c, "inchi", None)
        if isinstance(inchi, str) and inchi.strip():
            mol, mol_repr, mol_value = Chem.MolFromInchi(inchi), "inchi", inchi

    image_saved_to = None
    if mol is not None and save_path:
        Draw.MolToImage(mol, size=(400, 400), legend=getattr(c, "iupac_name", None) or "").save(save_path)
        image_saved_to = save_path

    return {
        "available":      mol is not None,
        "iupac_name":     getattr(c, "iupac_name", None),
        "cid":            getattr(c, "cid", None),
        "repr":           mol_repr if mol else None,
        "value":          mol_value if mol else None,
        "image_saved_to": image_saved_to,
    }

# ---------------------------------------------------------------------------
# Main normalization entry point
# ---------------------------------------------------------------------------

def normalize_chemical(chemical_id, namespace, allowed_namespaces=None, version_info=None, save_image=None):
    """
    Normalize a single chemical identifier and optionally produce a structure image.

    Parameters
    ----------
    chemical_id : str
        The identifier value without the namespace prefix (e.g. "16236").
    namespace : str
        The CURIE prefix (e.g. "CHEBI").
    allowed_namespaces : dict | None
        Maps accepted prefixes -> canonical prefix. Uses FALLBACK_NAMESPACES if None.
    version_info : dict | None
        Pre-fetched version info dict; omitted from output if None.
    save_image : str | None
        File path to save a structure PNG. Skipped if None.

    Returns
    -------
    dict -- the full output object ready for JSON serialisation.
    """
    if allowed_namespaces is None:
        allowed_namespaces = FALLBACK_NAMESPACES

    # Resolve to canonical casing (e.g. DRUGCENTRAL -> DrugCentral)
    canonical_ns = allowed_namespaces.get(namespace) or allowed_namespaces.get(namespace.upper())
    if canonical_ns is None:
        print(
            "ERROR: namespace '{}' is not in the allowed list.\nAllowed: {}".format(
                namespace, sorted(set(allowed_namespaces.values()))
            ),
            file=sys.stderr,
        )
        sys.exit(1)

    curie  = "{}:{}".format(canonical_ns, chemical_id)
    raw    = query_node_normalizer(curie)
    result = parse_norm_result(curie, raw)

    vis = {}
    if result["normalized"]:
        vis = get_visualization_data(result, save_path=save_image)

    return {
        "query": {
            "input_id":  chemical_id,
            "namespace": canonical_ns,
            "curie":     curie,
        },
        "node_norm_meta": version_info or {},
        "result":         result,
        "visualization":  vis,
    }

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser():
    p = argparse.ArgumentParser(
        description="Normalize a chemical identifier via the NCATS NodeNorm API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--id",        dest="chemical_id", help="Chemical identifier value (no prefix), e.g. 16236")
    p.add_argument("--namespace", dest="namespace",   help="CURIE namespace prefix, e.g. CHEBI, PUBCHEM.COMPOUND, CAS")
    p.add_argument(
        "--save-image",
        dest="save_image",
        default=None,
        help="Optional path to save a structure PNG (e.g. ethanol.png)",
    )
    p.add_argument(
        "--skip-prefetch",
        action="store_true",
        help="Skip live namespace/version prefetch and use hardcoded fallback (faster for form calls)",
    )
    return p


def main():
    parser = build_parser()
    args   = parser.parse_args()

    if not args.chemical_id or not args.namespace:
        parser.error("--id and --namespace are both required")

    if args.skip_prefetch:
        version_info       = {}
        allowed_namespaces = FALLBACK_NAMESPACES
    else:
        try:
            version_info       = get_node_norm_version_info()
            allowed_namespaces = fetch_allowed_namespaces()
        except requests.RequestException as e:
            print("ERROR: could not reach NodeNorm API -- {}".format(e), file=sys.stderr)
            sys.exit(2)

    try:
        output = normalize_chemical(
            args.chemical_id,
            args.namespace,
            allowed_namespaces=allowed_namespaces,
            version_info=version_info,
            save_image=args.save_image,
        )
    except requests.RequestException as e:
        print("ERROR: NodeNorm API request failed -- {}".format(e), file=sys.stderr)
        sys.exit(2)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
