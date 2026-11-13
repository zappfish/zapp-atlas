# /// script
# requires-python = ">=3.12"
# dependencies = ["typer==0.19.2"]
# ///
"""Write manifest.json: what the bundle was built from, and what is in it.

Records the bundle's input hash (its name), each upstream source's URL and,
for ontologies, the owl:versionIRI read from the downloaded file, and the
size and sha256 of every file in the output directory.
"""

import csv
import gzip
import hashlib
import json
import re
from pathlib import Path
from typing import Annotated

import typer

VERSION_IRI = re.compile(r'<owl:versionIRI rdf:resource="([^"]+)"')


def version_iri(path: Path) -> str | None:
    """The owl:versionIRI from an RDF/XML file's header, if it has one."""
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as f:
        for _, line in zip(range(200), f, strict=False):
            if match := VERSION_IRI.search(line):
                return match.group(1)
    return None


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def main(
    dist: Annotated[Path, typer.Argument(help="Bundle output directory")],
    bundle_hash: Annotated[str, typer.Option("--hash", help="Input hash naming this bundle")],
    sources_tsv: Annotated[
        Path,
        typer.Option(
            "--sources",
            help="TSV of upstream inputs, one per row: name, URL, downloaded path",
        ),
    ],
) -> None:
    sources = {}
    with sources_tsv.open(newline="") as f:
        rows = list(csv.reader(f, delimiter="\t"))
    for name, url, downloaded in rows:
        path = Path(downloaded)
        entry = {"url": url}
        if path.name.endswith((".owl", ".owl.gz")) and (iri := version_iri(path)):
            entry["version_iri"] = iri
        sources[name] = entry

    manifest_path = dist / "manifest.json"
    files = {
        path.name: {"bytes": path.stat().st_size, "sha256": sha256(path)}
        for path in sorted(dist.iterdir())
        if path.is_file() and path != manifest_path
    }

    manifest = {"hash": bundle_hash, "sources": sources, "files": files}
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    typer.run(main)
