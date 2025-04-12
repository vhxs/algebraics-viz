from collections import defaultdict
import sys
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QPushButton, QColorDialog
)
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *

from algebraics.graphics.circle import generate_circles
from algebraics.graphics.models import Circle
from algebraics.polynomial.models import RootSet
from algebraics.polynomial.polynomial import enumerate_polynomials, find_roots

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

# Provided draw_circle function that renders one quad using texture coordinates.
def draw_circle(circle: Circle):
    # Set the color based on the circle's RGB values.
    glColor3f(circle.red, circle.green, circle.blue)
    glTexCoord2f(0, 0)
    glVertex2f(circle.x_center - circle.radius*10, circle.y_center - circle.radius*10)
    glTexCoord2f(1, 0)
    glVertex2f(circle.x_center + circle.radius*10, circle.y_center - circle.radius*10)
    glTexCoord2f(1, 1)
    glVertex2f(circle.x_center + circle.radius*10, circle.y_center + circle.radius*10)
    glTexCoord2f(0, 1)
    glVertex2f(circle.x_center - circle.radius*10, circle.y_center + circle.radius*10)

def create_texture(texture_size):

    texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    width = texture_size
    height = texture_size

    x_coords, y_coords = np.meshgrid(
        np.arange(width), 
        np.arange(height - 1, -1, -1), 
        indexing='xy'
    )

    texture_center = texture_size / 2.0

    intensity = ((texture_size / 2.0) ** 2) / (1 + (x_coords - texture_center)**2 + (y_coords - texture_center)**2)
    intensity = np.minimum(255, intensity).astype(np.uint8)

    texture_data = np.stack((intensity, intensity, intensity), axis=-1)

    gluBuild2DMipmaps(GL_TEXTURE_2D, 3, width, height, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
    return texture_id


class GLWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.zoom = 1.0
        self.texture = None

        # List of Circle objects.
        polynomials = [polynomial for polynomial in enumerate_polynomials(6, 6)]
        root_sets = [find_roots(polynomial) for polynomial in polynomials]
        root_sets = [root_set for root_set in root_sets if root_set is not None]
        self.circles_by_degree = self.generate_circles_by_degree(root_sets)
        self.colors_by_degree = COLORS.copy()
        self.default_color = DEFAULT_COLOR.copy()
        
        # Translation offsets.
        self.translate_x = 0.0
        self.translate_y = 0.0

    def generate_circles_by_degree(self, root_sets: list[RootSet]) -> dict[int, list[Circle]]:
        circles = defaultdict(list)
        for root_set in root_sets:
            for circle in generate_circles(root_set):
                circles[root_set.degree].append(circle)

        return circles

    def initializeGL(self):
        glEnable(GL_TEXTURE_2D)
        glClearColor(0, 0, 0, 1.0)
        self.texture = create_texture(256)

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
                draw_circle(circle)
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

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Algebraic numbers")
        main_layout = QHBoxLayout()
        
        # Create the GL widget.
        self.gl_widget = GLWidget()
        
        # Left control panel.
        control_layout = QVBoxLayout()
        self.color_layout = QVBoxLayout()
        self.color_buttons: dict[int | str, QPushButton] = {}
        self.degree = len(self.gl_widget.colors_by_degree)
        
        # Add initial color buttons.
        self.populate_color_buttons()
        
        # Layout for the +/- buttons.
        modify_layout = QHBoxLayout()
        self.minus_btn = QPushButton("-")
        self.minus_btn.clicked.connect(self.remove_color_button)
        self.plus_btn = QPushButton("+")
        self.plus_btn.clicked.connect(self.add_new_color_button)
        modify_layout.addWidget(self.minus_btn)
        modify_layout.addWidget(self.plus_btn)
        
        control_layout.addLayout(self.color_layout)
        control_layout.addLayout(modify_layout)
        
        # Zoom controls.
        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.clicked.connect(self.zoom_in)
        control_layout.addWidget(zoom_in_btn)
        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom_out)
        control_layout.addWidget(zoom_out_btn)
        
        # Translation buttons arranged in a grid.
        translate_layout = QGridLayout()
        up_btn = QPushButton("Up")
        up_btn.clicked.connect(self.move_up)
        left_btn = QPushButton("Left")
        left_btn.clicked.connect(self.move_left)
        right_btn = QPushButton("Right")
        right_btn.clicked.connect(self.move_right)
        down_btn = QPushButton("Down")
        down_btn.clicked.connect(self.move_down)
        translate_layout.addWidget(up_btn, 0, 1)
        translate_layout.addWidget(left_btn, 1, 0)
        translate_layout.addWidget(right_btn, 1, 2)
        translate_layout.addWidget(down_btn, 2, 1)
        control_layout.addLayout(translate_layout)
        
        control_layout.addStretch(1)
        control_widget = QWidget()
        control_widget.setLayout(control_layout)
        
        main_layout.addWidget(control_widget)
        main_layout.addWidget(self.gl_widget, stretch=1)
        self.setLayout(main_layout)

    def populate_color_buttons(self):
        btn = QPushButton(f"Default")
        color = self.gl_widget.default_color
        btn.setStyleSheet(f"background-color: rgb({color[0]*255},{color[1]*255},{color[2]*255});")
        btn.clicked.connect(lambda _, idx="default": self.pick_color(idx))
        self.color_buttons["default"] = btn
        self.color_layout.addWidget(btn)

        for degree, color in self.gl_widget.colors_by_degree.items():
            btn = QPushButton(f"Degree {degree}")
            btn.setStyleSheet(f"background-color: rgb({color[0]*255},{color[1]*255},{color[2]*255});")
            btn.clicked.connect(lambda _, idx=degree: self.pick_color(idx))
            self.color_buttons[degree] = btn
            self.color_layout.addWidget(btn)

    def add_new_color_button(self):
        self.degree += 1

        btn = QPushButton(f"Degree {self.degree}")
        btn.setStyleSheet("background-color: rgb(255,255,255);")
        btn.clicked.connect(lambda _, idx=self.degree: self.pick_color(idx))
        self.color_buttons[self.degree] = btn
        self.color_layout.addWidget(btn)
        self.gl_widget.update()

    def remove_color_button(self):
        if self.degree > 0:
            btn = self.color_buttons.pop(self.degree)
            btn.setParent(None)

            self.gl_widget.colors_by_degree.pop(self.degree)
            self.degree -= 1
            self.gl_widget.update()

    def pick_color(self, degree: int | str):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_buttons[degree].setStyleSheet(
                    f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});"
                )
            if isinstance(degree, int):
                self.gl_widget.colors_by_degree[degree] = [color.red() / 255., color.green() / 255., color.blue() / 255.]
            else:
                self.gl_widget.default_color = [color.red() / 255., color.green() / 255., color.blue() / 255.]
            self.gl_widget.update()

    def zoom_in(self):
        self.gl_widget.zoom_in()

    def zoom_out(self):
        self.gl_widget.zoom_out()

    def move_left(self):
        self.gl_widget.move_left()

    def move_right(self):
        self.gl_widget.move_right()

    def move_up(self):
        self.gl_widget.move_up()

    def move_down(self):
        self.gl_widget.move_down()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1200, 1000)
    window.show()
    sys.exit(app.exec())
