from dataclasses import dataclass


def locate(filename: str, lineno: int, offset: int) -> str:
    return f"{filename}:{lineno}:{offset}"


@dataclass
class Call:
    name: str
    filename: str
    lineno: int
    offset: int

    def __str__(self) -> str:
        location = locate(self.filename, self.lineno, self.offset)
        return f"{self.name} {location}"


@dataclass
class Trace:
    name: str
    filename: str
    lineno: int
    offset: int
    calls: list[Call]

    def __str__(self) -> str:
        location = locate(self.filename, self.lineno, self.offset)
        calls = "\n".join(str(call) for call in self.calls) if len(self.calls) else "-"
        return f"Block: {location}\nCalls:\n    {calls}"
