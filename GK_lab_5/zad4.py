#!/usr/bin/env python3
import sys

import numpy as np

from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import *
from PIL import Image

viewer = [0.0, 0.0, 10.0] # pozycja obserwatora
theta = 0.0 # obrot obiektu
phi = 0.0
pix2angle = 1.0 # przelicznik pikseli na stopnie

left_mouse_button_pressed = 0 # czy lewy przycisk myszy jest wcisniety

mouse_x_pos_old = 0
mouse_y_pos_old = 0
delta_y = 0
delta_x = 0

# Właściwości materiału dla obiektu
mat_ambient = [1.0, 1.0, 1.0, 1.0]
mat_diffuse = [1.0, 1.0, 1.0, 1.0]
mat_specular = [1.0, 1.0, 1.0, 1.0]
mat_shininess = 20.0

# Właściwości światła
light_ambient = [0.1, 0.1, 0.0, 1.0]
light_diffuse = [0.95, 0.95, 0.95, 1.0]
light_specular = [1.0, 1.0, 1.0, 1.0]
light_position = [0.0, 0.0, 10, 1.0]

# Ustawienia tłumienia światła
att_constant = 1.0
att_linear = 0.05
att_quadratic = 0.001

# Wybór tekstury
choose_texture = 0

# Wczytanie tekstur z plików
texture1 = Image.open("tekstura.tga")
texture2 = Image.open("P6_t.tga")

n = 20

# Macierze do przechowywania danych wierzchołków, wektorów normalnych i tekstur
matrix = np.zeros((n + 1, n + 1, 3))
matrix_with_vectors = np.zeros((n + 1, n + 1, 3))
matrix_with_textures = np.zeros((n + 1, n + 1, 2))


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

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

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_CULL_FACE)

    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

# Funkcja zmieniająca teksturę (po naciśnięciu klawisza 'T')
def set_texture():
    if choose_texture:
        img = texture1
    else:
        img = texture2

    # Generate the texture if not already done
    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGB, img.size[0], img.size[1], 0,
        GL_RGB, GL_UNSIGNED_BYTE, img.tobytes("raw", "RGB", 0, -1)
    )

    # Set texture parameters
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)


def axes():
    glBegin(GL_LINES)

    # Oś X (czerwona)
    glColor3f(0.0, 0.0, 0.0)
    glVertex3f(-5.0, 0.0, 0.0)
    glVertex3f(5.0, 0.0, 0.0)

    # Oś Y (zielona)
    glColor3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, -5.0, 0.0)
    glVertex3f(0.0, 5.0, 0.0)

    # Oś Z (niebieska)
    glColor3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, -5.0)
    glVertex3f(0.0, 0.0, 5.0)

    glEnd()

def spin(angle):
    glRotatef(angle, 1.0, 0.0, 0.0)  # Rotate around the Y-axis
    glRotatef(angle, 0.0, 1.0, 0.0)  # Rotate around the Z-axis
    glRotate(angle, 0.0, 0.0, 1.0)  # Rotate around the X-axis


def shutdown():
    pass

# Funkcja renderująca scenę

def render(time):
    global theta, phi

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Ustawienie widoku
    gluLookAt(viewer[0], viewer[1], viewer[2], 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    # Aktualizacja obrotu na podstawie myszy
    if left_mouse_button_pressed:
        theta += delta_x * pix2angle
        phi += delta_y * pix2angle

    # Obrót obiektu na podstawie theta i phi
    glRotatef(phi, 1.0, 0.0, 0.0)  # Obrót w pionie (phi)
    glRotatef(theta, 0.0, 1.0, 0.0)  # Obrót w poziomie (theta)

    # Rysowanie sceny
    axes()
    draw_egg()

    set_texture()
    glFlush()


def draw_egg():
    for i in range(n):
        for j in range(n):
            if (i > (n / 2)):
                glFrontFace(GL_CW)
            else:
                glFrontFace(GL_CCW)

            glBegin(GL_TRIANGLES)
            glTexCoord2f(matrix_with_textures[i][j + 1][0], matrix_with_textures[i][j + 1][1])
            glNormal3f(matrix_with_vectors[i][j + 1][0], matrix_with_vectors[i][j + 1][1], matrix_with_vectors[i][j + 1][2])
            glVertex3f(matrix[i][j + 1][0], matrix[i][j + 1][1] - 5, matrix[i][j + 1][2])

            glTexCoord2f(matrix_with_textures[i][j][0], matrix_with_textures[i][j][1])
            glNormal3f(matrix_with_vectors[i][j][0], matrix_with_vectors[i][j][1], matrix_with_vectors[i][j][2])
            glVertex3f(matrix[i][j][0], matrix[i][j][1] - 5, matrix[i][j][2])

            glTexCoord2f(matrix_with_textures[i + 1][j + 1][0], matrix_with_textures[i + 1][j + 1][1])
            glNormal3f(matrix_with_vectors[i + 1][j + 1][0], matrix_with_vectors[i + 1][j + 1][1],
                       matrix_with_vectors[i + 1][j + 1][2])
            glVertex3f(matrix[i + 1][j + 1][0], matrix[i + 1][j + 1][1] - 5, matrix[i + 1][j + 1][2])
            glEnd()

            glBegin(GL_TRIANGLES)
            glTexCoord2f(matrix_with_textures[i + 1][j + 1][0], matrix_with_textures[i + 1][j + 1][1])
            glNormal3f(matrix_with_vectors[i + 1][j + 1][0], matrix_with_vectors[i + 1][j + 1][1],
                       matrix_with_vectors[i + 1][j + 1][2])
            glVertex3f(matrix[i + 1][j + 1][0], matrix[i + 1][j + 1][1] - 5, matrix[i + 1][j + 1][2])

            glTexCoord2f(matrix_with_textures[i][j][0], matrix_with_textures[i][j][1])
            glNormal3f(matrix_with_vectors[i][j][0], matrix_with_vectors[i][j][1], matrix_with_vectors[i][j][2])
            glVertex3f(matrix[i][j][0], matrix[i][j][1] - 5, matrix[i][j][2])

            glTexCoord2f(matrix_with_textures[i + 1][j][0], matrix_with_textures[i + 1][j][1])
            glNormal3f(matrix_with_vectors[i + 1][j][0], matrix_with_vectors[i + 1][j][1], matrix_with_vectors[i + 1][j][2])
            glVertex3f(matrix[i + 1][j][0], matrix[i + 1][j][1] - 5, matrix[i + 1][j][2])
            glEnd()


def generate_texture_coordinates():
    for i in range(0, n + 1):
        for j in range(0, n + 1):
            u = i / n
            v = j / n

            # obrocenie tekstury na wlasciwej polowce
            if (i > (n / 2)):
                matrix_with_textures[i][j][0] = v
                matrix_with_textures[i][j][1] = 1 - 2 * u

            else:
                matrix_with_textures[i][j][0] = v
                matrix_with_textures[i][j][1] = 2 * u


def vertex_data():
    for i in range(0, n + 1):
        for j in range(0, n + 1):
            u = i / n
            v = j / n
            # wsp. 'x'
            matrix[i][j][0] = (-90 * pow(u, 5) + 225 * pow(u, 4) - 270 * pow(u, 3) + 180 * pow(u, 2) - 45 * u) * cos(
                pi * v)
            # wsp. 'y'
            matrix[i][j][1] = 160 * pow(u, 4) - 320 * pow(u, 3) + 160 * pow(u, 2)
            # wsp. 'z'
            matrix[i][j][2] = (-90 * pow(u, 5) + 225 * pow(u, 4) - 270 * pow(u, 3) + 180 * pow(u, 2) - 45 * u) * sin(
                pi * v)


# wypelnienie tablicy z wektorami normalnymi wartosciami
def normal_vectors():
    for i in range(0, n + 1):
        for j in range(0, n + 1):
            u = i / n
            v = j / n

            xu = (-450 * pow(u, 4) + 900 * pow(u, 3) - 810 * pow(u, 2) + 360 * u - 45) * cos(pi * v)
            xv = pi * (90 * pow(u, 5) - 225 * pow(u, 4) + 270 * pow(u, 3) - 180 * pow(u, 2) + 45 * u) * sin(pi * v)
            yu = 640 * pow(u, 3) - 960 * pow(u, 2) + 320 * u
            yv = 0
            zu = (-450 * pow(u, 4) + 900 * pow(u, 3) - 810 * pow(u, 2) + 360 * u - 45) * sin(pi * v)
            zv = (- pi) * (90 * pow(u, 5) - 225 * pow(u, 4) + 270 * pow(u, 3) - 180 * pow(u, 2) + 45 * u) * cos(pi * v)

            x = yu * zv - zu * yv
            y = zu * xv - xu * zv
            z = xu * yv - yu * xv

            sum = pow(x, 2) + pow(y, 2) + pow(z, 2)
            length = sqrt(sum)

            if length > 0:
                x = x / length
                y = y / length
                z = z / length

            if i > n / 2:
                x *= -1
                y *= -1
                z *= -1

            matrix_with_vectors[i][j][0] = x
            matrix_with_vectors[i][j][1] = y
            matrix_with_vectors[i][j][2] = z


def update_viewport(window, width, height):
    global pix2angle
    pix2angle = 180.0 / min(width, height)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(70, 1.0, 0.1, 300.0)

    if width <= height:
        glViewport(0, int((height - width) / 2), width, width)
    else:
        glViewport(int((width - height) / 2), 0, height, height)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def keyboard_key_callback(window, key, scancode, action, mods):
    global choose_texture
    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)
    if key == GLFW_KEY_T and action == GLFW_PRESS:
        if choose_texture == 0:
            choose_texture = 1
        else:
            choose_texture = 0


def mouse_motion_callback(window, x_pos, y_pos):
    global delta_x, delta_y
    global mouse_x_pos_old, mouse_y_pos_old

    delta_x = x_pos - mouse_x_pos_old
    delta_y = y_pos - mouse_y_pos_old

    mouse_x_pos_old = x_pos
    mouse_y_pos_old = y_pos


def mouse_button_callback(window, button, action, mods):
    global left_mouse_button_pressed

    if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
        left_mouse_button_pressed = 1
    else:
        left_mouse_button_pressed = 0


def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    normal_vectors()
    vertex_data()
    generate_texture_coordinates()

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSetKeyCallback(window, keyboard_key_callback)
    glfwSetCursorPosCallback(window, mouse_motion_callback)
    glfwSetMouseButtonCallback(window, mouse_button_callback)
    glfwSwapInterval(1)

    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()

    glfwTerminate()


if __name__ == '__main__':
    main()