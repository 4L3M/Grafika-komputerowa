#!/usr/bin/env python3
import sys
import numpy as np
import random
from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image

viewer = [0.0, 0.0, 10.0]

theta = 0.0
pix2angle = 1.0
phi = 0.0
piy2angle = 1.0
left_mouse_button_pressed = 0
mouse_x_pos_old = 0
delta_x = 0
mouse_y_pos_old = 0
delta_y = 0

mat_ambient = [1.0, 1.0, 1.0, 1.0]
mat_diffuse = [1.0, 1.0, 1.0, 1.0]
mat_specular = [1.0, 1.0, 1.0, 1.0]
mat_shininess = 20.0
light_ambient = [0.1, 0.1, 0.0, 1.0]
light_diffuse = [0.9, 0.4, 0.9, 1.0]
light_specular = [1.0, 1.0, 1.0, 1.0]
light_position = [0.0, 0.0, 10.0, 1.0]

# drugie zrodlo swiatla
mat_ambient1 = [1.0, 1.0, 1.0, 1.0]
mat_diffuse1 = [1.0, 1.0, 1.0, 1.0]
mat_specular1 = [1.0, 1.0, 1.0, 1.0]
mat_shininess1 = 20.0
light_ambient1 = [0.05, 0.1, 0.0, 1.0]
light_diffuse1 = [1.0, 0.0, 1.0, 1.0]
light_specular1 = [1.0, 1.0, 1.0, 1.0]
light_position1 = [10.0, 5.0, 1.0, 1.0]

att_constant = 1.0
att_linear = 0.05
att_quadratic = 0.001

x_buttons_state = 1


def load_texture(file_name):
    """Ładowanie teksturę z pliku."""
    image = Image.open(file_name)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)  # Flip to match OpenGL's texture coordinate system

    # Tworzenie tekstury
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, image.size[0], image.size[1], 0,
                 GL_RGB, GL_UNSIGNED_BYTE, image.tobytes("raw", "RGB", 0, -1))
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    return texture


def egg_model(N):
    """Generates an NxN grid of vertices representing the egg shape and assigns random colors to each vertex."""
    u = np.linspace(0.0, 1.0, N)
    v = np.linspace(0.0, 1.0, N)

    vertices = np.zeros((N, N, 3), dtype=np.float32)
    colors = np.zeros((N, N, 3), dtype=np.float32)
    tex_coords = np.zeros((N, N, 2), dtype=np.float32)  # Współrzędne tekstury

    for i in range(N):
        for j in range(N):
            uu = u[i]
            vv = v[j]

            # Parametryczne równania jajka
            x = (-90 * uu ** 5 + 225 * uu ** 4 - 270 * uu ** 3 + 180 * uu ** 2 - 45 * uu) * np.cos(np.pi * vv)
            y = 160 * uu ** 4 - 320 * uu ** 3 + 160 * uu ** 2 - 5
            z = (-90 * uu ** 5 + 225 * uu ** 4 - 270 * uu ** 3 + 180 * uu ** 2 - 45 * uu) * np.sin(np.pi * vv)

            vertices[i][j] = [x, y, z]

            # Random colors (optional, can be omitted if you use texture)
            colors[i][j] = [random.random(), random.random(), random.random()]

            # Przypisanie współrzędnych tekstury
            tex_coords[i][j] = [uu, vv]  # Współrzędne tekstury

    return vertices, tex_coords


def render(time, texture):
    global theta, phi, pix2angle, piy2angle
    angle = time * 180.0 / np.pi  # Obliczanie kąta na podstawie czasu (w radianach)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(viewer[0], viewer[1], viewer[2],
              0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    if left_mouse_button_pressed:
        theta += delta_x * pix2angle
        phi += delta_y * piy2angle

    glRotatef(-30, 1.0, 0.0, 0.0)  # Obrót o 30 stopni wokół osi X
    glRotatef(angle, 1.0, 1.0, 0.0)  # Rotate based on time (around both X and Y axis)

    axes()  # Rysowanie osi współrzędnych

    glBindTexture(GL_TEXTURE_2D, texture)  # Bindowanie tekstury
    # Rysowanie modelu jajka jako triangle strips
    for i in range(egg_vertices.shape[0] - 1):
        glBegin(GL_TRIANGLE_STRIP)

        for j in range(egg_vertices.shape[1]):
            # Pierwszy wierzchołek: (i, j)
            glTexCoord2f(egg_tex_coords[i][j][0], egg_tex_coords[i][j][1])  # Współrzędne tekstury
            glVertex3f(*egg_vertices[i][j])

            # Drugi wierzchołek: (i + 1, j)
            glTexCoord2f(egg_tex_coords[i + 1][j][0], egg_tex_coords[i + 1][j][1])  # Współrzędne tekstury
            glVertex3f(*egg_vertices[i + 1][j])

        glEnd()

    glFlush()



def spin(angle):
    glRotatef(angle, 1.0, 0.0, 0.0)  # Rotate around the Y-axis
    glRotatef(angle, 0.0, 1.0, 0.0)  # Rotate around the Z-axis
    glRotate(angle, 0.0, 0.0, 1.0)  # Rotate around the X-axis


def axes():
    glBegin(GL_LINES)

    # Oś X (czerwona)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-5.0, 0.0, 0.0)
    glVertex3f(5.0, 0.0, 0.0)

    # Oś Y (zielona)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, -5.0, 0.0)
    glVertex3f(0.0, 5.0, 0.0)

    # Oś Z (niebieska)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -5.0)
    glVertex3f(0.0, 0.0, 5.0)

    glEnd()


def update_viewport(window, width, height):
    if width == 0:
        width = 1
    if height == 0:
        height = 1
    aspect_ratio = width / height

    glMatrixMode(GL_PROJECTION)
    glViewport(0, 0, width, height)
    glLoadIdentity()

    if width <= height:
        glOrtho(-7.5, 7.5, -7.5 / aspect_ratio, 7.5 / aspect_ratio, 7.5, -7.5)
    else:
        glOrtho(-7.5 * aspect_ratio, 7.5 * aspect_ratio, -7.5, 7.5, 7.5, -7.5)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    glEnable(GL_TEXTURE_2D)  # Włącz teksturowanie

    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, mat_shininess)

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, att_constant)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, att_linear)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, att_quadratic)

    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)


def shutdown():
    pass


def main():
    global egg_vertices, egg_colors, egg_tex_coords

    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, "Model jajka", None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSwapInterval(1)

    # Generowanie wierzchołków jajka i kolorów
    N = 50  # Rozdzielczość siatki
    egg_vertices, egg_tex_coords = egg_model(N)

    # Ładowanie tekstury
    texture = load_texture("tekstura.tga")

    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime(), texture)
        glfwSwapBuffers(window)
        glfwPollEvents()

    shutdown()
    glfwTerminate()


if __name__ == '__main__':
    main()
