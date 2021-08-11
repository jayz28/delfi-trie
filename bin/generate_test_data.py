#!/usr/bin/env python3
import sys
import random


def main(args) -> None:
    read_length: int = int(args[0])
    num_reads: int = int(args[1])

    bases: [str] = ["A", "T", "C", "G", "N"]

    for _ in range(num_reads):
        read: str = "".join(random.choices(bases, k=read_length))
        print(read)


if __name__ == "__main__":
    main(sys.argv[1:])
