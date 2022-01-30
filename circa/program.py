from collections import deque
from pathlib import Path
from typing import Generator
from typing import Optional

from .blocks import Block
from .results import Trace
from .tracer import Tracer


class Program:
    def __init__(self, location: str) -> None:
        self.path = Path(location)
        if not self.path.exists():
            raise Exception(f"ProgramNotFound: '{location}'")
        self._blocks: dict[str, Block] = {}

    @property
    def main(self) -> str:
        if self.path.is_file():
            return self.path.stem
        return "__main__"

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
            definition = name.removeprefix(self.path.stem)
            return [definition] if definition else [], self.path

        parts = name.split(".")
        definitions: list[str] = []

        for _ in range(len(parts)):
            path = "/".join(parts)
            file = (self.path / path).with_suffix(".py")

            if file.exists():
                return definitions, file

            definitions.insert(0, parts.pop())

        raise Exception(f"BlockNotFound: '{name}'")

    def trace(self, entrypoint: Optional[str] = None) -> Generator[Trace, None, None]:
        _entrypoint = entrypoint if entrypoint is not None else self.main
        names = deque([_entrypoint])
        while names:
            name = names.popleft()
            block = self.get_block(name)
            tracer = Tracer(block)
            trace = tracer.run()

            yield trace

            for call in trace.calls:
                names.append(call.name)
