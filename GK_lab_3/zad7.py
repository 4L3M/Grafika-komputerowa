#!/usr/bin/env python3
import math
import sys
from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *
from math import cos, sin, pi, fmod
import os
from PIL import Image

# współrzędne sferyczne
viewer = [0.0, 0.0, 10.0]

# katy obrotu kamery
yaw = 0.0
pitch = 0.0


R = 10.0  # Promień sfery, po której porusza się kamera
theta = 0.0  # Obrót wokół osi Y
phi = 0.0    # Obrót wokół osi X
pix2angle = 1.0

# slownik tekstur
textures = {}

# Lista planet
planets_data = [
    {'name': 'Earth', 'orbit_radius': 10.0, 'speed': 20.0, 'size': 1.0},
    {'name': 'Mars', 'orbit_radius': 5.0, 'speed': 40.0, 'size': 0.5},
    {'name': 'Jupiter', 'orbit_radius': 15.0, 'speed': 15.0, 'size': 1.5}
]

# domyślna planeta i tryb widoku
selected_planet = 0  # Domyślnie z Ziemii
mode = 0 # domyślnie tryb z przestrzeni

left_mouse_button_pressed = 0
right_mouse_button_pressed = 0  # zmienna do obsługi prawego przycisku myszy
mouse_x_pos_old = 0
mouse_y_pos_old = 0
delta_x = 0
delta_y = 0

# Tryb: 0 - poruszanie kamerą, 1 - obracanie obiektem
mode = 0

# Funkcja ładująca tekstury
def load_textures():
    global textures
    texture_files = {
        'sun': 'textures/sun.jpg',
        'earth': 'textures/earth.jpg',
        'moon': 'textures/moon.jpg',
        'mars': 'textures/mars.jpg',
        'jupiter': 'textures/jupiter.jpg',
        'stars': 'textures/stars.jpg'  # Tekstura tła
    }

    for key, file in texture_files.items():
        if not os.path.exists(file):
            print(f"Error: Texture file '{file}' not found!")
            continue  # Przejdź do następnego pliku zamiast kończyć program

        print(f"Loading texture: {file}")  # Debug

        texture = glGenTextures(1) # identyfikator tekstury
        textures[key] = texture
        glBindTexture(GL_TEXTURE_2D, texture) # wiązanie tekstury
        image = Image.open(file) # wczytanie obrazu
        #image = image.transpose(Image.)  # Obrót o 90 stopni
        image_data = image.convert("RGB").tobytes()
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

# Funckja rysująca sferę z teksturą
def draw_sphere_with_texture(radius, slices, stacks, texture):
    glBindTexture(GL_TEXTURE_2D, texture)
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_FILL)
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluQuadricTexture(quadric, GL_TRUE)

    # Obrót tekstury o 90 stopni
    glPushMatrix()
    glRotatef(90, 1.0, 0.0, 0.0)  # Obrót wokół osi Z o 90 stopni

    gluSphere(quadric, radius, slices, stacks)
    gluDeleteQuadric(quadric)
    glPopMatrix()

# Renderuje tło jako teksturowany kwadrat
def render_background():
    glBindTexture(GL_TEXTURE_2D, textures['stars'])
    glBegin(GL_QUADS)

    glTexCoord2f(0.0, 0.0)
    glVertex3f(-50.0, -50.0, -50.0)

    glTexCoord2f(1.0, 0.0)
    glVertex3f(50.0, -50.0, -50.0)

    glTexCoord2f(1.0, 1.0)
    glVertex3f(50.0, 50.0, -50.0)

    glTexCoord2f(0.0, 1.0)
    glVertex3f(-50.0, 50.0, -50.0)

    glEnd()

def render_orbit(radius): # orbity
    glBegin(GL_LINE_LOOP)
    glColor3f(1.0, 1.0, 1.0)
    for angle in range(0, 360, 5):
        x = radius * math.cos(math.radians(angle))
        z = radius * math.sin(math.radians(angle))
        glVertex3f(x, 0.0, z)
    glEnd()

def startup():
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_TEXTURE_2D)
    load_textures()  # Ładowanie tekstur

def shutdown():
    pass

def axes():
    glDisable(GL_TEXTURE_2D)  # Wyłącz tekstury przed rysowaniem osi

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

    glEnable(GL_TEXTURE_2D)  # Włącz tekstury po narysowaniu osi

def render(time):
    global theta, phi, R, yaw, pitch

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    if mode == 0:  # Tryb wolnego obserwatora
        # Obliczanie pozycji kamery w układzie sferycznym
        xeye = R * cos(phi * pi / 180) * cos(theta * pi / 180)
        yeye = R * sin(phi * pi / 180)
        zeye = R * cos(phi * pi / 180) * sin(theta * pi / 180)

        gluLookAt(float(xeye), float(yeye), float(zeye), 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

        if left_mouse_button_pressed:
            theta += delta_x * pix2angle  # Obrót wokół osi Y
            phi += delta_y * pix2angle    # Obrót wokół osi X

            # Ograniczenie kąta phi
            phi = max(-89.0, min(89.0, phi))
            # Ograniczenie theta do przedziału [0, 360)
            theta = fmod(theta, 360.0)

        if right_mouse_button_pressed:
            R += delta_y * 0.01  # Zmiana promienia na podstawie ruchu myszy
            R = max(0.5, min(20.0, R))  # Ograniczenie promienia

    elif mode == 2:  # Tryb obserwacji z powierzchni planety
        planet = planets_data[selected_planet]
        orbit_radius = planet['orbit_radius']
        speed = planet['speed']
        size = planet['size']

        # Pozycja planety
        angle = (time * speed) % 360
        planet_x = orbit_radius * cos(angle * pi / 180)
        planet_z = orbit_radius * sin(angle * pi / 180)

        # Ustawienie kamery na powierzchni planety
        # Kamera znajduje się na powierzchni planety, patrzy na Układ Słoneczny
        camera_x = planet_x + size * cos(phi * pi / 180) * cos(theta * pi / 180)
        camera_y = size * sin(phi * pi / 180)  # Wysokość kamery
        camera_z = planet_z + size * cos(phi * pi / 180) * sin(theta * pi / 180)

        # Ustawienie kamery (patrzymy na słońce, czyli na punkt (0, 0, 0))
        gluLookAt(camera_x, camera_y, camera_z, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

        # Obracanie kamery wokół planety
        if left_mouse_button_pressed:
            theta += delta_x * pix2angle  # Obrót wokół osi Y
            phi += delta_y * pix2angle    # Obrót wokół osi X

            # Ograniczenie kąta phi
            phi = max(-89.0, min(89.0, phi))
            # Ograniczenie theta do przedziału [0, 360)
            theta = fmod(theta, 360.0)

    # Renderowanie reszty sceny
    render_background()
    axes()

    # Słońce
    glPushMatrix()
    draw_sphere_with_texture(2.0, 50, 50, textures['sun'])
    glPopMatrix()

    # Renderowanie planet
    for planet in planets_data:
        orbit_radius = planet['orbit_radius']
        angle = (time * planet['speed']) % 360
        planet_x = orbit_radius * cos(angle * pi / 180)
        planet_z = orbit_radius * sin(angle * pi / 180)

        glPushMatrix()
        glTranslatef(planet_x, 0.0, planet_z)
        glRotatef((time * 50) % 360, 0.0, 1.0, 0.0)
        draw_sphere_with_texture(planet['size'], 50, 50, textures[planet['name'].lower()])
        glPopMatrix()

    glFlush()
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
    global mode, selected_planet

    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)

    if key == GLFW_KEY_S and action == GLFW_PRESS:  # Przełącz na tryb wolnego obserwatora
        mode = 0

    if key == GLFW_KEY_P and action == GLFW_PRESS:  # Przełącz na tryb obserwacji z planety
        mode = 2

    if mode == 2 and action == GLFW_PRESS:  # Przełączanie planet
        if key == GLFW_KEY_1:
            selected_planet = 0  # Ziemia
        elif key == GLFW_KEY_2:
            selected_planet = 1  # Mars
        elif key == GLFW_KEY_3:
            selected_planet = 2  # Jowisz

def mouse_motion_callback(window, x_pos, y_pos):
    global delta_x, delta_y
    global mouse_x_pos_old, mouse_y_pos_old

    delta_x = x_pos - mouse_x_pos_old
    delta_y = y_pos - mouse_y_pos_old

    mouse_x_pos_old = x_pos
    mouse_y_pos_old = y_pos

def mouse_button_callback(window, button, action, mods):
    global left_mouse_button_pressed, right_mouse_button_pressed

    if button == GLFW_MOUSE_BUTTON_LEFT:
        if action == GLFW_PRESS:
            left_mouse_button_pressed = 1
        else:
            left_mouse_button_pressed = 0

    if button == GLFW_MOUSE_BUTTON_RIGHT:
        if action == GLFW_PRESS:
            right_mouse_button_pressed = 1
        else:
            right_mouse_button_pressed = 0

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
