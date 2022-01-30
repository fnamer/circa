import ast
import tokenize
from pathlib import Path


class Block:
    def __init__(
        self, node: ast.AST, filename: str = "<module>", name: str = "__main__"
    ):
        self.node = node
        self.filename = filename
        self.name = name

    @classmethod
    def read(self, filename: str | Path) -> "Block":
        with tokenize.open(filename) as fp:
            node = ast.parse(fp.read())
            return Block(node, filename=str(filename), name=Path(filename).stem)

    @property
    def lineno(self) -> int:
        lineno = getattr(self.node, "lineno", 1)
        return lineno

    @property
    def offset(self) -> int:
        col_offset = getattr(self.node, "col_offset", 0)
        return col_offset

    def get(self, name: str) -> "Block":
        for child in ast.iter_child_nodes(self.node):
            if getattr(child, "name", None) == name:
                return Block(child, filename=self.filename, name=name)
        raise Exception(f"BlockNotFound: '{name}'")
