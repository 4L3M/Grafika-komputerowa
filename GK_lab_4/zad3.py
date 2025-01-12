#!/usr/bin/env python3
import sys

from glfw.GLFW import *

from OpenGL.GL import *
from OpenGL.GLU import *
from math import *

import random


viewer = [0.0, 0.0, 10.0]

theta = 0.0
phi = 0.0
pix2angle = 1.0

left_mouse_button_pressed = 0
mouse_x_pos_old = 0
mouse_y_pos_old = 0
delta_x = 0
delta_y = 0

# Material properties
mat_ambient = [1.0, 1.0, 1.0, 1.0]
mat_diffuse = [1.0, 1.0, 1.0, 1.0]
mat_specular = [1.0, 1.0, 1.0, 1.0]
mat_shininess = 20.0

# Light properties
light_ambient = [0.1, 0.1, 0.0, 1.0]
light_diffuse = [0.8, 0.8, 0.0, 1.0]
light_specular = [1.0, 1.0, 1.0, 1.0]
light_position = [0.0, 0.0, 10.0, 1.0]

att_constant = 1.0
att_linear = 0.05
att_quadratic = 0.001

# Control variables
current_component = "ambient"  # Can be 'ambient', 'diffuse', or 'specular'
current_index = 0  # Index of the RGB component to modify

# Light source movement variables
xs = 0.0
ys = 0.0
zs = 10.0

def update_light_properties():
    """Update light properties based on current values."""
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, [xs, ys, zs, 1.0])


def print_current_values():
    """Print the current values of the light components."""
    print(f"Current Component: {current_component}")
    print(f"Ambient: {light_ambient}")
    print(f"Diffuse: {light_diffuse}")
    print(f"Specular: {light_specular}")
    print(f"Light Position: ({xs:.2f}, {ys:.2f}, {zs:.2f})")


def change_current_component():
    """Cycle through the components to select one for modification."""
    global current_component
    if current_component == "ambient":
        current_component = "diffuse"
    elif current_component == "diffuse":
        current_component = "specular"
    else:
        current_component = "ambient"
    print_current_values()


def modify_component_value(delta):
    """Modify the currently selected component's value."""
    global light_ambient, light_diffuse, light_specular

    component = {
        "ambient": light_ambient,
        "diffuse": light_diffuse,
        "specular": light_specular,
    }[current_component]

    # Update the selected RGB value
    component[current_index] = max(0.0, min(1.0, component[current_index] + delta))

    update_light_properties()
    print_current_values()

def modify_light_position(delta_x, delta_y):
    """Modify the position of the light source."""
    global xs, ys, zs, theta, phi

    # Factor to slow down the movement
    slow_factor = 0.01

    theta += delta_x * pix2angle * slow_factor
    phi += delta_y * pix2angle * slow_factor

    r = 10.0
    xs = r * sin(theta) * cos(phi)
    ys = r * sin(phi)
    zs = r * cos(theta) * cos(phi)

    update_light_properties()
    print_current_values()

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
    glLightfv(GL_LIGHT0, GL_POSITION, [xs, ys, zs, 1.0])

    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, att_constant)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, att_linear)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, att_quadratic)

    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)


def shutdown():
    pass


def render(time):
    global theta

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(viewer[0], viewer[1], viewer[2],
              0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    if left_mouse_button_pressed:
        theta += delta_x * pix2angle

        # Set the material color to pink (RGB = [1.0, 0.0, 1.0])
        pink_color = [1.0, 0.0, 1.0]
        glMaterialfv(GL_FRONT, GL_AMBIENT, pink_color)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, pink_color)
        glMaterialfv(GL_FRONT, GL_SPECULAR, pink_color)

    # Visualize light position
    glPushMatrix()
    glTranslatef(xs, ys, zs)
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_LINE)
    gluSphere(quadric, 0.5, 6, 5)
    gluDeleteQuadric(quadric)
    glPopMatrix()

    glRotatef(theta, 0.0, 1.0, 0.0)

    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL)
    gluSphere(quadric, 3.0, 10, 10)
    gluDeleteQuadric(quadric)

    glFlush()


def update_viewport(window, width, height):
    global pix2angle
    pix2angle = 360.0 / width / 10.0

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
    global current_index

    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)
    elif key == GLFW_KEY_TAB and action == GLFW_PRESS:
        change_current_component()
    elif key == GLFW_KEY_UP and action == GLFW_PRESS:
        modify_component_value(0.1)
    elif key == GLFW_KEY_DOWN and action == GLFW_PRESS:
        modify_component_value(-0.1)
    elif key == GLFW_KEY_LEFT and action == GLFW_PRESS:
        current_index = (current_index - 1) % 3
        print(f"Current index: {current_index}")
    elif key == GLFW_KEY_RIGHT and action == GLFW_PRESS:
        current_index = (current_index + 1) % 3
        print(f"Current index: {current_index}")


def mouse_motion_callback(window, x_pos, y_pos):
    global delta_x, delta_y
    global mouse_x_pos_old, mouse_y_pos_old

    delta_x = x_pos - mouse_x_pos_old
    delta_y = y_pos - mouse_y_pos_old
    mouse_x_pos_old = x_pos
    mouse_y_pos_old = y_pos

    if left_mouse_button_pressed:
        modify_light_position(delta_x, delta_y)


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
