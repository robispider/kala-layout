"""A second guard: original outputs inside the project are also protected."""
from pathlib import Path
from ..paths import PROJECT_ROOT, output_path
from ..reference import sha256_file


def new_run_directory(path) -> Path:
    target = Path(path).resolve()
    roots = [PROJECT_ROOT / "work" / "evaluator-experiments", PROJECT_ROOT / "results" / "evaluator-e1"]
    if not any(target.is_relative_to(root.resolve()) and target != root.resolve() for root in roots):
        raise ValueError("output must be a new child of work/evaluator-experiments or results/evaluator-e1")
    if target.exists():
        raise FileExistsError("experimental run already exists; choose a new run name")
    output_path(target)
    target.mkdir(exist_ok=False)
    return target


def protected_hashes():
    """Hash the published resources, data and result phases; ignore the new phase."""
    paths = []
    for folder in ("reference/colemak-dh-resources", "data/kala", "data/baselines", "challenge",
                   "src/bangla_dh/colemak", "src/bangla_dh/geometry", "src/bangla_dh/scoring", "src/bangla_dh/search"):
        paths.extend(p for p in (PROJECT_ROOT / folder).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts)
    for folder in ("phase1", "phase2", "phase3", "phase3-crosscheck", "phase4", "mix-search", "kala-keyboards"):
        paths.extend(p for p in (PROJECT_ROOT / "results" / folder).rglob("*") if p.is_file())
    paths.extend((PROJECT_ROOT / "data").glob("*.json"))
    paths.append(PROJECT_ROOT / "results" / "reproduction.lock.json")
    return {p.relative_to(PROJECT_ROOT).as_posix(): sha256_file(p) for p in sorted(set(paths))}
