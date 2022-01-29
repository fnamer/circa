from .results import Result


class Tracer:
    def __init__(self, program: str) -> None:
        self.program = program

    def run(self, entrypoint: str = None) -> Result:
        raise NotImplementedError()
