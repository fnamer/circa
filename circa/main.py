import argparse
from typing import Generator
from typing import Optional

from .blocks import Block
from .program import Program


def trace(
    program: str, entrypoint: Optional[str] = None
) -> Generator[Block, None, None]:
    _program = Program(program)
    return _program.trace(entrypoint)


def report(block: Block) -> None:
    print(f"Block: {block.name} {block.filename}:{block.lineno}:{block.offset}")
    print("Calls:")
    for call in block.calls:
        print(f"    - {call.name} {call.filename}:{call.lineno}:{call.offset}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser("circa")
    parser.add_argument("program")
    parser.add_argument("entrypoint", nargs="?")

    args = parser.parse_args()

    for block in trace(args.program, args.entrypoint):
        report(block)
