"""
Extract chemical information from all ZFIN download files into a single unified TSV.

Each output row corresponds to one row from a source file and includes:
  - source_file
  - fish_id / experiment_id / pub_id / pmid
  - gene_symbol / gene_id       (gene expression files only)
  - disease_id / disease_name   (disease model file only)
  - anatomy_id / anatomy_name   (phenotype files)
  - quality_name                (phenotype quality, where present)
  - phenotype_effect            (ameliorated / exacerbated / abnormal / etc.)
  - exposure_type               (ZECO label)
  - chemical_ids                (pipe-separated CHEBI IDs)
  - chemical_names              (pipe-separated, aligned with chemical_ids)
"""

import os
import csv
import pandas as pd


DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "zfin_test_data")

# Column indices are 0-based throughout (subtract 1 from the 1-based positions above).
# Each file spec maps output field names to source column indices (0-based).
# Fields not present in a file are omitted (will be NaN in the final dataframe).

FILE_SPECS = {
    "fish_model_disease_chemical_2.txt": {
        "fish_id":         0,
        "experiment_id":   1,
        "disease_id":      3,
        "disease_name":    4,
        "pub_id":          5,
        "pmid":            6,
        "exposure_type":   9,   # ZECO label
        "chemical_ids":    10,
        "chemical_names":  11,
    },
    "ameliorated_phenotype_fish_with_chemicals_2.txt": {
        "fish_id":          0,
        "anatomy_id":       10,
        "anatomy_name":     11,
        "quality_name":     13,
        "phenotype_effect": 14,  # "ameliorated"
        "pub_id":           21,
        "experiment_id":    22,
        "exposure_type":    24,
        "chemical_ids":     25,
        "chemical_names":   26,
    },
    "phenotypes_modified_by_chemicals_ameliorated_or_exacerbated_2.txt": {
        "fish_id":          0,
        "anatomy_id":       10,
        "anatomy_name":     11,
        "quality_name":     13,
        "phenotype_effect": 14,  # "ameliorated" or "exacerbated"
        "pub_id":           21,
        "pmid":             22,
        "experiment_id":    23,
        "exposure_type":    25,
        "chemical_ids":     26,
        "chemical_names":   27,
    },
    "phenotype_fish_with_one_chemical_including_mutants_and_wt_2.txt": {
        "fish_id":          0,
        "anatomy_id":       10,
        "anatomy_name":     11,
        "quality_name":     13,
        "phenotype_effect": 14,
        "pub_id":           21,
        "pmid":             22,
        "experiment_id":    23,
        "exposure_type":    25,
        "chemical_ids":     26,
        "chemical_names":   27,
    },
    "phenotype_fish_with_chemicals_including_mutants_and_wt_2.txt": {
        "fish_id":          0,
        "gene_id":          2,
        "gene_symbol":      3,
        "anatomy_id":       14,
        "anatomy_name":     15,
        "quality_name":     17,
        "phenotype_effect": 18,
        "pub_id":           25,
        "pmid":             26,
        "experiment_id":    27,
        "exposure_type":    29,
        "chemical_ids":     30,
        "chemical_names":   31,
    },
    "gene_expression_phenotype_with_chemicals_2.txt": {
        "gene_symbol":      0,
        "gene_id":          1,
        "anatomy_name":     4,
        "anatomy_id":       5,
        "quality_name":     8,
        "phenotype_effect": 10,
        "fish_id":          20,
        "experiment_id":    21,
        "pub_id":           23,
        "pmid":             24,
        "exposure_type":    26,
        "chemical_ids":     27,  # may be pipe-separated
        "chemical_names":   28,  # may be pipe-separated
    },
    "gene_expression_phenotype_wildtype_with_one_chemical_2.txt": {
        "gene_symbol":      0,
        "gene_id":          1,
        "anatomy_name":     4,
        "anatomy_id":       5,
        "quality_name":     8,
        "phenotype_effect": 10,
        "fish_id":          20,
        "experiment_id":    21,
        "pub_id":           23,
        "pmid":             24,
        "exposure_type":    27,
        "chemical_ids":     28,
        "chemical_names":   29,
    },
}

# Canonical column order in output
OUTPUT_COLUMNS = [
    "source_file",
    "fish_id",
    "experiment_id",
    "pub_id",
    "pmid",
    "gene_symbol",
    "gene_id",
    "disease_id",
    "disease_name",
    "anatomy_id",
    "anatomy_name",
    "quality_name",
    "phenotype_effect",
    "exposure_type",
    "chemical_ids",
    "chemical_names",
]


def parse_file(filename: str, spec: dict) -> list[dict]:
    filepath = os.path.join(DATA_DIR, filename)
    rows = []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        for cols in reader:
            row = {"source_file": filename}
            for field, idx in spec.items():
                row[field] = cols[idx].strip() if idx < len(cols) else ""
            rows.append(row)
    return rows


def main():
    all_rows = []
    for filename, spec in FILE_SPECS.items():
        print(f"Parsing {filename}...")
        rows = parse_file(filename, spec)
        print(f"  {len(rows):,} rows")
        all_rows.extend(rows)

    df = pd.DataFrame(all_rows, columns=OUTPUT_COLUMNS)

    # Drop rows with no chemical ID at all
    df = df[df["chemical_ids"].str.strip().ne("")]

    # Normalise empty strings to NaN for cleaner output
    df.replace("", pd.NA, inplace=True)

    print(f"\nTotal rows: {len(df):,}")
    print(f"Unique chemical IDs (after splitting pipes): "
          f"{df['chemical_ids'].dropna().str.split('|').explode().nunique():,}")

    out_path = os.path.join(DATA_DIR, "zfin_chemicals_unified.tsv")
    df.to_csv(out_path, sep="\t", index=False)
    print(f"\nWritten to {out_path}")


if __name__ == "__main__":
    main()
