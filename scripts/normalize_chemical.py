"""
normalize_chemical.py
---------------------
CLI wrapper around the NCATS NodeNormalization and SRI Name Resolution APIs
for chemical identifiers.
Intended to be called by a submission form backend; outputs JSON or TSV to stdout.

Usage
-----
    # Normalize by ID
    python normalize_chemical.py --id 16236 --namespace CHEBI
    python normalize_chemical.py --id 702 --namespace PUBCHEM.COMPOUND
    python normalize_chemical.py --id 50-00-0 --namespace CAS

    # Normalize by name
    python normalize_chemical.py --name "ethanol"
    python normalize_chemical.py --name "ethanol" --hits 5

    # Output format
    python normalize_chemical.py --name "ethanol" --format tsv
    python normalize_chemical.py --name "ethanol" --format json

    # Save a structure image (auto-selects first visualizable identifier)
    python normalize_chemical.py --name "ethanol" --save-image ethanol.png
    python normalize_chemical.py --id 16236 --namespace CHEBI --save-image ethanol.png

    # Visualize a CURIE directly (standalone, no normalization)
    python normalize_chemical.py --visualize PUBCHEM.COMPOUND:702
    python normalize_chemical.py --visualize PUBCHEM.COMPOUND:702 --save-image water.png

    # Skip optional prefetch steps
    python normalize_chemical.py --name "ethanol" --skip-version
    python normalize_chemical.py --name "ethanol" --skip-namespace-lookup
    python normalize_chemical.py --name "ethanol" --skip-version --skip-namespace-lookup

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

# ── Constants ──────────────────────────────────────────────────────────────────

NODE_NORM_BASE     = "https://nodenormalization-sri.renci.org"
NAME_RESOLVER_BASE = "https://name-resolution-sri.renci.org"

# Biolink classes we consider chemical-relevant
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

# Fallback namespace map when --skip-namespace-lookup is used.
# Sourced from NodeNorm /get_curie_prefixes (babel_version 2025sep1).
# Maps input prefix -> canonical prefix, preserving NodeNorm casing.
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

# Namespaces that can be looked up in PubChem for structure visualization.
# Values are pubchempy namespace argument names.
VISUALIZATION_NAMESPACES = {
    "PUBCHEM.COMPOUND": "cid",
    "SMILES":           "smiles",
    "INCHIKEY":         "inchi",
}

# ── API helpers ────────────────────────────────────────────────────────────────

def fetch_version_info():
    """Fetch babel/biolink version metadata from NodeNorm /status."""
    r = requests.get("{}/status".format(NODE_NORM_BASE), timeout=15)
    r.raise_for_status()
    d = r.json()
    return {
        "babel_version":     d.get("babel_version"),
        "babel_version_url": d.get("babel_version_url"),
        "biolink_model_url": d.get("biolink_model", {}).get("url"),
    }


def fetch_namespace_prefixes(biolink_classes=None):
    """
    Fetch the live namespace prefix list from NodeNorm /get_curie_prefixes.
    Returns {prefix: canonical_prefix}, same structure as FALLBACK_NAMESPACES.
    """
    r = requests.get(
        "{}/get_curie_prefixes".format(NODE_NORM_BASE),
        params={"semantic_type": biolink_classes or REL_BIOLINK},
        timeout=15,
    )
    r.raise_for_status()
    namespaces = {}
    for btype_data in r.json().values():
        for prefix in btype_data.get("curie_prefix", {}).keys():
            namespaces[prefix] = prefix
            namespaces[prefix.upper()] = prefix
    return namespaces


def _query_node_normalizer(curies):
    """Query NodeNorm /get_normalized_nodes with one or more CURIEs. Returns raw JSON."""
    if isinstance(curies, str):
        curies = [curies]
    r = requests.get(
        "{}/get_normalized_nodes".format(NODE_NORM_BASE),
        params={
            "curie":                  curies,
            "conflate":               "false",
            "drug_chemical_conflate": "false",
            "description":            "true",
            "individual_types":       "true",
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def _query_name_resolver(name, limit=10):
    """Query SRI Name Resolver /lookup for a chemical name. Returns list of hits."""
    r = requests.get(
        "{}/lookup".format(NAME_RESOLVER_BASE),
        params={
            "string":       name,
            "autocomplete": "false",
            "highlighting": "false",
            "offset":       0,
            "limit":        limit,
            "biolink_type": REL_BIOLINK,
        },
        timeout=15,
    )
    r.raise_for_status()
    return r.json()

# ── Core normalization ─────────────────────────────────────────────────────────

def _empty_result():
    return {
        "normalized":             False,
        "primary_id":             None,
        "label":                  None,
        "description":            None,
        "biolink_type":           None,
        "equivalent_identifiers": [],
    }


def _parse_node_norm(curie, raw):
    """Parse a raw NodeNorm response for one CURIE into a clean result dict."""
    result = _empty_result()
    hit    = raw.get(curie)
    if not hit:
        return result
    primary = hit.get("id", {})
    result.update({
        "normalized":  True,
        "primary_id":  primary.get("identifier"),
        "label":       primary.get("label"),
        "description": primary.get("description"),
        "biolink_type": hit.get("type"),
        "equivalent_identifiers": [
            {
                "identifier":  eq.get("identifier"),
                "label":       eq.get("label"),
                "description": eq.get("description"),
            }
            for eq in hit.get("equivalent_identifiers", [])
        ],
    })
    return result


def normalize_curie(curie):
    """
    Normalize a single CURIE through NodeNorm.

    Parameters
    ----------
    curie : str
        A fully-formed CURIE, e.g. "CHEBI:16236" or "PUBCHEM.COMPOUND:702".

    Returns
    -------
    dict with keys: normalized, primary_id, label, description, biolink_type,
                    equivalent_identifiers
    """
    raw = _query_node_normalizer(curie)
    return _parse_node_norm(curie, raw)


def lookup(input_value, namespace=None, namespaces=None, hits=10, meta=None):
    """
    Unified entry point for chemical lookup.

    Resolves a bare identifier + namespace (ID mode) or a free-text chemical
    name (name mode), normalizes through NodeNorm, and returns a consistent
    output dict with the same shape in both modes.

    Parameters
    ----------
    input_value : str
        A chemical name ("ethanol") or bare identifier ("16236").
    namespace : str | None
        CURIE prefix (e.g. "CHEBI"). If provided, ID mode is used.
        If None, name resolution mode is used.
    namespaces : dict | None
        Allowed prefix map {input_prefix: canonical_prefix}.
        Defaults to FALLBACK_NAMESPACES.
    hits : int
        Max name-resolver results to include in output (default: 10).
    meta : dict | None
        Pre-fetched version/namespace metadata to embed in output.

    Returns
    -------
    dict with keys:
        query               -- input, namespace, curie, mode
        meta                -- babel/biolink version info + fetch flags
        name_resolver_hits  -- list of hits (always present; empty in ID mode)
        result              -- normalized result dict (same shape in both modes)
    """
    if namespaces is None:
        namespaces = FALLBACK_NAMESPACES

    name_resolver_hits = []
    results            = []

    if namespace is not None:
        # ── ID mode ──
        canonical_ns = namespaces.get(namespace) or namespaces.get(namespace.upper())
        if canonical_ns is None:
            raise ValueError(
                "Namespace '{}' is not in the allowed list.\nAllowed: {}".format(
                    namespace, sorted(set(namespaces.values()))
                )
            )
        curie  = "{}:{}".format(canonical_ns, input_value)
        result = normalize_curie(curie)
        results = [result] if result["normalized"] else []
        query  = {"input": input_value, "namespace": canonical_ns, "curie": curie, "mode": "id"}

    else:
        # ── Name mode ──
        # Collect valid CURIEs from all name-resolver hits, then normalize in
        # one batch call so we surface multiple distinct candidates.
        hits_list          = _query_name_resolver(input_value, limit=hits)
        name_resolver_hits = hits_list
        result             = _empty_result()
        resolved_curie     = None

        if hits_list:
            valid_curies = []
            for hit in hits_list:
                curie = hit.get("curie", "")
                if ":" in curie:
                    raw_ns, cid  = curie.split(":", 1)
                    canonical_ns = namespaces.get(raw_ns) or namespaces.get(raw_ns.upper())
                    if canonical_ns:
                        valid_curies.append("{}:{}".format(canonical_ns, cid))

            if valid_curies:
                resolved_curie = valid_curies[0]
                raw_norm       = _query_node_normalizer(valid_curies)
                seen_primary   = set()
                for curie in valid_curies:
                    r   = _parse_node_norm(curie, raw_norm)
                    pid = r.get("primary_id")
                    if r["normalized"] and pid and pid not in seen_primary:
                        seen_primary.add(pid)
                        results.append(r)
                if results:
                    result = results[0]

        query = {"input": input_value, "namespace": None, "curie": resolved_curie, "mode": "name"}

    return {
        "query":              query,
        "meta":               meta or {},
        "name_resolver_hits": name_resolver_hits,
        "result":             result,
        "results":            results,
    }

# ── Visualization ──────────────────────────────────────────────────────────────

def find_visualizable_curie(equivalent_identifiers):
    """
    Return the first CURIE from a list of equivalent identifiers whose namespace
    is supported for PubChem visualization (PUBCHEM.COMPOUND, SMILES, INCHIKEY).
    Returns None if none are found.
    """
    return next(
        (
            eq["identifier"]
            for eq in equivalent_identifiers
            if eq.get("identifier")
            and eq["identifier"].split(":")[0] in VISUALIZATION_NAMESPACES
        ),
        None,
    )


def visualize_chemical(curie, save_path=None):
    """
    Fetch structure data for a CURIE from PubChem and optionally save a PNG image.

    Accepts any CURIE whose namespace is in VISUALIZATION_NAMESPACES.
    The CURIE is typically obtained from find_visualizable_curie() applied to
    a lookup() result, or passed directly (e.g. from --visualize CLI mode).

    Parameters
    ----------
    curie : str
        A visualizable CURIE, e.g. "PUBCHEM.COMPOUND:702".
    save_path : str | None
        File path to write a 400x400 structure PNG. Skipped if None.

    Returns
    -------
    dict with keys: available, iupac_name, cid, smiles, inchi, image_saved_to
    On failure: available=False plus a reason string.
    """
    ns, _, val = curie.partition(":")
    if ns not in VISUALIZATION_NAMESPACES:
        return {
            "available": False,
            "reason":    "Namespace '{}' is not visualizable. Supported: {}".format(
                ns, list(VISUALIZATION_NAMESPACES)
            ),
        }

    compounds = pcp.get_compounds(val, namespace=VISUALIZATION_NAMESPACES[ns])
    if not compounds:
        return {"available": False, "reason": "Compound not found in PubChem"}

    c      = compounds[0]
    smiles = next(
        (s for s in [getattr(c, "isomeric_smiles", None), getattr(c, "canonical_smiles", None)]
         if isinstance(s, str) and s.strip()),
        None,
    )
    mol   = Chem.MolFromSmiles(smiles) if smiles else None
    inchi = getattr(c, "inchi", None)

    if mol is None and isinstance(inchi, str) and inchi.strip():
        mol = Chem.MolFromInchi(inchi)

    image_saved_to = None
    if mol is not None and save_path:
        Draw.MolToImage(mol, size=(400, 400), legend=getattr(c, "iupac_name", None) or "").save(save_path)
        image_saved_to = save_path

    return {
        "available":      mol is not None,
        "iupac_name":     getattr(c, "iupac_name", None),
        "cid":            getattr(c, "cid", None),
        "smiles":         smiles,
        "inchi":          inchi,
        "image_saved_to": image_saved_to,
    }


def draw_chemical(curie, size=(600, 600)):
    """
    Return a PIL Image of a chemical structure for a given CURIE.

    Designed for direct interactive use — works with IPython display() or
    as the last expression in a Jupyter cell:

        display(draw_chemical("PUBCHEM.COMPOUND:702"))
        draw_chemical("PUBCHEM.COMPOUND:702")   # last cell expression also works

    Parameters
    ----------
    curie : str
        A visualizable CURIE, e.g. "PUBCHEM.COMPOUND:702".
    size : tuple
        Pixel dimensions (width, height). Default (600, 600).

    Returns
    -------
    PIL.Image | None
        None if the compound cannot be found or visualized.
    """
    vis = visualize_chemical(curie)
    if not vis.get("available"):
        return None
    mol = Chem.MolFromSmiles(vis["smiles"]) if vis.get("smiles") else None
    if mol is None and vis.get("inchi"):
        mol = Chem.MolFromInchi(vis["inchi"])
    if mol is None:
        return None
    return Draw.MolToImage(mol, size=size, legend=vis.get("iupac_name") or "")

# ── Output formatting ──────────────────────────────────────────────────────────

def _flatten(data, prefix=""):
    """Recursively flatten a nested dict to [(dotted.key, value)] pairs."""
    items = []
    for k, v in data.items():
        key = "{}.{}".format(prefix, k) if prefix else k
        if isinstance(v, dict):
            items.extend(_flatten(v, key))
        elif isinstance(v, list):
            items.append((key, json.dumps(v)))
        else:
            items.append((key, "" if v is None else v))
    return items


def format_output(data, fmt="json"):
    """
    Serialize output data to a string.

    Parameters
    ----------
    data : dict
    fmt  : "json" (default) | "tsv"
        json -- pretty-printed JSON
        tsv  -- two-column key/value table; lists are serialized as JSON strings
    """
    if fmt == "json":
        return json.dumps(data, indent=2)
    if fmt == "tsv":
        rows = ["field\tvalue"] + ["{}\t{}".format(k, v) for k, v in _flatten(data)]
        return "\n".join(rows)
    raise ValueError("Unknown format: {}".format(fmt))

# ── CLI ────────────────────────────────────────────────────────────────────────

def build_parser():
    p = argparse.ArgumentParser(
        description="Normalize a chemical identifier or name via NCATS NodeNorm / SRI Name Resolver.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--name",      dest="name",        help="Chemical name to resolve (e.g. 'ethanol')")
    mode.add_argument("--id",        dest="chemical_id", help="Chemical identifier value without prefix (e.g. 16236)")
    mode.add_argument("--visualize", dest="visualize",   help="Visualize a CURIE directly (e.g. PUBCHEM.COMPOUND:702)")

    p.add_argument("--namespace",            dest="namespace",  help="CURIE namespace prefix, required with --id (e.g. CHEBI, PUBCHEM.COMPOUND, CAS)")
    p.add_argument("--hits",                 dest="hits",       type=int, default=10, help="Max name-resolver hits to return (default: 10)")
    p.add_argument("--format",               dest="fmt",        choices=["json", "tsv"], default="json", help="Output format (default: json)")
    p.add_argument("--save-image",           dest="save_image", default=None, help="Path to save a structure PNG (e.g. ethanol.png)")
    p.add_argument("--skip-version",         action="store_true", help="Skip fetching babel/biolink version info from NodeNorm")
    p.add_argument("--skip-namespace-lookup",action="store_true", help="Skip live namespace prefix fetch; use hardcoded fallback")
    return p


def main():
    parser = build_parser()
    args   = parser.parse_args()

    if args.chemical_id and not args.namespace:
        parser.error("--namespace is required when using --id")

    # ── Standalone visualize mode ──────────────────────────────────────────────
    if args.visualize:
        try:
            vis = visualize_chemical(args.visualize, save_path=args.save_image)
        except Exception as e:
            print("ERROR: {}".format(e), file=sys.stderr)
            sys.exit(2)
        print(format_output(vis, args.fmt))
        return

    # ── Prefetch meta ──────────────────────────────────────────────────────────
    meta = {}
    try:
        if not args.skip_version:
            meta.update(fetch_version_info())
        namespaces = FALLBACK_NAMESPACES if args.skip_namespace_lookup else fetch_namespace_prefixes()
    except requests.RequestException as e:
        print("ERROR: could not reach NodeNorm API -- {}".format(e), file=sys.stderr)
        sys.exit(2)

    meta["namespaces_fetched"] = not args.skip_namespace_lookup

    # ── Normalize ──────────────────────────────────────────────────────────────
    try:
        output = lookup(
            args.name or args.chemical_id,
            namespace=args.namespace,
            namespaces=namespaces,
            hits=args.hits,
            meta=meta,
        )
    except ValueError as e:
        print("ERROR: {}".format(e), file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as e:
        print("ERROR: API request failed -- {}".format(e), file=sys.stderr)
        sys.exit(2)

    # ── Optional visualization (auto-selects first visualizable identifier) ────
    if args.save_image and output["result"]["normalized"]:
        vis_curie = find_visualizable_curie(output["result"]["equivalent_identifiers"])
        output["visualization"] = (
            visualize_chemical(vis_curie, save_path=args.save_image)
            if vis_curie
            else {"available": False, "reason": "No visualizable identifier in equivalent_identifiers"}
        )

    print(format_output(output, args.fmt))


if __name__ == "__main__":
    main()
