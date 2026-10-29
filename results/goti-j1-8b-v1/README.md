# Durable Goti J1 evidence

The source search and report manifests are retained byte for byte. Paths in them
name the original `work/` locations; `run-manifest.json` maps those paths to this
archive and records both compressed and decompressed SHA-256 hashes. No corpus
texts are included. `REPORT.md` is the original report; its `search/A.json` link
refers to the lossless `search/A.json.gz` archive here. The complete 8,000 seeded
records, all 241 endpoints, confirmation records, settings and maps are retained.

From the repository root: `PYTHONPATH=src python -m bangla_dh.goti_evidence`.
Verification reads only this archive and tracked frozen inputs, independently
rescores every retained endpoint with exact integer coefficients, and checks the
52 published assignments. It runs no search and certifies no optimum.
To inspect the original JSON use Python's standard-library `gzip.open`.
Search replay uses the command in `REPORT.md` at its recorded source revision
`010ee328d92f8a0f066b89dadfeb89090b0ab877` in a separate checkout.
