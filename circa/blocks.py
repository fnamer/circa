import ast
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Call:
    name: str
    filename: Path
    lineno: int
    offset: int


class Block(ast.NodeVisitor):
    def __init__(
        self, node: ast.AST, name: str, filename: Path, parent: Optional["Block"] = None
    ):
        self.node = node
        self._name = name
        self.filename = filename
        self.parent = parent
        self._names: dict[str, str] = {}
        self.calls: list[Call] = []
        self.generic_visit(self.node)

    @property
    def names(self) -> dict[str, str]:
        if self.parent is None:
            return self._names
        return self.parent.names | self._names

    @property
    def name(self) -> str:
        if self.parent is None:
            return self._name
        return f"{self.parent.name}.{self._name}"

    @property
    def lineno(self) -> int:
        lineno = getattr(self.node, "lineno", 1)
        return lineno

    @property
    def offset(self) -> int:
        col_offset = getattr(self.node, "col_offset", 0)
        # TODO: fix one-off bug?
        return col_offset

    def get(self, name: str) -> "Block":
        for child in ast.iter_child_nodes(self.node):
            if getattr(child, "name", None) == name:
                return Block(child, filename=self.filename, name=name, parent=self)
        raise Exception(f"BlockNotFound: '{name}'")

    def resolve_import(self, module: Optional[str], name: str, level: int) -> str:
        assert module is not None, "TODO: handle optional case"
        definition = f"{module}.{name}"
        parent = Path(self.filename).resolve().parent
        for _ in range(level):
            definition = f"{parent.stem}.{definition}"
            parent = parent.parent
        return definition

    def _is_firstparty_module(self, module: str) -> bool:
        if module in sys.stdlib_module_names:
            return False

        # very hacky check to differentiate between module and package
        block = self
        while block.parent is not None:
            block = block.parent
        return "." in block.name

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            name = alias.asname if alias.asname is not None else alias.name
            if self._is_firstparty_module(alias.name):
                self._names[name] = alias.name

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if not self._is_firstparty_module(node.module):
            return

        for alias in node.names:
            name = alias.asname if alias.asname is not None else alias.name
            definition = self.resolve_import(node.module, alias.name, node.level)
            self._names[name] = definition

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        # TODO: method calls and specifically __init__
        self._names[node.name] = f"{self.name}.{node.name}"

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._names[node.name] = f"{self.name}.{node.name}"

    def visit_Call(self, node: ast.Call) -> None:
        name = self.names.get(ast.unparse(node.func))
        if name is not None:
            call = Call(name, self.filename, node.lineno, node.col_offset)
            self.calls.append(call)
