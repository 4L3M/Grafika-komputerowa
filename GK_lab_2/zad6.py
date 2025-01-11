#!/usr/bin/env python3
import sys
import math
from PIL import Image
from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *
import os

yaw = 0.0
pitch = 0.0

KEY_STATE = {
    'UP': False,
    'DOWN': False,
    'LEFT': False,
    'RIGHT': False
}

textures = {}

def key_callback(window, key, scancode, action, mods):
    global KEY_STATE
    if key == GLFW_KEY_UP:
        KEY_STATE['UP'] = action != GLFW_RELEASE
    elif key == GLFW_KEY_DOWN:
        KEY_STATE['DOWN'] = action != GLFW_RELEASE
    elif key == GLFW_KEY_LEFT:
        KEY_STATE['LEFT'] = action != GLFW_RELEASE
    elif key == GLFW_KEY_RIGHT:
        KEY_STATE['RIGHT'] = action != GLFW_RELEASE

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
            sys.exit(-1)  # Wyjście, jeśli plik tekstury nie istnieje

        texture = glGenTextures(1)
        textures[key] = texture
        glBindTexture(GL_TEXTURE_2D, texture)
        image = Image.open(file)
        #image = image.transpose(Image.)  # Obrót o 90 stopni
        image_data = image.convert("RGB").tobytes()
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_REPLACE)
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
    gluQuadricDrawStyle(quadric, GLU_FILL)
    gluQuadricNormals(quadric, GLU_SMOOTH)
    gluQuadricTexture(quadric, GL_TRUE)

    # Obrót tekstury o 90 stopni (zmiana współrzędnych u, v na v, 1-u)
    glPushMatrix()
    glRotatef(90, 1.0, 0.0, 0.0)  # Obrót wokół osi Z o 90 stopni

    gluSphere(quadric, radius, slices, stacks)
    gluDeleteQuadric(quadric)
    glPopMatrix()

    # # TRIANGLE STRIPS
    # glBindTexture(GL_TEXTURE_2D, texture)  # Powiązanie tekstury ze sferą
    #
    # for i in range(stacks):  # Pętla po szerokości geograficznej (phi)
    #     phi1 = math.pi * i / stacks
    #     phi2 = math.pi * (i + 1) / stacks
    #
    #     glBegin(GL_TRIANGLE_STRIP)  # Rozpoczęcie pasma
    #     for j in range(slices + 1):  # Pętla po długości geograficznej (theta)
    #         theta = 2 * math.pi * j / slices
    #
    #         # Wierzchołki dla dolnego pasa (phi1)
    #         x1 = radius * math.sin(phi1) * math.cos(theta)
    #         y1 = radius * math.sin(phi1) * math.sin(theta)
    #         z1 = radius * math.cos(phi1)
    #         u1 = j / slices
    #         v1 = i / stacks
    #
    #         # Wierzchołki dla górnego pasa (phi2)
    #         x2 = radius * math.sin(phi2) * math.cos(theta)
    #         y2 = radius * math.sin(phi2) * math.sin(theta)
    #         z2 = radius * math.cos(phi2)
    #         u2 = j / slices
    #         v2 = (i + 1) / stacks
    #
    #         # Dodanie dolnego wierzchołka
    #         glTexCoord2f(u1, v1)  # Współrzędne tekstury
    #         glNormal3f(x1 / radius, y1 / radius, z1 / radius)  # Normalne
    #         glVertex3f(x1, y1, z1)  # Pozycja wierzchołka
    #
    #         # Dodanie górnego wierzchołka
    #         glTexCoord2f(u2, v2)  # Współrzędne tekstury
    #         glNormal3f(x2 / radius, y2 / radius, z2 / radius)  # Normalne
    #         glVertex3f(x2, y2, z2)  # Pozycja wierzchołka
    #     glEnd()  # Zamknięcie pasma


def render_background():
    """Renderuje tło jako teksturowany kwadrat."""
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

def render_orbit(radius):
    glBegin(GL_LINE_LOOP)
    glColor3f(1.0, 1.0, 1.0)
    for angle in range(0, 360, 5):
        x = radius * math.cos(math.radians(angle))
        z = radius * math.sin(math.radians(angle))
        glVertex3f(x, 0.0, z)
    glEnd()

def axes():
    glDisable(GL_TEXTURE_2D)  # Wyłącz tekstury przed rysowaniem osi

    glBegin(GL_LINES)

    glColor3f(1.0, 0.0, 1.0)  # X-axis
    glVertex3f(-10.0, 0.0, 0.0)
    glVertex3f(10.0, 0.0, 0.0)

    glColor3f(0.5, 1.0, 0.0)  # Y-axis
    glVertex3f(0.0, -10.0, 0.0)
    glVertex3f(0.0, 10.0, 0.0)

    glColor3f(0.0, 1.0, 1.0)  # Z-axis
    glVertex3f(0.0, 0.0, -10.0)
    glVertex3f(0.0, 0.0, 10.0)

    glEnd()

    glEnable(GL_TEXTURE_2D)  # Włącz tekstury po narysowaniu osi


def render(time):
    global yaw, pitch

    # Obsługa klawiatury
    if KEY_STATE['UP']:
        pitch += 1.0
    if KEY_STATE['DOWN']:
        pitch -= 1.0
    if KEY_STATE['LEFT']:
        yaw -= 1.0
    if KEY_STATE['RIGHT']:
        yaw += 1.0

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    gluLookAt(0.0, 15.0, 30.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    # Obrót sceny
    glRotatef(pitch, 1.0, 0.0, 0.0)
    glRotatef(yaw, 0.0, 1.0, 0.0)

    # Renderowanie tła
    glPushMatrix()
    render_background()
    glPopMatrix()

    # Rysowanie osi układu współrzędnych
    axes()

    # Słońce
    glPushMatrix()
    draw_sphere_with_texture(2.0, 50, 50, textures['sun'])
    glPopMatrix()

    # Ziemia
    glPushMatrix()
    earth_orbit_radius = 10.0
    earth_angle = (time * 20) % 360
    glRotatef(earth_angle, 0.0, 1.0, 0.0)
    glTranslatef(earth_orbit_radius, 0.0, 0.0)

    glPushMatrix()
    glRotatef((time * 50) % 360, 0.0, 1.0, 0.0)
    draw_sphere_with_texture(1.0, 50, 50, textures['earth'])
    glPopMatrix()

    # Księżyc
    glPushMatrix()
    moon_orbit_radius = 2.5
    moon_angle = (time * 100) % 360
    glRotatef(moon_angle, 0.0, 1.0, 0.0)
    glTranslatef(moon_orbit_radius, 0.0, 0.0)
    draw_sphere_with_texture(0.3, 50, 50, textures['moon'])
    glPopMatrix()

    glPopMatrix()

    # Inne planety
    planets = [
        (5.0, 0.5, textures['mars'], 40),
        (15.0, 1.5, textures['jupiter'], 15)
    ]

    for orbit_radius, radius, texture, speed in planets:
        glPushMatrix()
        planet_angle = (time * speed) % 360
        glRotatef(planet_angle, 0.0, 1.0, 0.0)
        glTranslatef(orbit_radius, 0.0, 0.0)

        glRotatef((time * 50) % 360, 0.0, 1.0, 0.0)
        draw_sphere_with_texture(radius, 50, 50, texture)
        glPopMatrix()

    # Orbity
    for orbit_radius, _, _, _ in [(earth_orbit_radius, 0, 0, 0)] + planets:
        render_orbit(orbit_radius)

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

    gluPerspective(60.0, aspect_ratio, 1.0, 100.0)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def main():
    if not glfwInit():
        sys.exit(-1)

    window = glfwCreateWindow(800, 800, "Zad. 5.", None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSetKeyCallback(window, key_callback)
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
