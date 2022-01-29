from pathlib import Path

from .blocks import Block
from .results import Result


class Tracer:
    def __init__(self, program: str) -> None:
        self.program = program
        self.path = Path(program).resolve()
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
            module = self.path.stem
            definitions = (
                name.removeprefix(module).split(".") if name != "__main__" else []
            )
            return definitions, self.path

        parts = name.split(".")
        definitions: list[str] = []

        for _ in range(len(parts)):
            path = "/".join(parts)
            file = (self.path / path).with_suffix(".py")

            if file.exists():
                return definitions, file

            definitions.insert(0, parts.pop())

        raise Exception(f"NoSuchBlock: '{name}'")

    def run(self, entrypoint: str = "__main__") -> Result:
        block = self.get_block(entrypoint)
        return NotImplementedError()
