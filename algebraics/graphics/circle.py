import math
from typing import Generator

from OpenGL.GL import GL_TRIANGLE_FAN, glBegin, glColor3f, glEnd, glFlush, glVertex2f

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
    color = COLORS[root_set.degree-1] if root_set.degree < 8 else (1.0, 1.0, 1.0)
    for root in root_set.roots:
        circle = Circle(
            x_center=root.real,
            y_center=root.imag,
            radius=(0.5 ** (root_set.length + 1 + root_set.degree)),
            red=color[0],
            green=color[1],
            blue=color[2]
        )
        yield circle