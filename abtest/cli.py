"""Command line entry point: `python3 -m abtest assign|srm`."""

import argparse
import json
import sys
from pathlib import Path

from abtest.bucket import Experiment, assign
from abtest.srm import DEFAULT_ALPHA, check_srm

EXIT_MISMATCH = 1
EXIT_USAGE = 2


def load_experiment(path: str) -> Experiment:
    try:
        raw = json.loads(Path(path).read_text())
        return Experiment(raw["name"], raw["variants"])
    except OSError as error:
        raise ValueError(f"cannot read config {path!r}: {error.strerror}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"config {path!r} is not valid JSON: {error}") from error
    except KeyError as error:
        raise ValueError(f"config {path!r} is missing key {error}") from error


def parse_counts(pairs: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for pair in pairs:
        variant, separator, number = pair.partition("=")
        if not separator or not number.isdigit():
            raise ValueError(f"expected variant=count, got {pair!r}")
        counts[variant] = int(number)
    return counts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="abtest")
    commands = parser.add_subparsers(dest="command", required=True)
    assign_cmd = commands.add_parser("assign", help="print the variant for each user id")
    assign_cmd.add_argument("--config", required=True)
    assign_cmd.add_argument("users", nargs="+")
    srm_cmd = commands.add_parser("srm", help="check observed counts against the weights")
    srm_cmd.add_argument("--config", required=True)
    srm_cmd.add_argument("--counts", nargs="+", required=True, metavar="VARIANT=COUNT")
    srm_cmd.add_argument("--alpha", type=float, default=DEFAULT_ALPHA)
    return parser


def run(argv: list[str]) -> int:
    args = build_parser().parse_args(argv)
    try:
        experiment = load_experiment(args.config)
        if args.command == "assign":
            for user in args.users:
                print(f"{user}\t{assign(experiment, user)}")
            return 0
        result = check_srm(parse_counts(args.counts), experiment.weights, args.alpha)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return EXIT_USAGE
    verdict = "MISMATCH" if result.mismatch else "ok"
    print(
        f"chi2={result.chi_square:.3f} df={result.degrees_of_freedom} "
        f"p={result.p_value:.4g} alpha={args.alpha} {verdict}"
    )
    return EXIT_MISMATCH if result.mismatch else 0
