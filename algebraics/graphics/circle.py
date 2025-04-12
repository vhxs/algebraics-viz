from typing import Generator

from algebraics.graphics.models import Circle
from algebraics.polynomial.models import RootSet

COLORS = [
    [1.0, 0.0, 0.0],
    [0.0, 1.0, 0.0],
    [0.0, 0.0, 1.0],
    [0.7, 0.7, 0.0],
    [1.0, 0.6, 0.0],
    [0.0, 1.0, 1.0],
    [1.0, 0.0, 1.0],
    [0.6, 0.6, 0.6],
]

def generate_circles(root_set: RootSet) -> Generator[Circle]:
    for root in root_set.roots:
        circle = Circle(
            x_center=root.real,
            y_center=root.imag,
            radius=(0.5 ** (root_set.length + 1 + root_set.degree)),
        )
        yield circle