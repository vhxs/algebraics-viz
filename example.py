from typing import Generator
from algebraics.graphics.circle import generate_circles
from algebraics.graphics.models import Circle
from algebraics.polynomial.models import RootSet
from algebraics.polynomial.polynomial import enumerate_polynomials, enumerate_polynomials_sjbrooks, find_roots
from pydantic import BaseModel
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import time
import math
import numpy as np

# ---------------------------
# Circle Class for Parameters
# ---------------------------
# class Circle(BaseModel):
#     x_center: float
#     y_center: float
#     radius: float
#     red: float
#     green: float
#     blue: float

# ---------------------------
# Circle Generation (generate_circles)
# ---------------------------
# def generate_circles(dummy):
#     num_circles = 150  # Number of circles to generate
#     circles = []
#     for i in range(num_circles):
#         angle = i * 0.3
#         dist = i * 0.5
#         x_center = math.cos(angle) * dist
#         y_center = math.sin(angle) * dist
#         # Base radius similar to original: 0.125 * (0.5 ** (i mod 3))
#         base_radius = 0.125 * (0.5 ** (i % 3))
#         mod = (i % 8) + 1
#         if mod == 1:
#             red, green, blue = 1.0, 0.0, 0.0
#         elif mod == 2:
#             red, green, blue = 0.0, 1.0, 0.0
#         elif mod == 3:
#             red, green, blue = 0.0, 0.0, 1.0
#         elif mod == 4:
#             red, green, blue = 0.7, 0.7, 0.0
#         elif mod == 5:
#             red, green, blue = 1.0, 0.6, 0.0
#         elif mod == 6:
#             red, green, blue = 0.0, 1.0, 1.0
#         elif mod == 7:
#             red, green, blue = 1.0, 0.0, 1.0
#         elif mod == 8:
#             red, green, blue = 0.6, 0.6, 0.6

#         circle = Circle(
#             x_center=x_center,
#             y_center=y_center,
#             radius=base_radius,
#             red=red,
#             green=green,
#             blue=blue
#         )
#         circles.append(circle)
#     return circles

def generate_all_circles(root_sets: list[RootSet]) -> Generator[Circle]:
    for root_set in root_sets:
        yield from generate_circles(root_set)

# ---------------------------
# Texture Generator (create_texture)
# ---------------------------
def create_texture(sz):
    tex = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    xs = sz
    ys = sz
    # Create coordinate grids with y running from top to bottom.
    X, Y = np.meshgrid(np.arange(xs), np.arange(ys-1, -1, -1), indexing='xy')
    center = sz / 2.0
    # Compute f = ((sz/2)^2) / (1 + (x - center)^2 + (y - center)^2)
    f = ((sz / 2.0) ** 2) / (1 + (X - center)**2 + (Y - center)**2)
    # Clamp values to a maximum of 255.
    f = np.minimum(255, f)
    f = f.astype(np.uint8)
    # Create an RGB image where each channel is f.
    data = np.stack((f, f, f), axis=-1)
    
    gluBuild2DMipmaps(GL_TEXTURE_2D, 3, xs, ys, GL_RGB, GL_UNSIGNED_BYTE, data)
    return tex

# ---------------------------
# Draw a Textured Quad as a Circle (draw_circle)
# ---------------------------
def draw_circle(circle: Circle, scale_factor=1.0):
    # Set the color based on the circle's RGB values.
    glColor3f(circle.red, circle.green, circle.blue)
    effective_radius = circle.radius * scale_factor
    glTexCoord2f(0, 0)
    glVertex2f(circle.x_center - effective_radius, circle.y_center - effective_radius)
    glTexCoord2f(1, 0)
    glVertex2f(circle.x_center + effective_radius, circle.y_center - effective_radius)
    glTexCoord2f(1, 1)
    glVertex2f(circle.x_center + effective_radius, circle.y_center + effective_radius)
    glTexCoord2f(0, 1)
    glVertex2f(circle.x_center - effective_radius, circle.y_center + effective_radius)

# ---------------------------
# Screenshot Function
# ---------------------------
def screenshotauto():
    filename = "screenshot_{}.png".format(int(time.time()))
    screenshot = pygame.display.get_surface()
    pygame.image.save(screenshot, filename)
    print("Screenshot saved as", filename)

# ---------------------------
# Main Program
# ---------------------------
def main():
    pygame.init()
    xres, yres = 1000, 1000
    pygame.display.set_mode((xres, yres), DOUBLEBUF | OPENGL)
    pygame.display.set_caption("Algebraic numbers [Stephen Brooks 2010]")

    # Set up an orthographic projection.
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-1, 1, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Global offset and scaling factors.
    ox, oy = 0.0, 0.0
    zoom = 1.0
    # Global factors for scaling circle radii.
    k1 = 1.0
    k2 = 1.0

    polynomials = [polynomial for polynomial in enumerate_polynomials(7, 7)]
    root_sets = [find_roots(polynomial) for polynomial in polynomials]
    root_sets = [root_set for root_set in root_sets if root_set is not None]
    circles = list(generate_all_circles(root_sets))

    ot = time.time()
    # circles = generate_circles(15)
    display_list = 0
    tex = create_texture(256)
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = time.time() - ot
        ot = time.time()

        # Process events.
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == pygame.K_z:
                    k1 *= 1.3
                    if display_list:
                        glDeleteLists(display_list, 1)
                        display_list = 0
                elif event.key == pygame.K_x:
                    k1 /= 1.3
                    if display_list:
                        glDeleteLists(display_list, 1)
                        display_list = 0
                elif event.key == pygame.K_c:
                    k2 += 0.05
                    if display_list:
                        glDeleteLists(display_list, 1)
                        display_list = 0
                elif event.key == pygame.K_v:
                    k2 -= 0.05
                    if display_list:
                        glDeleteLists(display_list, 1)
                        display_list = 0
                elif event.key == pygame.K_l:
                    if display_list:
                        glDeleteLists(display_list, 1)
                        display_list = 0
                elif event.key == pygame.K_s and (pygame.key.get_mods() & KMOD_CTRL):
                    screenshotauto()
                elif event.key == pygame.K_ESCAPE:
                    running = False

        # Use arrow keys to pan the view.
        keys = pygame.key.get_pressed()
        speed = 0.5  # world units per second
        if keys[pygame.K_LEFT]:
            ox -= speed * dt
        if keys[pygame.K_RIGHT]:
            ox += speed * dt
        if keys[pygame.K_UP]:
            oy += speed * dt
        if keys[pygame.K_DOWN]:
            oy -= speed * dt

        # Zoom in/out with mouse buttons.
        mb = pygame.mouse.get_pressed()
        if mb[0]:
            zoom *= math.exp(dt * 3)
        if mb[2]:
            zoom *= math.exp(-dt * 3)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glPushMatrix()
        glScaled(zoom, zoom, zoom)
        glTranslated(-ox, -oy, 0)

        # (Re)compile the display list if needed.
        if display_list == 0:
            display_list = glGenLists(1)
            glNewList(display_list, GL_COMPILE_AND_EXECUTE)
            glEnable(GL_BLEND)
            glBlendFunc(GL_ONE, GL_ONE)
            glDisable(GL_DEPTH_TEST)
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, tex)
            glBegin(GL_QUADS)
            # Draw each circle in reverse order.
            for circle in circles:
                # The color and effective radius are now handled inside draw_circle.
                draw_circle(circle, k1 * k2)
            glEnd()
            glEndList()
        else:
            glCallList(display_list)

        glPopMatrix()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == '__main__':
    main()
