import sys
import math
import numpy as np
from PyQt6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QPushButton, QColorDialog
)
from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from OpenGL.GL import *
from OpenGL.GLU import *

def create_texture(sz):
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    xs = sz
    ys = sz
    X, Y = np.meshgrid(np.arange(xs), np.arange(ys-1, -1, -1), indexing='xy')
    center = sz / 2.0
    f = ((sz / 2.0) ** 2) / (1 + (X - center)**2 + (Y - center)**2)
    f = np.minimum(255, f).astype(np.uint8)
    data = np.stack((f, f, f), axis=-1)
    
    gluBuild2DMipmaps(GL_TEXTURE_2D, 3, xs, ys, GL_RGB, GL_UNSIGNED_BYTE, data)
    return tex

class GLWidget(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.zoom = 1.0
        self.texture = None
        # Start with an empty list of colors; the MainWindow will add one immediately.
        self.colors = []  
        # Translation offsets.
        self.tx = 0.0
        self.ty = 0.0

    def initializeGL(self):
        glEnable(GL_TEXTURE_2D)
        glClearColor(0, 0, 0, 1.0)
        self.texture = create_texture(256)

    def draw_textured_circle(self, cx, cy, radius, color, segments=50):
        # Convert color from 0-255 to normalized values.
        r, g, b = [c / 255.0 for c in color]
        glColor3f(r, g, b)
        glBegin(GL_TRIANGLE_FAN)
        # Center of the circle uses the center of the texture.
        glTexCoord2f(0.5, 0.5)
        glVertex2f(cx, cy)
        for i in range(segments + 1):
            angle = 2 * math.pi * i / segments
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            # Map texture coordinates in a circular fashion.
            tx = 0.5 + 0.5 * math.cos(angle)
            ty = 0.5 + 0.5 * math.sin(angle)
            glTexCoord2f(tx, ty)
            glVertex2f(x, y)
        glEnd()

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        # Apply translation offsets.
        glTranslatef(self.tx, self.ty, 0)
        scale = self.zoom
        glBindTexture(GL_TEXTURE_2D, self.texture)
        
        n = len(self.colors)
        if n > 0:
            # Divide the horizontal range (-scale to scale) evenly among the circles.
            width_per_circle = (2 * scale) / n
            for i, color in enumerate(self.colors):
                # Compute center for each circle.
                cx = -scale + (i + 0.5) * width_per_circle
                # Use 40% of the width_per_circle as the circle's radius.
                radius = width_per_circle * 0.4
                self.draw_textured_circle(cx, 0.0, radius, color)

    def zoom_in(self):
        self.zoom *= 1.1
        self.update()

    def zoom_out(self):
        self.zoom /= 1.1
        self.update()

    # Translation methods.
    def move_left(self):
        self.tx -= 0.1
        self.update()

    def move_right(self):
        self.tx += 0.1
        self.update()

    def move_up(self):
        self.ty += 0.1
        self.update()

    def move_down(self):
        self.ty -= 0.1
        self.update()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dynamic Colors and Translation")
        main_layout = QHBoxLayout()
        
        # Create GL widget.
        self.gl_widget = GLWidget()
        
        # Left side: Control panel.
        control_layout = QVBoxLayout()
        self.color_layout = QVBoxLayout()
        self.color_buttons = []  # Store references to color buttons.
        
        # Add the initial color button.
        self.add_color_button()
        
        # Layout for the + and – buttons.
        modify_layout = QHBoxLayout()
        self.minus_btn = QPushButton("-")
        self.minus_btn.clicked.connect(self.remove_color_button)
        self.plus_btn = QPushButton("+")
        self.plus_btn.clicked.connect(self.add_color_button)
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

    def add_color_button(self):
        index = len(self.color_buttons)
        # Append a default white color.
        self.gl_widget.colors.append((255, 255, 255))
        btn = QPushButton(f"Color {index + 1}")
        btn.setStyleSheet("background-color: rgb(255, 255, 255);")
        btn.clicked.connect(lambda _, idx=index: self.pick_color(idx))
        self.color_buttons.append(btn)
        self.color_layout.addWidget(btn)
        self.gl_widget.update()

    def remove_color_button(self):
        if len(self.color_buttons) > 1:
            btn = self.color_buttons.pop()
            btn.setParent(None)
            self.gl_widget.colors.pop()
            self.gl_widget.update()

    def pick_color(self, idx):
        color = QColorDialog.getColor()
        if color.isValid():
            self.gl_widget.colors[idx] = (color.red(), color.green(), color.blue())
            self.color_buttons[idx].setStyleSheet(
                f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});"
            )
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
    try:
        app = QApplication(sys.argv)
        window = MainWindow()
        window.resize(800, 600)
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        print("An error occurred:", e)
