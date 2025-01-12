#!/usr/bin/env python3
import sys

from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *

# Parametry dla widoku i oświetlenia
viewer = [0.0, 0.0, 10.0]
light_position = [0.0, 0.0, 10.0, 1.0]

mat_ambient = [1.0, 1.0, 1.0, 1.0]
mat_diffuse = [1.0, 1.0, 1.0, 1.0]
mat_specular = [1.0, 1.0, 1.0, 1.0]
mat_shininess = 20.0

light_ambient = [0.1, 0.1, 0.0, 1.0]
light_diffuse = [0.8, 0.8, 0.0, 1.0]
light_specular = [1.0, 1.0, 1.0, 1.0]

att_constant = 1.0
att_linear = 0.05
att_quadratic = 0.001

# Zmienna do obrotu modelu
theta = 0.0
pix2angle = 1.0

# Parametry myszki
left_mouse_button_pressed = 0
mouse_x_pos_old = 0
delta_x = 0


def startup():
    """Funkcja inicjalizująca ustawienia OpenGL i oświetlenie."""
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Kolor tła
    glEnable(GL_DEPTH_TEST)  # Włącz test głębokości

    # Ustawienia materiałów
    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, mat_shininess)

    # Ustawienia oświetlenia
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, att_constant)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, att_linear)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, att_quadratic)

    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glShadeModel(GL_SMOOTH)  # Włącz wygładzanie


def shutdown():
    """Funkcja do czyszczenia zasobów po zakończeniu działania programu."""
    # Możesz dodać kod do zwalniania zasobów (np. tekstur), jeśli będzie to konieczne.
    pass


def render(time):
    """Renderowanie sceny."""
    global theta

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Ustawienie widoku
    gluLookAt(viewer[0], viewer[1], viewer[2],
              0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    # Obrót modelu na podstawie ruchu myszy
    if left_mouse_button_pressed:
        theta += delta_x * pix2angle

    glRotatef(theta, 0.0, 1.0, 0.0)

    # Renderowanie sfery
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL)
    gluSphere(quadric, 3.0, 10, 10)
    gluDeleteQuadric(quadric)

    # Zastosowanie oświetlenia
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    glFlush()


def update_viewport(window, width, height):
    """Aktualizacja widoku przy zmianie rozmiaru okna."""
    global pix2angle
    pix2angle = 360.0 / width

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
    """Obsługuje naciśnięcia klawiszy."""
    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)


def mouse_motion_callback(window, x_pos, y_pos):
    """Obsługuje ruch myszy."""
    global delta_x
    global mouse_x_pos_old

    delta_x = x_pos - mouse_x_pos_old
    mouse_x_pos_old = x_pos


def mouse_button_callback(window, button, action, mods):
    """Obsługuje przyciski myszy."""
    global left_mouse_button_pressed

    if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
        left_mouse_button_pressed = 1
    else:
        left_mouse_button_pressed = 0


def main():
    """Główna funkcja programu."""
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSetKeyCallback(window, keyboard_key_callback)
    glfwSetCursorPosCallback(window, mouse_motion_callback)
    glfwSetMouseButtonCallback(window, mouse_button_callback)
    glfwSwapInterval(1)

    startup()  # Inicjalizacja przed rozpoczęciem renderowania

    while not glfwWindowShouldClose(window):
        render(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()

    shutdown()  # Czyszczenie zasobów po zakończeniu działania

    glfwTerminate()


if __name__ == '__main__':
    main()
