import argparse
from typing import Generator

from .blocks import Block
from .program import Program


def trace(entrypoint: str, program: str = ".") -> Generator[Block, None, None]:
    _program = Program(program)
    _entrypoint = (
        f"{entrypoint}.__main__"
        if (_program.path / entrypoint).is_dir()
        else entrypoint
    )
    return _program.trace(_entrypoint)


def report(block: Block) -> None:
    print(f"Block: {block.name} {block.filename}:{block.lineno}:{block.offset}")
    print("Calls:")
    for call in block.calls:
        print(f"    - {call.name} {call.filename}:{call.lineno}:{call.offset}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser("circa")
    parser.add_argument("entrypoint")
    parser.add_argument("program", nargs="?", default=".")

    args = parser.parse_args()

    for block in trace(args.entrypoint, args.program):
        report(block)
