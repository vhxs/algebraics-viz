from typing import Generator

from OpenGL.GL import glColor3f, glTexCoord2f, glVertex2f

from algebraics.ui.models import Circle
from algebraics.polynomial.models import RootSet

def generate_circles(root_set: RootSet) -> Generator[Circle]:
    for root in root_set.roots:
        circle = Circle(
            x_center=root.real,
            y_center=root.imag,
            radius=(0.5 ** (root_set.length + 1 + root_set.degree)),
        )
        yield circle


# Provided draw_circle function that renders one quad using texture coordinates.
def draw_circle(circle: Circle):
    glColor3f(circle.red, circle.green, circle.blue)
    glTexCoord2f(0, 0)
    glVertex2f(circle.x_center - circle.radius*10, circle.y_center - circle.radius*10)
    glTexCoord2f(1, 0)
    glVertex2f(circle.x_center + circle.radius*10, circle.y_center - circle.radius*10)
    glTexCoord2f(1, 1)
    glVertex2f(circle.x_center + circle.radius*10, circle.y_center + circle.radius*10)
    glTexCoord2f(0, 1)
    glVertex2f(circle.x_center - circle.radius*10, circle.y_center + circle.radius*10)