import sys
import numpy as np
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout
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

    def initializeGL(self):
        glEnable(GL_TEXTURE_2D)
        glClearColor(0.2, 0.3, 0.3, 1.0)
        self.texture = create_texture(256)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        scale = self.zoom

        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)
        glColor3f(0.1, 0.5, 0.1)
        glTexCoord2f(0.0, 0.0)
        glVertex2f(-scale, -scale)
        glTexCoord2f(1.0, 0.0)
        glVertex2f(scale, -scale)
        glTexCoord2f(1.0, 1.0)
        glVertex2f(scale, scale)
        glTexCoord2f(0.0, 1.0)
        glVertex2f(-scale, scale)
        glEnd()

    def zoom_in(self):
        self.zoom *= 1.1
        self.update()

    def zoom_out(self):
        self.zoom /= 1.1
        self.update()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 + OpenGL + Texture Zoom")

        layout = QVBoxLayout()

        self.gl_widget = GLWidget()
        layout.addWidget(self.gl_widget)

        btn_layout = QHBoxLayout()
        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.clicked.connect(self.gl_widget.zoom_in)
        btn_layout.addWidget(zoom_in_btn)

        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.clicked.connect(self.gl_widget.zoom_out)
        btn_layout.addWidget(zoom_out_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

app = QApplication(sys.argv)
window = MainWindow()
window.resize(600, 600)
window.show()
sys.exit(app.exec())
