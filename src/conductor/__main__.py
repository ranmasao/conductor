"""Allow Conductor to run with ``python -m conductor``."""

from .cli import main

if __name__ == "__main__":
    raise SystemExit(main())
