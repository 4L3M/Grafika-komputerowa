#!/usr/bin/env python3
import sys
import numpy as np

from math import *
from OpenGL.GL import *
from OpenGL.GLU import *
from glfw.GLFW import *

viewer = [0.0, 0.0, 10.0]

theta = 180.0
phi = 0.0
pix2angle = 1.0
piy2angle = 1.0
pixs2angle = 1.0
scale = 1.0
R = 15.0

left_mouse_button_pressed = 0
right_mouse_button_pressed = 0

mouse_x_pos_old = 0
mouse_y_pos_old = 0
delta_x = 0
delta_y = 0
delta_s = 0

upY = 1.0
n = 20
matrix = np.zeros((n + 1, n + 1, 3))
matrixColor = np.zeros((n + 1, n + 1, 3))


def drawChain():
    drawTorusLines(0.7, 0.0, 0.7, 0.0)
    drawTorusLines(0.3, 0.5, 0.2, 2.5)
    drawTorusLines(0.1, 0.9, 0.5, -5.0)
    drawTorusLines(0.9, 0.1, 0.1, -2.5)
    drawTorusLines(0.9, 0.8, 0.1, 5)
    drawTorusLines(0.3, 0.3, 0.67, 7.5)
    spin(90)
    drawTorusLines(0.9, 0.3, 0.67, -7.5)


# wypelnienie tablicy wartosciami
def matrixValues():
    for i in range(0, n + 1):
        for j in range(0, n + 1):
            u = i / n
            v = j / n
            R = 2
            r = 0.5
            # wsp. 'x'
            matrix[i][j][0] = (R + r * cos(2 * pi * v)) * cos(2 * pi * u)
            # wsp. 'y'
            matrix[i][j][1] = (R + r * cos(2 * pi * v)) * sin(2 * pi * u)
            # wsp. 'z'
            matrix[i][j][2] = r * sin(2 * pi * v)


def drawTorusLines(x, y, z, c):
    spin(90)
    glColor3f(x, y, z)
    for i in range(0, n):
        for j in range(0, n):
            glBegin(GL_LINES)
            glVertex3f(matrix[i][j][0], matrix[i][j][1] + c, matrix[i][j][2])
            glVertex3f(matrix[i + 1][j][0], matrix[i + 1][j][1] + c, matrix[i + 1][j][2])
            glVertex3f(matrix[i][j][0], matrix[i][j][1] + c, matrix[i][j][2])
            glVertex3f(matrix[i][j + 1][0], matrix[i][j + 1][1] + c, matrix[i][j + 1][2])
            glEnd()


def render(time):
    global theta
    global phi
    global R
    global upY

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    xeye = R * cos(2 * pi * theta / 360) * cos(2 * pi * phi / 360)
    yeye = R * sin(2 * pi * phi / 360)
    zeye = R * sin(2 * pi * theta / 360) * cos(2 * pi * phi / 360)

    gluLookAt(xeye, yeye, zeye, 0.0, 0.0, 0.0, 0.0, upY, 0.0)

    if phi > 180:
        phi -= 2 * 180
    elif phi <= -180:
        phi += 2 * 180

    if phi < -180 / 2 or phi > 180 / 2:
        upY = -1.0
    else:
        upY = 1

    if left_mouse_button_pressed:
        theta += delta_x * 6 * pix2angle
        phi += delta_y * 6 * piy2angle

    # 'R' moze przyjmowac wartosci od 1 do 20
    if right_mouse_button_pressed:
        if delta_x > 0 and R < 20:
            R += 1
        else:
            if R >= 1:
                R -= 1
    axes()
    drawChain()
    glFlush()


def mouse_button_callback(window, button, action, mods):
    global left_mouse_button_pressed
    global right_mouse_button_pressed

    if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
        left_mouse_button_pressed = 1
    else:
        left_mouse_button_pressed = 0

    if button == GLFW_MOUSE_BUTTON_RIGHT and action == GLFW_PRESS:
        right_mouse_button_pressed = 1
    else:
        right_mouse_button_pressed = 0


def mouse_motion_callback(window, x_pos, y_pos):
    global delta_x
    global mouse_x_pos_old
    global delta_y
    global mouse_y_pos_old

    delta_x = x_pos - mouse_x_pos_old
    mouse_x_pos_old = x_pos

    delta_y = y_pos - mouse_y_pos_old
    mouse_y_pos_old = y_pos


def update_viewport(window, width, height):
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
    global e_button_state

    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)


def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(400, 400, __file__, None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)
    matrixValues()
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


def axes():
    glBegin(GL_LINES)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(-5.0, 0.0, 0.0)
    glVertex3f(5.0, 0.0, 0.0)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, -5.0, 0.0)
    glVertex3f(0.0, 5.0, 0.0)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, -5.0)
    glVertex3f(0.0, 0.0, 5.0)

    glEnd()


def example_object():
    glColor3f(1.0, 1.0, 1.0)

    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_LINE)
    glRotatef(90, 1.0, 0.0, 0.0)
    glRotatef(-90, 0.0, 1.0, 0.0)

    gluSphere(quadric, 1.5, 10, 10)

    glTranslatef(0.0, 0.0, 1.1)
    gluCylinder(quadric, 1.0, 1.5, 1.5, 10, 5)
    glTranslatef(0.0, 0.0, -1.1)

    glTranslatef(0.0, 0.0, -2.6)
    gluCylinder(quadric, 0.0, 1.0, 1.5, 10, 5)
    glTranslatef(0.0, 0.0, 2.6)

    glRotatef(90, 1.0, 0.0, 1.0)
    glTranslatef(0.0, 0.0, 1.5)
    gluCylinder(quadric, 0.1, 0.0, 1.0, 5, 5)
    glTranslatef(0.0, 0.0, -1.5)
    glRotatef(-90, 1.0, 0.0, 1.0)

    glRotatef(-90, 1.0, 0.0, 1.0)
    glTranslatef(0.0, 0.0, 1.5)
    gluCylinder(quadric, 0.1, 0.0, 1.0, 5, 5)
    glTranslatef(0.0, 0.0, -1.5)
    glRotatef(90, 1.0, 0.0, 1.0)

    glRotatef(90, 0.0, 1.0, 0.0)
    glRotatef(-90, 1.0, 0.0, 0.0)
    gluDeleteQuadric(quadric)


def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)


def shutdown():
    pass


def spin(angle):
    glRotatef(angle, 1.0, 0.0, 0.0)
    glRotatef(angle, 0.0, 1.0, 0.0)
    glRotatef(angle, 0.0, 0.0, 1.0)


if __name__ == '__main__':
    main()