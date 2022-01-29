import argparse

from .tracer import Tracer


def trace(program: str, entrypoint: str = "__main__"):
    tracer = Tracer(program)
    return tracer.run(entrypoint)


def main() -> None:
    parser = argparse.ArgumentParser("circa")
    parser.add_argument("program")
    parser.add_argument("entrypoint", nargs="?", default="__main__")

    args = parser.parse_args()

    result = trace(args.program, args.entrypoint)
    print(result)
