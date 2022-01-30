import ast
import tokenize
from collections import deque
from pathlib import Path
from typing import Generator
from typing import Optional

from .blocks import Block


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
        return f"{self.path.stem}.__main__"

    def get_block(self, name: str) -> Block:
        block = self._blocks.get(name, self._load_block(name))
        self._blocks[name] = block
        return block

    def _load_block(self, name: str) -> Block:
        definitions, filename = self._find_block(name)

        with tokenize.open(filename) as fp:
            node = ast.parse(fp.read())

        bname = (
            f"{self.path.stem}.{filename.stem}"
            if self.path.is_dir()
            else self.path.stem
        )
        block = Block(node, bname, filename)

        for definition in definitions:
            block = block.get(definition)

        return block

    def _find_block(self, name: str) -> tuple[list[str], Path]:
        if self.path.is_file():
            definition = name.replace(f"{self.path.stem}", "").strip(".")
            return [definition] if definition else [], self.path

        parts = name.split(".")[1:]
        definitions: list[str] = []

        for _ in range(len(parts)):
            path = "/".join(parts)
            file = (self.path / path).with_suffix(".py")

            if file.exists():
                return definitions, file

            definitions.insert(0, parts.pop())

        raise Exception(f"BlockNotFound: '{name}'")

    def trace(self, entrypoint: Optional[str] = None) -> Generator[Block, None, None]:
        _entrypoint = entrypoint if entrypoint is not None else self.main
        names = deque([_entrypoint])
        while names:
            name = names.popleft()
            block = self.get_block(name)

            yield block

            for call in block.calls:
                names.append(call.name)
