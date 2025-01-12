#!/usr/bin/env python3
import sys
from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import sin, cos

# Viewer position
viewer = [0.0, 0.0, 10.0]

# Rotation parameters
theta = 0.0
phi = 0.0
pix2angle = 1.0

# Mouse handling
left_mouse_button_pressed = 0
mouse_x_pos_old = 0
mouse_y_pos_old = 0
delta_x = 0
delta_y = 0

# Light components
light_ambient = [0.1, 0.1, 0.1, 1.0]
light_diffuse = [0.8, 0.8, 0.8, 1.0]
light_specular = [1.0, 1.0, 1.0, 1.0]
light_position = [0.0, 0.0, 10.0, 1.0]

# Attenuation factors
att_constant = 1.0
att_linear = 0.05
att_quadratic = 0.001

# Function to initialize OpenGL settings
def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.1, 0.1, 0.1, 1.0)  # Dark background
    glEnable(GL_DEPTH_TEST)

    # Set material properties
    glMaterialfv(GL_FRONT, GL_AMBIENT, [0.1, 0.1, 0.1, 1.0])
    glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 50.0)

    # Set light properties
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    # Set light attenuation
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, att_constant)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, att_linear)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, att_quadratic)

    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

# Function to render the scene
def render(time):
    global theta, phi

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(viewer[0], viewer[1], viewer[2], 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    # Transform the light position based on theta and phi
    glPushMatrix()

    # Calculate the light position in spherical coordinates
    xs = 10.0 * (1 + 0.5 * phi) * sin(theta)
    ys = 10.0 * cos(phi)
    zs = 10.0 * (1 + 0.5 * phi) * cos(theta)

    # Update the light position
    light_position[0] = xs
    light_position[1] = ys
    light_position[2] = zs

    # Set light position in OpenGL
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    # Visualize the light source as a small sphere (built from lines)
    glPushMatrix()
    glTranslatef(xs, ys, zs)
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_LINE)  # Set drawing style to lines
    gluSphere(quadric, 0.5, 6, 5)  # Draw the sphere
    gluDeleteQuadric(quadric)
    glPopMatrix()

    # Render the main object (the sphere)
    glRotatef(theta, 0.0, 1.0, 0.0)
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL)
    gluSphere(quadric, 3.0, 50, 50)
    gluDeleteQuadric(quadric)

    glPopMatrix()
    glFlush()

# Function to update the viewport
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

# Keyboard key callback
def keyboard_key_callback(window, key, scancode, action, mods):
    global current_component, current_value_index

    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)

# Mouse motion callback to handle light movement
def mouse_motion_callback(window, x_pos, y_pos):
    global delta_x, delta_y, mouse_x_pos_old, mouse_y_pos_old, theta, phi

    # Calculate delta movement
    delta_x = x_pos - mouse_x_pos_old
    delta_y = y_pos - mouse_y_pos_old

    # Update theta and phi based on mouse movement
    theta += delta_x * pix2angle
    phi += delta_y * pix2angle

    # Clamp phi between 0 and pi (to avoid going below the "equator")
    phi = max(min(phi, 3.14), 0.0)

    mouse_x_pos_old = x_pos
    mouse_y_pos_old = y_pos

# Mouse button callback
def mouse_button_callback(window, button, action, mods):
    global left_mouse_button_pressed

    if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
        left_mouse_button_pressed = 1
    else:
        left_mouse_button_pressed = 0

# Main function
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
