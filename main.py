import glfw
from OpenGL.GL import GL_COLOR_BUFFER_BIT, glClear

from algebraics.graphics.models import Circle
from algebraics.graphics.rendering import draw_circle, setup_gl
from algebraics.polynomial.polynomial import (
    enumerate_polynomials,
    enumerate_polynomials_sjbrooks,
    find_roots,
)

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


def main():
    if not glfw.init():
        return
    
    window = glfw.create_window(1000, 1000, "OpenGL Circle", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    setup_gl()
    
    polynomials = [polynomial for polynomial in enumerate_polynomials(6, 6)]
    root_sets = [find_roots(polynomial) for polynomial in polynomials]

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)
        for root_set in root_sets:
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
                draw_circle(circle)
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    glfw.terminate()

main()