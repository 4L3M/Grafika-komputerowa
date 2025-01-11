#!/usr/bin/env python3
import sys
import math
from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image

viewer = [0.0, 0.0, 10.0]

# Globalne zmienne dla kamery
R = 30.0
theta = 0.0
phi = 0.0



camera_mode = 'free'  # Tryb kamery: 'free' lub 'planetary'
active_planet_index = 0  # Aktywna planeta w trybie "planetary"

left_mouse_button_pressed = False
mouse_x_pos_old = 0
mouse_y_pos_old = 0
delta_x = 0
delta_y = 0

textures = {}

# Lista planet z ich parametrami
planets = [
    {'name': 'Earth', 'radius': 5.0, 'distance': 15.0, 'speed': 0.5, 'texture': 'earth'},
    {'name': 'Mars', 'radius': 3.0, 'distance': 25.0, 'speed': 0.3, 'texture': 'mars'},
    {'name': 'Jupiter', 'radius': 10.0, 'distance': 40.0, 'speed': 0.2, 'texture': 'jupiter'}
]


def load_textures():
    global textures
    texture_files = {
        'sun': 'textures/sun.jpg',
        'earth': 'textures/earth.jpg',
        'mars': 'textures/mars.jpg',
        'jupiter': 'textures/jupiter.jpg',
        'stars': 'textures/stars.jpg'
    }

    for key, file in texture_files.items():
        texture = glGenTextures(1)
        textures[key] = texture
        glBindTexture(GL_TEXTURE_2D, texture)
        image = Image.open(file)
        image_data = image.convert("RGB").tobytes()
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)


def startup():
    update_viewport(None, 800, 800)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    load_textures()


def shutdown():
    pass


def draw_sphere_with_texture(radius, slices, stacks, texture):
    glBindTexture(GL_TEXTURE_2D, texture)
    quadric = gluNewQuadric()
    gluQuadricTexture(quadric, GL_TRUE)
    gluSphere(quadric, radius, slices, stacks)
    gluDeleteQuadric(quadric)


def render_orbit(radius):
    glBegin(GL_LINE_LOOP)
    for angle in range(0, 360, 5):
        x = radius * math.cos(math.radians(angle))
        z = radius * math.sin(math.radians(angle))
        glVertex3f(x, 0.0, z)
    glEnd()


def render_scene(time):
    global camera_mode, active_planet_index

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Ustawienie kamery
    if camera_mode == 'free':
        xeye = R * math.cos(math.radians(phi)) * math.cos(math.radians(theta))
        yeye = R * math.sin(math.radians(phi))
        zeye = R * math.cos(math.radians(phi)) * math.sin(math.radians(theta))
        gluLookAt(xeye, yeye, zeye, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)
    elif camera_mode == 'planetary':
        planet = planets[active_planet_index]
        angle = time * planet['speed']
        xeye = planet['distance'] * math.cos(angle)
        zeye = planet['distance'] * math.sin(angle)
        gluLookAt(xeye, 0.0, zeye, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    # Renderowanie tła
    glPushMatrix()
    glDisable(GL_DEPTH_TEST)
    draw_sphere_with_texture(100.0, 50, 50, textures['stars'])
    glEnable(GL_DEPTH_TEST)
    glPopMatrix()

    # Renderowanie słońca
    glPushMatrix()
    glTranslatef(0.0, 0.0, 0.0)
    draw_sphere_with_texture(8.0, 50, 50, textures['sun'])
    glPopMatrix()

    # Renderowanie planet
    for planet in planets:
        angle = time * planet['speed']
        x = planet['distance'] * math.cos(angle)
        z = planet['distance'] * math.sin(angle)

        # Orbita
        glColor3f(1.0, 1.0, 1.0)
        render_orbit(planet['distance'])

        # Planeta
        glPushMatrix()
        glTranslatef(x, 0.0, z)
        draw_sphere_with_texture(planet['radius'], 50, 50, textures[planet['texture']])
        glPopMatrix()

    glFlush()


def mouse_motion_callback(window, x_pos, y_pos):
    global delta_x, delta_y, mouse_x_pos_old, mouse_y_pos_old, theta, phi

    if left_mouse_button_pressed:
        delta_x = x_pos - mouse_x_pos_old
        delta_y = y_pos - mouse_y_pos_old

        # Aktualizacja kątów theta i phi
        theta += delta_x * 0.2
        phi -= delta_y * 0.2

        # Ograniczenie phi do zakresu (-89, 89)
        phi = max(-89.0, min(89.0, phi))

    mouse_x_pos_old = x_pos
    mouse_y_pos_old = y_pos



def mouse_button_callback(window, button, action, mods):
    global left_mouse_button_pressed
    if button == GLFW_MOUSE_BUTTON_LEFT:
        left_mouse_button_pressed = (action == GLFW_PRESS)


def key_callback(window, key, scancode, action, mods):
    global camera_mode, active_planet_index
    if action == GLFW_PRESS:
        if key == GLFW_KEY_F:
            camera_mode = 'free'
        elif key == GLFW_KEY_P:
            camera_mode = 'planetary'
        elif key == GLFW_KEY_RIGHT:
            active_planet_index = (active_planet_index + 1) % len(planets)
        elif key == GLFW_KEY_LEFT:
            active_planet_index = (active_planet_index - 1) % len(planets)


def update_viewport(window, width, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(70.0, width / height, 1.0, 100.0)
    glViewport(0, 0, width, height)
    glMatrixMode(GL_MODELVIEW)


def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(800, 800, "Ruch planet - Tryby kamery", None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSetCursorPosCallback(window, mouse_motion_callback)
    glfwSetMouseButtonCallback(window, mouse_button_callback)
    glfwSetKeyCallback(window, key_callback)
    glfwSwapInterval(1)

    startup()
    while not glfwWindowShouldClose(window):
        render_scene(glfwGetTime())
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()
    glfwTerminate()


if __name__ == "__main__":
    main()
