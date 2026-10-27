# Empirical study registries

These are separate from frozen search inputs. `v1/registry.json` contains exact available mapping snapshots, mapping+engine identities, historical engine source hashes, bank/source hashes and text-free source-work families. It deliberately retains missing imports and unresolved engine/family review states.

The client convention is raw-file SHA-256 for the default style. An alternate style uses SHA-256 of UTF-8 `lowercase_raw_hash:style`. Imported runtime JSON, not an import GUID or localized display name, is the mapping identity. The original runtime bytes are stored with their SHA-256 and checked again on load.

The historical UniJoy file was recovered exactly. Historical UniBijoy hash `sha256:920ff482e85a2d0002b0e63f235171a0c049276302b1034148c142dba6a5a638` is not recoverable from the currently available imports. Do not replace it with a similarly named layout. Pass the exact recovered runtime to register-usage-data in a new version directory.

Bank passage texts are not duplicated here. They remain in versioned Kala bank sources, identified by hashes; the registry stores prompt hashes and family/work identities. Authored near-duplicate review and engine replay validation are pending. Changing a status string alone is not validation evidence.

`candidates/` contains symbol-only physical mappings for the frozen research A/D layouts, with explicit grammar identifiers. The experimental evaluator refuses missing models and unsupported contexts. These files do not change the Kala application or its published layout rankings.
