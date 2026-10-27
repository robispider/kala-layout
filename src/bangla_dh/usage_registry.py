"""Immutable study registries: raw mapping bytes and text-free prompt families."""
import hashlib
import json
from pathlib import Path
import subprocess

from .paths import DATA, PROJECT_ROOT, output_path, write_json
from .usage_metric import require, strict_json
from .usage_scores import PROTOCOLS

VERSION = "usage-registry-v1"
DEFAULT = DATA / "usage-metric-registry/v1/registry.json"


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def mapping_hash(raw, default_style, style):
    """KalaLayoutSources.Create: raw SHA; alternate style hashes lowerhex:style."""
    value = digest(raw)
    return "sha256:" + (value if style == default_style else digest((value + ":" + style).encode("utf-8")))


def immutable_json(path, value):
    raw = (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    target = output_path(path)
    require(not target.exists() or target.read_bytes() == raw, "registry is immutable; choose a new version directory")
    if not target.exists(): target.write_bytes(raw)
    return target


def load(path=DEFAULT):
    path = Path(path).resolve()
    raw = path.read_bytes()
    registry = strict_json(raw)
    require(registry["schema"] == "kala.usage-metric.registry/1", "unsupported registry")
    inputs = {path.relative_to(PROJECT_ROOT).as_posix(): digest(raw)}
    identities = set()
    for entry in registry["mappings"]:
        identity = (entry["mapping_hash"], entry["engine_version"])
        require(identity not in identities, "duplicate mapping engine registry entry")
        identities.add(identity)
        if entry["status"] != "verified_mapping":
            continue
        source = (path.parent / entry["file"]).resolve()
        require(source.is_relative_to(path.parent), "mapping registry path escapes snapshot")
        contents = source.read_bytes()
        require(digest(contents) == entry["file_sha256"] and
                mapping_hash(contents, entry["default_style"], entry["style"]) == entry["mapping_hash"],
                "mapping registry hash mismatch")
        require(strict_json(contents) == entry["mapping"], "mapping registry content mismatch")
        inputs[source.relative_to(PROJECT_ROOT).as_posix()] = digest(contents)
    return registry, inputs


def build(dataset, kala_root, out=DEFAULT, mapping_paths=()):
    """Snapshot available mappings; missing imports remain explicit unresolved entries.

    Public banks are already archived by Kala Git. This repo records source hashes
    and family/work identities, never copies their passage texts into results.
    """
    from .usage_metric import audit_dataset
    dataset, kala_root, out = Path(dataset), Path(kala_root).resolve(), Path(out)
    audited = audit_dataset(dataset)[0]
    require(not audited["errors"], "audit failed; cannot register dataset")
    candidates = sorted((kala_root / "kala/layout/bn").glob("*.json"))
    candidates += sorted((DATA / "baselines/layouts").glob("*.json"))
    # Imported runtimes are key maps, not participant profiles or original archives.
    local = Path.home() / "AppData/Local/Kala/Layouts"
    candidates += sorted(local.glob("*/layout.json"))
    candidates += [Path(p).resolve() for p in mapping_paths]
    mappings, paths = [], []
    versions = sorted({(s["mapping_hash"], s["engine_version"]) for s in audited["sessions"]})
    for wanted, engine in versions:
        entry = {"mapping_hash": wanted, "engine_version": engine,
                 "status": "missing_mapping", "reason": "exact runtime mapping unavailable"}
        for candidate in candidates:
            raw = candidate.read_bytes()
            # Unrelated Kala assets (e.g. legacy alphabets) are not mappings and
            # need not satisfy this registry's strict mapping schema.
            possible = {"sha256:" + digest(raw)} | {"sha256:" + digest((digest(raw) + ":" + style).encode()) for style in ("layout-default", "avro-modern", "avro-old")}
            if wanted not in possible: continue
            definition = strict_json(raw)
            native = definition.get("type") != "avro-fixed"
            default = "layout-default" if native else "avro-modern"
            matched = next((s for s in (default, "avro-modern", "avro-old") if mapping_hash(raw, default, s) == wanted), None)
            if matched is None:
                continue
            name = "mappings/" + digest(raw) + ".json"
            target = output_path(out.parent / name)
            require(not target.exists() or target.read_bytes() == raw, "immutable mapping collision")
            if not target.exists(): target.write_bytes(raw)
            paths.append(target)
            entry.update(status="verified_mapping", reason=None, file=name, file_sha256=digest(raw),
                         mapping=definition, default_style=default, style=matched)
            break
        # The engine identity embeds a Kala Git revision. Record the exact
        # source hashes at that revision, rather than relabel today's composer.
        revision = engine.split("/", 1)[0].split("+")[-1]
        sources = {}
        for relative in ("kala/Keyboard/FixedLayoutManager.cs", "kala/Keyboard/AvroFixedLayoutManager.cs",
                         "kala/Keyboard/LayoutManagerFactory.cs", "kala/Layouts/FixedTypingStyles.cs",
                         "kala/Learning/Kala/KalaLayoutSources.cs", "kala/layout/bn/Alphabet.json"):
            result = subprocess.run(["git", "-C", str(kala_root), "show", f"{revision}:{relative}"], capture_output=True)
            if result.returncode == 0: sources[relative] = digest(result.stdout)
        entry.update(engine_revision=revision, engine_sources_sha256=sources,
                     engine_rules_status="source_hashes_only_requires_replay_validation")
        mappings.append(entry)
    protocols = []
    for protocol, version in sorted(PROTOCOLS.items()):
        bank = kala_root / "kala/learning-packs/kala.bn-typing-check" / version / "prompts.json"
        if not bank.exists(): continue
        raw = bank.read_bytes(); data = strict_json(raw)
        prompt_meta = []
        for p in data["prompts"]:
            provenance = p.get("provenance") or {}
            works = provenance.get("work_ids", [])
            # Shared source works, not just individual passage IDs, are held out.
            family = "work:" + digest("\0".join(sorted(works)).encode()) if works else "authored:" + digest(p["text"].encode())
            prompt_meta.append({"prompt_id": p["id"], "target_sha256": digest(p["text"].encode()),
                                "family": family, "work_ids": works,
                                "provenance_family": provenance.get("family_id"),
                                "passage_id": (p.get("passage") or {}).get("id")})
        protocols.append({"protocol": protocol, "bank_version": version,
                          "bank_sha256": digest(raw), "bank_source": bank.relative_to(kala_root).as_posix(),
                          "behavior": "timed-passages" if protocol.endswith(("-r4", "-r5")) else "sentence-enter",
                          "comparison": "NFC", "scorer": "kala-grapheme-v1", "prompts": prompt_meta})
    revision = subprocess.run(["git", "-C", str(kala_root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    preparation = {}
    for name in ("PromptBank.cs", "PromptCoverage.cs", "ResearchPromptSequence.cs", "TypingCheckController.cs", "SkillCheckScorer.cs"):
        path = kala_root / "kala/Learning/Study" / name
        preparation[path.relative_to(kala_root).as_posix()] = digest(path.read_bytes())
    value = {"schema": "kala.usage-metric.registry/1", "version": VERSION,
             "kala_repository": "https://github.com/robispider/kala", "kala_revision": revision,
             "preparation_sources_sha256": preparation, "mappings": mappings, "protocols": protocols,
             "limitations": ["A verified mapping hash is not validated engine replay.",
                             "Missing imported mappings must be supplied as exact runtime files.",
                             "Authored prompt near-duplicate family review remains pending."]}
    paths.append(immutable_json(out, value))
    return value, paths
