import ast
from dataclasses import dataclass
from dataclasses import field

from .blocks import Block
from .results import Call
from .results import Trace


@dataclass
class Frame:
    locals: dict[str, str] = field(default_factory=dict)
    globals: dict[str, str] = field(default_factory=dict)
    calls: list[Call] = field(default_factory=list)


class Tracer(ast.NodeVisitor):
    def __init__(self, block: Block) -> None:
        self.block = block

    def run(self) -> Trace:
        self.frame = Frame()
        return Trace(
            name=self.block.name,
            filename=self.block.filename,
            lineno=self.block.lineno,
            offset=self.block.offset,
            calls=self.frame.calls,
        )
