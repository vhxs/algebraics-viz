
from OpenGL.GL import (
    GL_PROJECTION,
    glClearColor,
    glLoadIdentity,
    glMatrixMode,
    glOrtho,
)


def setup_gl():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)
