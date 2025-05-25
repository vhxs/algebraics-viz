from typing import Generator

from OpenGL.GL import glColor3f, glTexCoord2f, glVertex2f

from algebraics.polynomial.models import RootSet
from algebraics.ui.models import Circle


def generate_circles(root_set: RootSet) -> Generator[Circle]:
    for root in root_set.roots:
        circle = Circle(
            x_center=root.real,
            y_center=root.imag,
            radius=(0.5 ** (root_set.length + 1 + root_set.degree)),
        )
        yield circle


def draw_circle(circle: Circle, radius_scale=10.0):
    glColor3f(circle.red, circle.green, circle.blue)
    glTexCoord2f(0, 0)
    glVertex2f(circle.x_center - circle.radius*radius_scale, circle.y_center - circle.radius*radius_scale)
    glTexCoord2f(1, 0)
    glVertex2f(circle.x_center + circle.radius*radius_scale, circle.y_center - circle.radius*radius_scale)
    glTexCoord2f(1, 1)
    glVertex2f(circle.x_center + circle.radius*radius_scale, circle.y_center + circle.radius*radius_scale)
    glTexCoord2f(0, 1)
    glVertex2f(circle.x_center - circle.radius*radius_scale, circle.y_center + circle.radius*radius_scale)