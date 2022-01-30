import argparse
from typing import Generator
from typing import Optional

from .program import Program
from .results import Trace


def trace(
    program: str, entrypoint: Optional[str] = None
) -> Generator[Trace, None, None]:
    _program = Program(program)
    return _program.trace(entrypoint)


def main() -> None:
    parser = argparse.ArgumentParser("circa")
    parser.add_argument("program")
    parser.add_argument("entrypoint", nargs="?")

    args = parser.parse_args()

    for result in trace(args.program, args.entrypoint):
        print(result)
