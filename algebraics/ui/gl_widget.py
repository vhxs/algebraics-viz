from collections import defaultdict

import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt6.QtOpenGLWidgets import QOpenGLWidget

from algebraics.polynomial.models import RootSet
from algebraics.polynomial.polynomial import enumerate_polynomials, find_roots
from algebraics.ui.circle import draw_circle, generate_circles


class GLWidget(QOpenGLWidget):
    COLORS = {
        1: [1.0, 0.0, 0.0],
        2: [0.0, 1.0, 0.0],
        3: [0.0, 0.0, 1.0],
        4: [0.7, 0.7, 0.0],
        5: [1.0, 0.6, 0.0],
        6: [0.0, 1.0, 1.0],
        7: [1.0, 0.0, 1.0],
        8: [0.6, 0.6, 0.6],
    }

    DEFAULT_COLOR = [1.0, 1.0, 1.0]

    def __init__(self):
        super().__init__()
        self.zoom = 1.0
        self.radius_scale = 10.0
        self.texture = None

        self.max_degree = 5
        self.max_length = 5

        self.generate_circles_by_degree(self.max_length, self.max_degree)
        self.default_color = GLWidget.DEFAULT_COLOR.copy()

        self.translate_x = 0.0
        self.translate_y = 0.0

    def generate_circles_by_degree(self, max_length: int, max_degree: int):
        polynomials = [
            polynomial for polynomial in enumerate_polynomials(max_length, max_degree)
        ]
        root_sets: list[RootSet] = []
        for polynomial in polynomials:
            root_set = find_roots(polynomial)
            if root_set:
                root_sets.append(root_set)

        self.circles_by_degree = defaultdict(list)
        for root_set in root_sets:
            for circle in generate_circles(root_set):
                self.circles_by_degree[root_set.degree].append(circle)

        self.colors_by_degree = {
            k: v for k, v in GLWidget.COLORS.copy().items() if k <= max_degree
        }

        self.max_degree = max_degree
        self.max_length = max_length

    def create_texture(self, texture_size: int) -> int:
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        width = texture_size
        height = texture_size

        x_coords, y_coords = np.meshgrid(
            np.arange(width), np.arange(height - 1, -1, -1), indexing="xy"
        )

        texture_center = texture_size / 2.0

        intensity = ((texture_size / 2.0) ** 2) / (
            1 + (x_coords - texture_center) ** 2 + (y_coords - texture_center) ** 2
        )
        intensity = np.minimum(255, intensity).astype(np.uint8)

        texture_data = np.stack((intensity, intensity, intensity), axis=-1)

        gluBuild2DMipmaps(
            GL_TEXTURE_2D, 3, width, height, GL_RGB, GL_UNSIGNED_BYTE, texture_data
        )
        return texture_id

    def initializeGL(self):
        glEnable(GL_TEXTURE_2D)
        glClearColor(0, 0, 0, 1.0)
        self.texture = self.create_texture(256)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(self.translate_x, self.translate_y, 0)
        glScalef(self.zoom, self.zoom, 1.0)

        glEnable(GL_BLEND)
        glBlendFunc(GL_ONE, GL_ONE)
        glDisable(GL_DEPTH_TEST)
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, self.texture)

        glBegin(GL_QUADS)
        for degree in self.circles_by_degree.keys():
            for circle in self.circles_by_degree[degree]:
                if degree in self.colors_by_degree:
                    circle.set_color(self.colors_by_degree[degree])
                else:
                    circle.set_color(self.default_color)
                draw_circle(circle, self.radius_scale)
        glEnd()

    def zoom_in(self):
        self.zoom *= 1.1
        self.update()

    def zoom_out(self):
        self.zoom /= 1.1
        self.update()

    def move_left(self):
        self.translate_x -= 0.1
        self.update()

    def move_right(self):
        self.translate_x += 0.1
        self.update()

    def move_up(self):
        self.translate_y += 0.1
        self.update()

    def move_down(self):
        self.translate_y -= 0.1
        self.update()

    def update_radius_scale(self, radius_scale: float):
        self.radius_scale = radius_scale
        self.update()
