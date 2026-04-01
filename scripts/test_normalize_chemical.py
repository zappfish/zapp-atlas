"""
test_normalize_chemical.py
--------------------------
Test cases for normalize_chemical.py.
Exercises the full normalization pipeline against the live NodeNorm API.

Usage
-----
    python test_normalize_chemical.py
    python test_normalize_chemical.py --skip-prefetch

Exit codes
----------
    0  all tests passed
    1  one or more tests failed
    2  network / API error during setup
"""

import argparse
import sys
import requests

from normalize_chemical import (
    fetch_allowed_namespaces,
    get_node_norm_version_info,
    normalize_chemical,
    FALLBACK_NAMESPACES,
)

# ---------------------------------------------------------------------------
# Test cases
# Format: (label, chemical_id, namespace, expect_normalized, expected_primary_id)
# expected_primary_id is None if we only care about the normalized bool.
# ---------------------------------------------------------------------------

TEST_CASES = [
    # Known chemicals via different namespaces
    ("Ethanol via CHEBI",           "16236",        "CHEBI",            True,  "CHEBI:16236"),
    ("Ethanol via PubChem CID",     "702",          "PUBCHEM.COMPOUND", True,  "CHEBI:16236"),
    ("Formaldehyde via CAS",        "50-00-0",      "CAS",              True,  "CHEBI:16842"),
    ("Warfarin via CHEBI",          "10033",        "CHEBI",            True,  "CHEBI:10033"),
    ("Lithium Chloride via CHEBI",  "48607",        "CHEBI",            True,  "CHEBI:48607"),
    ("Gentamicin via PubChem CID",  "3467",         "PUBCHEM.COMPOUND", True,  None),
    # Chemicals without CHEBI IDs -- should still normalize to something
    ("BIO (GSK-3 inhibitor)",       "448949",       "PUBCHEM.COMPOUND", True,  None),
    ("Dorsomorphin",                "11524144",     "PUBCHEM.COMPOUND", True,  None),
    # Namespace casing variants
    ("Ethanol, lowercase namespace","16236",        "chebi",            True,  "CHEBI:16236"),
    ("DrugCentral casing variant",  "1076",         "DRUGCENTRAL",      True,  None),
    # Should NOT normalize
    ("Nonexistent CHEBI ID",        "ZAPP-999999",  "CHEBI",            False, None),
]

SEP = "=" * 65


def run_tests(allowed_namespaces, version_info):
    print("\nNodeNorm version: {}".format(version_info.get("babel_version", "unknown")))
    print("Running {} test cases...\n".format(len(TEST_CASES)))

    passed = 0
    failed = 0

    for label, cid, ns, expect_norm, expect_primary in TEST_CASES:
        print(SEP)
        print("TEST: {}  [{}:{}]".format(label, ns, cid))

        try:
            output = normalize_chemical(
                cid, ns,
                allowed_namespaces=allowed_namespaces,
                version_info=version_info,
            )
            result = output["result"]
            vis    = output.get("visualization", {})

            norm_ok    = result["normalized"] == expect_norm
            primary_ok = (expect_primary is None) or (result["primary_id"] == expect_primary)
            ok = norm_ok and primary_ok

            status = "PASS" if ok else "FAIL"
            if ok:
                passed += 1
            else:
                failed += 1

            print("  {}  normalized={}  primary_id={}  label={}".format(
                status,
                result["normalized"],
                result["primary_id"],
                result["label"],
            ))

            if not norm_ok:
                print("  ** expected normalized={}".format(expect_norm))
            if not primary_ok:
                print("  ** expected primary_id={}".format(expect_primary))

            if result["description"]:
                print("  description: {}".format(result["description"][:100]))

            if vis.get("available"):
                print("  visualization: cid={}  iupac={}  repr={}".format(
                    vis.get("cid"), vis.get("iupac_name"), vis.get("repr")
                ))
            else:
                print("  visualization: not available -- {}".format(
                    vis.get("reason") or vis.get("error", "mol build failed")
                ))

        except SystemExit as e:
            # normalize_chemical calls sys.exit(1) for bad namespace
            print("  FAIL  SystemExit({}) -- bad namespace or arg".format(e.code))
            failed += 1
        except Exception as e:
            print("  ERROR  {}".format(e))
            failed += 1

    print(SEP)
    print("\nResults: {}/{} passed".format(passed, len(TEST_CASES)))
    return failed == 0


def build_parser():
    p = argparse.ArgumentParser(description="Run normalize_chemical test suite.")
    p.add_argument(
        "--skip-prefetch",
        action="store_true",
        help="Use hardcoded fallback namespaces instead of querying NodeNorm live",
    )
    return p


def main():
    args = build_parser().parse_args()

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

    success = run_tests(allowed_namespaces, version_info)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
