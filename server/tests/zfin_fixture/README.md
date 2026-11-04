# ZFIN fixture

Miniature copies of the five ZFIN bulk downloads `extdata/scripts/zfin_db.py`
reads, laid out row for row like the real files (tab-separated, no header;
column layouts in that script's docstring). The `zfin_db` fixture in
`conftest.py` runs the builder on them, so the tests exercise the same
parsing the bundle gets. Cases covered: a co-injected line (one allele, two
constructs, repeated rows), a `markers missing` row that is not a gene link,
a transgenic whose gene is only recorded on its fish, a fish kept on two
backgrounds, a morpholino hitting two paralogs, a two-allele genotype, a
unique name that doesn't parse, and an allele without an SO id.
