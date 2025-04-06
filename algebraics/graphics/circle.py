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


def draw_circle(circle: Circle):
    glColor3f(circle.red, circle.green, circle.blue)
    glBegin(GL_TRIANGLE_FAN)
    num_segments = 100
    glVertex2f(circle.x_center, circle.y_center)
    for i in range(num_segments + 1):
        angle = 2.0 * math.pi * i / num_segments
        x = circle.x_center + circle.radius * math.cos(angle)
        y = circle.y_center + circle.radius * math.sin(angle)
        glVertex2f(x, y)
    glEnd()
    glFlush()

def generate_circles(root_set: RootSet) -> Generator[Circle]:
    color = COLORS[root_set.degree] if root_set.degree < 8 else (1.0, 1.0, 1.0)
    for root in root_set.roots:
        circle = Circle(
            x_center=root.real,
            y_center=root.imag,
            radius=(0.5 ** (root_set.length)),
            red=color[0],
            green=color[1],
            blue=color[2]
        )
        yield circle