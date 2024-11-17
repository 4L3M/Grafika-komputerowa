#!/usr/bin/env python3
import sys
import numpy as np
import random
from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *


def egg_model(N):
    """Generuje siatkę punktów NxN reprezentującą kształt jajka i przypisuje losowe kolory do każdego wierzchołka."""
    u = np.linspace(0.0, 1.0, N)
    v = np.linspace(0.0, 1.0, N)

    # Przygotowujemy tablicę wierzchołków oraz tablicę kolorów
    vertices = np.zeros((N, N, 3), dtype=np.float32)
    colors = np.zeros((N, N, 3), dtype=np.float32)

    # Wypełniamy tablicę wierzchołków za pomocą parametrycznych równań jajka
    for i in range(N):
        for j in range(N):
            uu = u[i]
            vv = v[j]

            # Parametryczne równania jajka
            x = (-90 * uu**5 + 225 * uu**4 - 270 * uu**3 + 180 * uu**2 - 45 * uu) * np.cos(np.pi * vv)
            y = 160 * uu**4 - 320 * uu**3 + 160 * uu**2 - 5
            z = (-90 * uu**5 + 225 * uu**4 - 270 * uu**3 + 180 * uu**2 - 45 * uu) * np.sin(np.pi * vv)

            vertices[i][j] = [x, y, z]

            # # Losowanie żywych kolorów w zakresie niebiesko-różowo-fioletowym
            # r = random.uniform(0.7, 1.0)  # Więcej czerwieni dla różowych i fioletowych tonów
            # g = random.uniform(0.4, 0.8)  # Zielony dla lekko pastelowych barw
            # b = random.uniform(0.7, 1.0)  # Więcej niebieskiego dla niebieskich i fioletowych tonów
            #
            # # Losowe wzmacnianie lub osłabianie dominujących kolorów
            # if random.random() < 0.5:  # Preferujemy bardziej niebieskie odcienie
            #     r *= random.uniform(0.6, 0.9)  # Lekko tłumimy czerwień
            # else:  # Preferujemy bardziej różowe/fioletowe odcienie
            #     b *= random.uniform(0.6, 0.9)  # Lekko tłumimy niebieski

            colors[i][j] = [random.random(), random.random(), random.random()]

    return vertices, colors


def render(time):
    angle = time * 180.0 / np.pi  # Obliczanie kąta na podstawie czasu (w radianach)

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glRotatef(-30, 1.0, 0.0, 0.0)  # Obrót o 30 stopni wokół osi X
    spin(angle)  # Obracanie obiektu na podstawie czasu

    axes()  # Rysowanie osi współrzędnych

    # Rysowanie modelu jajka jako siatka trójkątów
    glBegin(GL_TRIANGLES)

    # Iteracja po wierzchołkach i rysowanie trójkątów
    for i in range(egg_vertices.shape[0] - 1):
        for j in range(egg_vertices.shape[1] - 1):
            # Wierzchołki trójkątów - jeden z (i, j) połączony z (i+1, j) oraz (i, j+1)
            # Trójkąt 1
            glColor3f(*egg_colors[i][j])
            glVertex3f(*egg_vertices[i][j])

            glColor3f(*egg_colors[i + 1][j])
            glVertex3f(*egg_vertices[i + 1][j])

            glColor3f(*egg_colors[i][j + 1])
            glVertex3f(*egg_vertices[i][j + 1])

            # Trójkąt 2 (dopełniający)
            glColor3f(*egg_colors[i + 1][j])
            glVertex3f(*egg_vertices[i + 1][j])

            glColor3f(*egg_colors[i + 1][j + 1])
            glVertex3f(*egg_vertices[i + 1][j + 1])

            glColor3f(*egg_colors[i][j + 1])
            glVertex3f(*egg_vertices[i][j + 1])

    glEnd()
    glFlush()


def spin(angle):
    """Rotate the object by the specified angle."""
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


def shutdown():
    pass


def main():
    global egg_vertices, egg_colors

    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, "Model Jajka", None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSwapInterval(1)

    # Generowanie wierzchołków jajka i kolorów
    N = 50  # Rozdzielczość siatki
    egg_vertices, egg_colors = egg_model(N)

    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()

    shutdown()
    glfwTerminate()


if __name__ == '__main__':
    main()
