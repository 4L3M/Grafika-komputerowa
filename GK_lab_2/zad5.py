#!/usr/bin/env python3
import sys
import random
import numpy as np
from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Zmienne globalne do śledzenia kątów rotacji
x_angle = 0.0
y_angle = 0.0
z_angle = 0.0


def startup():
    update_viewport(None, 400, 400)
    glClearColor(1.0, 1.0, 1.0, 1.0)  # Ustawienie koloru tła na biały
    glEnable(GL_DEPTH_TEST)


def shutdown():
    pass


def interpolate_color(c1, c2, t):
    return [(1 - t) * c1[i] + t * c2[i] for i in range(3)] # Interpolacja liniowa dla każdego kanału RGB


def spin(angle):
    """Rotate the object by the specified angle."""
    glRotatef(angle, 1.0, 0.0, 0.0)  # Obrót wokół osi X
    glRotatef(angle, 0.0, 1.0, 0.0)  # Obrót wokół osi y
    glRotatef(angle, 0.0, 0.0, 1.0)  # Obrót wokół osi Z


def draw_triangle(p1, p2, p3, c1, c2, c3):
    glBegin(GL_TRIANGLES)

    # Ustawienie kolorów wierzchoła 1
    glColor3fv(c1)
    glVertex3fv(p1)

    # Ustawienie kolorów wierzchoła 2
    glColor3fv(c2)
    glVertex3fv(p2)

    # Ustawienie kolorów wierzchoła 3
    glColor3fv(c3)
    glVertex3fv(p3)
    glEnd()

def draw_triangle_outline(p1, p2, p3):
    glBegin(GL_LINE_LOOP) # Rysowanie linii łączących wierzchołki
    glColor3f(0.0, 0.0, 0.0)  # Czarny obrys
    glVertex3fv(p1) # Wierzchołek 1
    glVertex3fv(p2) # Wierzchołek 2
    glVertex3fv(p3) # Wierzchołek 3
    glEnd()

def sierpinski(p1, p2, p3, p4, c1, c2, c3, c4, depth):
    if depth == 0:
        # Jesli glebokosc rekursji wynosi 0, rysujemy trójkąty
        draw_triangle(p1, p2, p3, c1, c2, c3)
        draw_triangle(p1, p2, p4, c1, c2, c4)
        draw_triangle(p2, p3, p4, c2, c3, c4)
        draw_triangle(p3, p1, p4, c3, c1, c4)

        # Rysowanie obrysu trójkątów
        draw_triangle_outline(p1, p2, p3)
        draw_triangle_outline(p1, p2, p4)
        draw_triangle_outline(p2, p3, p4)
        draw_triangle_outline(p3, p1, p4)

    else:
        # Obliczanie środków odcinków dla wszystkich krawędzi
        m1 = [(p1[i] + p2[i]) / 2 for i in range(3)]
        m2 = [(p2[i] + p3[i]) / 2 for i in range(3)]
        m3 = [(p3[i] + p1[i]) / 2 for i in range(3)]
        m4 = [(p1[i] + p4[i]) / 2 for i in range(3)]
        m5 = [(p2[i] + p4[i]) / 2 for i in range(3)]
        m6 = [(p3[i] + p4[i]) / 2 for i in range(3)]

        # Interpolacja kolorów dla nowych punktów środkowych
        c12 = interpolate_color(c1, c2, 0.5)
        c23 = interpolate_color(c2, c3, 0.5)
        c31 = interpolate_color(c3, c1, 0.5)
        c14 = interpolate_color(c1, c4, 0.5)
        c25 = interpolate_color(c2, c4, 0.5)
        c36 = interpolate_color(c3, c4, 0.5)

        # Rekurencyjne wywołanie funkcji dla mniejszych piramid
        sierpinski(p1, m1, m3, m4, c1, c12, c31, c14, depth - 1)
        sierpinski(m1, p2, m2, m5, c12, c2, c23, c25, depth - 1)
        sierpinski(m3, m2, p3, m6, c31, c23, c3, c36, depth - 1)
        sierpinski(m4, m5, m6, p4, c14, c25, c36, c4, depth - 1)


def render(time, N):
    global x_angle, y_angle, z_angle

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Resetowanie macierzy transformacji

    # Zastosowanie rotacji wokół osi X, Y i Z
    glRotatef(x_angle, 1.0, 0.0, 0.0)  # Rotate around the X-axis
    glRotatef(y_angle, 0.0, 1.0, 0.0)  # Rotate around the Y-axis
    glRotatef(z_angle, 0.0, 0.0, 1.0)  # Rotate around the Z-axis

    # Współrzędne wierzchołków piramidy
    p1 = [-1.0, -1.0, -1.0]
    p2 = [1.0, -1.0, -1.0]
    p3 = [0.0, 1.0, -1.0]
    p4 = [0.0, 0.0, 1.0]

    # Kolory dla każdego wierzchołka piramidy
    c1 = [1.0, 0.0, 1.0]  # Magenta
    c2 = [0.0, 1.0, 1.0]  # Cyan
    c3 = [1.0, 1.0, 0.0]  # Yellow
    c4 = [0.5, 1.0, 0.0]  # Light Green

    # Rysowanie fraktala Sierpińskiego
    sierpinski(p1, p2, p3, p4, c1, c2, c3, c4, N)  # You can adjust the depth here

    glFlush()


def update_viewport(window, width, height):
    if width == 0:
        width = 1
    if height == 0:
        height = 1
    aspect_ratio = width / height

    glMatrixMode(GL_PROJECTION)
    glViewport(0, 0, width, height)
    glLoadIdentity()

    # Ustawienie rzutowania ortograficznego
    if width <= height:
        glOrtho(-3.0, 3.0, -3.0 / aspect_ratio, 3.0 / aspect_ratio, 3.0, -3.0)
    else:
        glOrtho(-3.0 * aspect_ratio, 3.0 * aspect_ratio, -3.0, 3.0, 3.0, -3.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def key_callback(window, key, scancode, action, mods):
    global x_angle, y_angle, z_angle

    if action == GLFW_PRESS or action == GLFW_REPEAT:
        if key == GLFW_KEY_W:
            x_angle += 5  # Obrót w górę wokół osi X
        elif key == GLFW_KEY_S:
            x_angle -= 5  # Obrót w dół wokół osi X
        elif key == GLFW_KEY_A:
            y_angle -= 5  # Obrót w lewo wokół osi Y
        elif key == GLFW_KEY_D:
            y_angle += 5  # Obrót w prawo wokół osi Y
        elif key == GLFW_KEY_Q:
            z_angle -= 5  # Obrót przeciwnie do ruchu wskazówek zegara wokół osi Z
        elif key == GLFW_KEY_E:
            z_angle += 5  # Obrót zgodnie z ruchem wskazówek zegara wokół osi Z


def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSetKeyCallback(window, key_callback)
    glfwSwapInterval(1)

    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime(), 3)
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()

    glfwTerminate()


if __name__ == '__main__':
    main()
