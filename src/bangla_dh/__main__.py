from .cli import main

# Guarded: multiprocessing workers (spawned on Windows) re-import this module.
if __name__ == "__main__":
    raise SystemExit(main())
