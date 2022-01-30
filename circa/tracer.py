from collections import deque
from pathlib import Path
from typing import Generator

from .blocks import Block
from .results import Call
from .results import Trace


class Tracer:
    def __init__(self, program: str) -> None:
        self.program = program
        self.path = Path(program)
        self._blocks: dict[str, Block] = {}

    def get_block(self, name: str) -> Block:
        block = self._blocks.get(name, self._load_block(name))
        self._blocks[name] = block
        return block

    def _load_block(self, name: str) -> Block:
        definitions, filename = self._find_block(name)
        block = Block.read(filename)
        for definition in definitions:
            block = block.get(definition)
        return block

    def _find_block(self, name: str) -> tuple[list[str], Path]:
        if self.path.is_file():
            return (
                name.removeprefix(self.path.stem).split(".")
                if name != "__main__"
                else [],
                self.path,
            )

        parts = name.split(".")
        definitions: list[str] = []

        for _ in range(len(parts)):
            path = "/".join(parts)
            file = (self.path / path).with_suffix(".py")

            if file.exists():
                return definitions, file

            definitions.insert(0, parts.pop())

        raise Exception(f"BlockNotFound: '{name}'")

    def trace_block(self, block: Block) -> Trace:
        calls: list[Call] = []
        return Trace(
            name=block.name,
            filename=block.filename,
            lineno=block.lineno,
            offset=block.offset,
            calls=calls,
        )

    def run(self, entrypoint: str = "__main__") -> Generator[Trace, None, None]:
        names = deque([entrypoint])
        while names:
            name = names.popleft()
            block = self.get_block(name)
            trace = self.trace_block(block)

            yield trace

            for call in trace.calls:
                names.append(call.name)
