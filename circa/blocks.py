import ast
import tokenize
from pathlib import Path
from typing import Optional


class Block:
    def __init__(
        self, node: ast.AST, filename: Optional[str] = None, name: str = "__main__"
    ):
        self.node = node
        self.filename = filename
        self.name = name

    @classmethod
    def read(self, filename: str | Path) -> "Block":
        with tokenize.open(filename) as fp:
            node = ast.parse(fp.read())
            return Block(node, filename=str(filename), name=Path(filename).stem)

    def get(self, name: str) -> "Block":
        for child in ast.iter_child_nodes(self.node):
            if getattr(child, "name", None) == name:
                return Block(child, filename=self.filename, name=name)
        raise Exception(f"BlockNotFound: '{name}'")
