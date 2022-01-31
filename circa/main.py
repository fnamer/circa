from typing import Generator

import click

from .blocks import Block
from .blocks import Call
from .program import Program


def trace(entrypoint: str, program: str = ".") -> Generator[Block, None, None]:
    _program = Program(program)
    _entrypoint = (
        f"{entrypoint}.__main__"
        if (_program.path / entrypoint).is_dir()
        else entrypoint
    )
    return _program.trace(_entrypoint)


def _style_call(call: Call) -> str:
    name = click.style(call.name, fg="green")
    location = f"{call.filename}:{call.lineno}:{call.offset}"
    return f"{name} {location}"


def _locate(obj: Call | Block) -> str:
    return f"{obj.filename}:{obj.lineno}:{obj.offset}"


def report(blocks: Generator[Block, None, None]) -> Generator[str, None, None]:
    for block in blocks:
        yield f"{click.style(block.name, fg='yellow')} {_locate(block)}\n"
        for call in block.calls:
            yield f" {click.style(call.name, fg='green')} {_locate(call)}\n"
        yield "\n"


@click.command("circa")
@click.argument("entrypoint")
@click.argument("program", default=".")
def main(entrypoint: str, program: str) -> None:
    blocks = trace(entrypoint, program)
    click.echo_via_pager(report(blocks))
