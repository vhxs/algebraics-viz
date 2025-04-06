from OpenGL.GL import *
import math

from algebraics.graphics.models import Circle

def draw_circle(circle: Circle):
    glColor3f(circle.red, circle.green, circle.blue)
    glBegin(GL_TRIANGLE_FAN)
    num_segments = 100
    glVertex2f(circle.x_center, circle.y_center)  # Center of the circle
    for i in range(num_segments + 1):
        angle = 2.0 * math.pi * i / num_segments
        x = circle.x_center + circle.radius * math.cos(angle)
        y = circle.y_center + circle.radius * math.sin(angle)
        glVertex2f(x, y)
    glEnd()
    glFlush()

def setup_gl():
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1, 1, -1, 1, -1, 1)
