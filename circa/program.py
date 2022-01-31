import ast
import tokenize
from collections import deque
from pathlib import Path
from typing import Generator

from .blocks import Block


class Program:
    def __init__(self, root: str) -> None:
        self.path = Path(root).resolve()
        if not self.path.exists():
            raise Exception(f"ProgramNotFound: '{root}'")
        self._blocks: dict[str, Block] = {}

    def get_block(self, name: str) -> Block:
        block = self._blocks.get(name, self._load_block(name))
        self._blocks[name] = block
        return block

    def _load_block(self, name: str) -> Block:
        blockname, definitions, filename = self._find_block(name)

        with tokenize.open(filename) as fp:
            node = ast.parse(fp.read())

        block = Block(node, blockname, filename.relative_to(self.path))

        for definition in definitions:
            block = block.get(definition)

        return block

    def _find_block(self, name: str) -> tuple[str, list[str], Path]:
        parts = name.split(".")
        definitions: list[str] = []

        for _ in range(len(parts)):
            path = "/".join(parts)
            file = (self.path / path).with_suffix(".py")

            if file.is_file():
                return ".".join(parts), definitions, file

            part = parts.pop()
            definitions.insert(0, part)

        # maybe package.__init__
        init = self.path / part / "__init__.py"
        if init.exists():
            return f"{part}.__init__", definitions[1:], init

        raise Exception(f"BlockNotFound: '{name}'")

    def trace(self, entrypoint: str) -> Generator[Block, None, None]:
        names = deque([entrypoint])
        while names:
            name = names.popleft()
            block = self.get_block(name)

            yield block

            for call in block.calls:
                names.append(call.name)
