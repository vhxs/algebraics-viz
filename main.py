import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np

from algebraics.graphics.circle import draw_circle, generate_circles
from algebraics.graphics.models import Circle
from algebraics.graphics.rendering import setup_gl
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

# def create_texture(sz):
#     tex = glGenTextures(1)
#     glBindTexture(GL_TEXTURE_2D, tex)
#     glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
#     glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
#     xs = sz
#     ys = sz
#     # Create coordinate grids with y running from top to bottom.
#     X, Y = np.meshgrid(np.arange(xs), np.arange(ys-1, -1, -1), indexing='xy')
#     center = sz / 2.0
#     # Compute f = ((sz/2)^2) / (1 + (x - center)^2 + (y - center)^2)
#     f = ((sz / 2.0) ** 2) / (1 + (X - center)**2 + (Y - center)**2)
#     # Clamp values to a maximum of 255.
#     f = np.minimum(255, f)
#     f = f.astype(np.uint8)
#     # Create an RGB image where each channel is f.
#     data = np.stack((f, f, f), axis=-1)
    
#     gluBuild2DMipmaps(GL_TEXTURE_2D, 3, xs, ys, GL_RGB, GL_UNSIGNED_BYTE, data)
#     return tex


def main():
    if not glfw.init():
        return
    
    window = glfw.create_window(1000, 1000, "OpenGL Circle", None, None)
    if not window:
        glfw.terminate()
        return
    
    glfw.make_context_current(window)
    setup_gl()
    
    polynomials = [polynomial for polynomial in enumerate_polynomials_sjbrooks(10)]
    root_sets = [find_roots(polynomial) for polynomial in polynomials]
    root_sets = [root_set for root_set in root_sets if root_set is not None]

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)
        for root_set in root_sets:
            for circle in generate_circles(root_set):
                draw_circle(circle)
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    glfw.terminate()

main()