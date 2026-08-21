"""Command-line interface for Conductor."""

import argparse

from conductor import __version__


def build_parser() -> argparse.ArgumentParser:
    """Build the Conductor argument parser."""
    parser = argparse.ArgumentParser(
        prog="conductor",
        description="Workflow orchestrator for software-development repositories.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main() -> int:
    """Run the command-line interface."""
    build_parser().parse_args()
    return 0
