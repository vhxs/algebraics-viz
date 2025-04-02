import itertools
from typing import Generator

def enumerate_partitions(n: int, length: int) -> Generator[list[int]]:
    def enumerate_partitions_recursive(n, current_partition) -> Generator[list[int]]:
        if len(current_partition) == length:
            if n == 0:
                yield list(current_partition)
            return
        for i in range(1, n + 1):
            current_partition.append(i)
            yield from enumerate_partitions_recursive(n - i, current_partition)
            current_partition.pop()

    yield from enumerate_partitions_recursive(n, [])

def generate_signs(partition: list[int]) -> Generator[list[int]]:
    signs = []
    for number in partition:
        if number > 0:
            signs.append([number, -number])
        else:
            signs.append([number])

    yield from itertools.product(*signs)

if __name__ == "__main__":
    for p in enumerate_partitions(4 + 3, 3):
        print(p)