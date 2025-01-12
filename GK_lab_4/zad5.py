#!/usr/bin/env python3
import sys
from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import *
import random
import numpy as np
import glfw

viewer_position = [0.0, 0.0, 10.0]

rotation_angle = 0.0
pixel_to_angle = 1.0
altitude = 0.0
pitch_angle = 1.0
mouse_left_pressed = False
prev_mouse_x = 0
x_diff = 0
prev_mouse_y = 0
y_diff = 0

ambient_material = [0.1, 0.0, 0.5, 1.0]  # Darker purple
diffuse_material = [0.5, 0.0, 1.0, 1.0]  # Purple
specular_material = [1.0, 0.0, 1.0, 1.0]  # Light purple


shininess_factor = 20.0

ambient_light_1 = [0.1, 0.1, 0.0, 1.0]
diffuse_light_1 = [0.9, 0.4, 0.9, 1.0]
specular_light_1 = [1.0, 1.0, 1.0, 1.0]
light_position_1 = [0.0, 0.0, 10.0, 1.0]

ambient_material_2 = [1.0, 1.0, 1.0, 1.0]
diffuse_material_2 = [1.0, 1.0, 1.0, 1.0]
specular_material_2 = [1.0, 1.0, 1.0, 1.0]
shininess_factor_2 = 20.0
ambient_light_2 = [0.05, 0.1, 0.0, 1.0]
diffuse_light_2 = [1.0, 0.0, 1.0, 1.0]
specular_light_2 = [1.0, 1.0, 1.0, 1.0]
light_position_2 = [10.0, 5.0, 1.0, 1.0]

light_att_constant = 1.0
light_att_linear = 0.05
light_att_quadratic = 0.001

x_key_pressed = True


def setup():
    set_viewport(None, 400, 400)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    glMaterialfv(GL_FRONT, GL_AMBIENT, ambient_material)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse_material)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular_material)
    glMaterialf(GL_FRONT, GL_SHININESS, shininess_factor)
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light_1)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light_1)
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light_1)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position_1)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, light_att_constant)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, light_att_linear)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, light_att_quadratic)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glMaterialfv(GL_FRONT, GL_AMBIENT, ambient_material_2)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, diffuse_material_2)
    glMaterialfv(GL_FRONT, GL_SPECULAR, specular_material_2)
    glMaterialf(GL_FRONT, GL_SHININESS, shininess_factor_2)
    glLightfv(GL_LIGHT1, GL_AMBIENT, ambient_light_2)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, diffuse_light_2)
    glLightfv(GL_LIGHT1, GL_SPECULAR, specular_light_2)
    glLightfv(GL_LIGHT1, GL_POSITION, light_position_2)
    glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, light_att_constant)
    glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, light_att_linear)
    glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, light_att_quadratic)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT1)


def cleanup():
    pass


def rotate(angle):
    glRotatef(angle, 1.0, 0.0, 0.0)
    glRotatef(angle, 0.0, 1.0, 0.0)
    glRotatef(angle, 0.0, 0.0, 1.0)


num_segments = 20
coordinates_matrix = np.zeros((num_segments + 1, num_segments + 1, 3))
normal_vectors_matrix = np.zeros((num_segments + 1, num_segments + 1, 3))


def draw_scene(time):
    global rotation_angle
    global altitude
    global x_key_pressed

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(viewer_position[0], viewer_position[1], viewer_position[2], 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    if mouse_left_pressed:
        rotation_angle += x_diff * pixel_to_angle
        altitude += y_diff * pitch_angle

    glRotatef(rotation_angle, 0.0, 1.0, 0.0)
    glRotatef(altitude, 1.0, 0.0, 0.0)

    draw_egg_surface()

    if x_key_pressed:
        draw_normal_vectors()

    glFlush()


def draw_egg_surface(time):
    for i in range(0, num_segments):
        for j in range(0, num_segments):
            u = i / num_segments
            v = j / num_segments

            # Pobranie koloru na podstawie parametrów u, v i czasu
            color = get_color(u, v, time)
            glColor3fv(color)  # Ustawienie koloru dla tego trójkąta

            glBegin(GL_TRIANGLES)
            # Rysowanie trójkąta
            glNormal3f(normal_vectors_matrix[i][j][0], normal_vectors_matrix[i][j][1], normal_vectors_matrix[i][j][2])
            glVertex3f(coordinates_matrix[i][j][0], coordinates_matrix[i][j][1] - 5, coordinates_matrix[i][j][2])

            glNormal3f(normal_vectors_matrix[i + 1][j][0], normal_vectors_matrix[i + 1][j][1],
                       normal_vectors_matrix[i + 1][j][2])
            glVertex3f(coordinates_matrix[i + 1][j][0], coordinates_matrix[i + 1][j][1] - 5,
                       coordinates_matrix[i + 1][j][2])

            glNormal3f(normal_vectors_matrix[i + 1][j + 1][0], normal_vectors_matrix[i + 1][j + 1][1],
                       normal_vectors_matrix[i + 1][j + 1][2])
            glVertex3f(coordinates_matrix[i + 1][j + 1][0], coordinates_matrix[i + 1][j + 1][1] - 5,
                       coordinates_matrix[i + 1][j + 1][2])

            glNormal3f(normal_vectors_matrix[i][j + 1][0], normal_vectors_matrix[i][j + 1][1],
                       normal_vectors_matrix[i][j + 1][2])
            glVertex3f(coordinates_matrix[i][j + 1][0], coordinates_matrix[i][j + 1][1] - 5,
                       coordinates_matrix[i][j + 1][2])

            glNormal3f(normal_vectors_matrix[i][j][0], normal_vectors_matrix[i][j][1], normal_vectors_matrix[i][j][2])
            glVertex3f(coordinates_matrix[i][j][0], coordinates_matrix[i][j][1] - 5, coordinates_matrix[i][j][2])

            glNormal3f(normal_vectors_matrix[i + 1][j + 1][0], normal_vectors_matrix[i + 1][j + 1][1],
                       normal_vectors_matrix[i + 1][j + 1][2])
            glVertex3f(coordinates_matrix[i + 1][j + 1][0], coordinates_matrix[i + 1][j + 1][1] - 5,
                       coordinates_matrix[i + 1][j + 1][2])
            glEnd()


def initialize_coordinates():
    for i in range(0, num_segments + 1):
        for j in range(0, num_segments + 1):
            u = i / num_segments
            v = j / num_segments
            coordinates_matrix[i][j][0] = (-90 * u**5 + 225 * u**4 - 270 * u**3 + 180 * u**2 - 45 * u) * cos(pi * v)
            coordinates_matrix[i][j][1] = 160 * u**4 - 320 * u**3 + 160 * u**2
            coordinates_matrix[i][j][2] = (-90 * u**5 + 225 * u**4 - 270 * u**3 + 180 * u**2 - 45 * u) * sin(pi * v)


def initialize_normal_vectors():
    for i in range(0, num_segments + 1):
        for j in range(0, num_segments + 1):
            u = i / num_segments
            v = j / num_segments

            xu = (-450 * u**4 + 900 * u**3 - 810 * u**2 + 360 * u - 45) * cos(pi * v)
            xv = pi * (90 * u**5 - 225 * u**4 + 270 * u**3 - 180 * u**2 + 45 * u) * sin(pi * v)
            yu = 640 * u**3 - 960 * u**2 + 320 * u
            yv = 0
            zu = (-450 * u**4 + 900 * u**3 - 810 * u**2 + 360 * u - 45) * sin(pi * v)
            zv = (-pi) * (90 * u**5 - 225 * u**4 + 270 * u**3 - 180 * u**2 + 45 * u) * cos(pi * v)

            x = yu * zv - zu * yv
            y = zu * xv - xu * zv
            z = xu * yv - yu * xv

            length = sqrt(x**2 + y**2 + z**2)

            if length > 0:
                x /= length
                y /= length
                z /= length

            if i > num_segments / 2:
                x *= -1
                y *= -1
                z *= -1

            normal_vectors_matrix[i][j][0] = x
            normal_vectors_matrix[i][j][1] = y
            normal_vectors_matrix[i][j][2] = z


def get_color(u, v, time):
    """Interpoluje kolor w zależności od parametrów u, v i czasu."""
    r = 0.5 + 0.5 * np.sin(np.pi * u + time)
    g = 0.5 + 0.5 * np.sin(np.pi * v + time)
    b = 0.5 + 0.5 * np.sin(np.pi * (u + v) + time)

    return (r, g, b)


def color_from_normal(x, y, z):
    # Normalize the vector
    length = sqrt(x ** 2 + y ** 2 + z ** 2)
    if length > 0:
        x /= length
        y /= length
        z /= length

    # Create color based on the normal vector direction (simple RGB interpolation)
    r = 0.5 * (x + 1)  # Normalize to 0-1 range
    g = 0.5 * (y + 1)  # Normalize to 0-1 range
    b = 0.5 * (z + 1)  # Normalize to 0-1 range
    return [r, g, b, 1.0]  # RGBA format


def draw_normal_vectors():
    for i in range(0, num_segments):
        for j in range(0, num_segments):
            # Get the color based on the normal vector direction
            normal_color = color_from_normal(normal_vectors_matrix[i][j][0], normal_vectors_matrix[i][j][1],
                                             normal_vectors_matrix[i][j][2])
            glColor4fv(normal_color)  # Apply the color to the normal vectors

            glBegin(GL_LINES)
            glVertex3f(coordinates_matrix[i][j][0], coordinates_matrix[i][j][1] - 5, coordinates_matrix[i][j][2])
            glVertex3f(coordinates_matrix[i][j][0] + normal_vectors_matrix[i][j][0],
                       coordinates_matrix[i][j][1] + normal_vectors_matrix[i][j][1] - 5,
                       coordinates_matrix[i][j][2] + normal_vectors_matrix[i][j][2])
            glEnd()


def draw_egg_surface():
    for i in range(0, num_segments):
        for j in range(0, num_segments):
            glBegin(GL_TRIANGLES)
            glNormal3f(normal_vectors_matrix[i][j][0], normal_vectors_matrix[i][j][1], normal_vectors_matrix[i][j][2])
            glVertex3f(coordinates_matrix[i][j][0], coordinates_matrix[i][j][1] - 5, coordinates_matrix[i][j][2])
            glNormal3f(normal_vectors_matrix[i + 1][j][0], normal_vectors_matrix[i + 1][j][1], normal_vectors_matrix[i + 1][j][2])
            glVertex3f(coordinates_matrix[i + 1][j][0], coordinates_matrix[i + 1][j][1] - 5, coordinates_matrix[i + 1][j][2])
            glNormal3f(normal_vectors_matrix[i + 1][j + 1][0], normal_vectors_matrix[i + 1][j + 1][1],
                       normal_vectors_matrix[i + 1][j + 1][2])
            glVertex3f(coordinates_matrix[i + 1][j + 1][0], coordinates_matrix[i + 1][j + 1][1] - 5,
                       coordinates_matrix[i + 1][j + 1][2])
            glNormal3f(normal_vectors_matrix[i][j + 1][0], normal_vectors_matrix[i][j + 1][1],
                       normal_vectors_matrix[i][j + 1][2])
            glVertex3f(coordinates_matrix[i][j + 1][0], coordinates_matrix[i][j + 1][1] - 5, coordinates_matrix[i][j + 1][2])
            glNormal3f(normal_vectors_matrix[i][j][0], normal_vectors_matrix[i][j][1], normal_vectors_matrix[i][j][2])
            glVertex3f(coordinates_matrix[i][j][0], coordinates_matrix[i][j][1] - 5, coordinates_matrix[i][j][2])
            glNormal3f(normal_vectors_matrix[i + 1][j + 1][0], normal_vectors_matrix[i + 1][j + 1][1],
                       normal_vectors_matrix[i + 1][j + 1][2])
            glVertex3f(coordinates_matrix[i + 1][j + 1][0], coordinates_matrix[i + 1][j + 1][1] - 5,
                       coordinates_matrix[i + 1][j + 1][2])
            glEnd()


def set_viewport(window, width, height):
    global pixel_to_angle
    pixel_to_angle = 360.0 / width

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()

    gluPerspective(70, 1.0, 0.1, 300.0)

    if width <= height:
        glViewport(0, int((height - width) / 2), width, width)
    else:
        glViewport(int((width - height) / 2), 0, height, height)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def handle_key_press(window, key, scancode, action, mods):
    global x_key_pressed

    if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
        glfw.set_window_should_close(window, True)
    if key == glfw.KEY_X and action == glfw.PRESS:
        x_key_pressed = not x_key_pressed


def handle_mouse_motion(window, x_pos, y_pos):
    global x_diff
    global prev_mouse_x
    global y_diff
    global prev_mouse_y

    x_diff = x_pos - prev_mouse_x
    prev_mouse_x = x_pos

    y_diff = y_pos - prev_mouse_y
    prev_mouse_y = y_pos


def handle_mouse_button(window, button, action, mods):
    global mouse_left_pressed

    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        mouse_left_pressed = True
    else:
        mouse_left_pressed = False


def main():
    if not glfw.init():
        sys.exit(-1)

    window = glfw.create_window(400, 400, __file__, None, None)
    if not window:
        glfw.terminate()
        sys.exit(-1)

    random.seed(1)
    initialize_normal_vectors()
    initialize_coordinates()

    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, set_viewport)
    glfw.set_key_callback(window, handle_key_press)
    glfw.set_cursor_pos_callback(window, handle_mouse_motion)
    glfw.set_mouse_button_callback(window, handle_mouse_button)
    glfw.swap_interval(1)

    setup()
    while not glfw.window_should_close(window):
        draw_scene(glfw.get_time())
        glfw.swap_buffers(window)
        glfw.poll_events()
    cleanup()

    glfw.terminate()


if __name__ == '__main__':
    main()
