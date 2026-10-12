"""Run separately: python -m bangla_dh.experimental candidates --out ..."""
import argparse
from pathlib import Path
import sys

from ..paths import PROJECT_ROOT
from .evaluate import run
from .inputs import HELDOUT


def main(argv=None):
    parser = argparse.ArgumentParser(description="Isolated season e1: reference scores and partial preference diagnostics; no search.")
    parser.add_argument("command", choices=("audit", "evaluate", "candidates"),
                        help="audit source only; evaluate published maps; candidates includes retained run maps")
    parser.add_argument("--out", type=Path, default=PROJECT_ROOT / "results/evaluator-e1/run-v1",
                        help="new run directory under results/evaluator-e1 or work/evaluator-experiments")
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--corpora", nargs="+", choices=HELDOUT, default=list(HELDOUT))
    parser.add_argument("--no-baselines", action="store_true",
                        help="style maps only; useful without rebuilt corpus token tables")
    args = parser.parse_args(argv)
    try:
        run(args.command, args.out, args.workers, tuple(args.corpora), not args.no_baselines)
    except (ValueError, FileExistsError, FileNotFoundError) as error:
        print(f"Evaluation failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
