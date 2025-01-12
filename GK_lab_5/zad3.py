#!/usr/bin/env python3
import sys
from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image

viewer = [0.0, 0.0, 10.0]  # Pozycja kamery (x, y, z)
theta = 0.0
phi = 0.0
pix2angle = 1.0

left_mouse_button_pressed = 0
mouse_x_pos_old = 0
mouse_y_pos_old = 0
delta_x = 0
delta_y = 0

mat_ambient = [1.0, 1.0, 1.0, 1.0]
mat_diffuse = [1.0, 1.0, 1.0, 1.0]
mat_specular = [1.0, 1.0, 1.0, 1.0]
mat_shininess = 20.0

mat_inside_color = [0.6, 0.6, 0.6, 1.0]  # Możesz zmienić na dowolny kolor

light_ambient = [0.1, 0.1, 0.0, 1.0]
light_diffuse = [0.9, 0.9, 1.0, 1.0]
light_specular = [1.0, 1.0, 1.0, 1.0]
light_position = [0.0, 0.0, 10, 1.0]
light_position_bottom = [0.0, 0.0, -20.0, 1.0]

att_constant = 1.0
att_linear = 0.05
att_quadratic = 0.001

x_key_pressed = 1

# Nowe zmienne do obsługi ruchu góra-dół
move_up_down = 0.0

# Zmienna do przechowywania tekstur
textures = []
current_texture = 0  # Zmienna przechowująca indeks aktualnej tekstury

def load_texture(file_path):
    image = Image.open(file_path)
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    glTexImage2D(
        GL_TEXTURE_2D, 0, 3, image.size[0], image.size[1], 0,
        GL_RGB, GL_UNSIGNED_BYTE, image.tobytes("raw", "RGB", 0, -1)
    )
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    return texture

def startup():
    global textures
    update_viewport(None, 400, 400)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glEnable(GL_DEPTH_TEST)

    # Ładujemy tekstury
    textures.append(load_texture("tekstura.tga"))
    textures.append(load_texture("P6_t.tga"))

    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, mat_shininess)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, att_constant)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, att_linear)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, att_quadratic)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialf(GL_FRONT, GL_SHININESS, mat_shininess)
    glLightfv(GL_LIGHT1, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT1, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT1, GL_POSITION, light_position_bottom)
    glLightf(GL_LIGHT1, GL_CONSTANT_ATTENUATION, att_constant)
    glLightf(GL_LIGHT1, GL_LINEAR_ATTENUATION, att_linear)
    glLightf(GL_LIGHT1, GL_QUADRATIC_ATTENUATION, att_quadratic)
    glShadeModel(GL_SMOOTH)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT1)

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_CULL_FACE)
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

def shutdown():
    pass

def render(time):
    global theta, move_up_down, current_texture

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Zaktualizowana pozycja kamery
    gluLookAt(viewer[0], viewer[1] + move_up_down, viewer[2], 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    glRotatef(theta, 0.0, 1.0, 0.0)

    # Wybór tekstury
    glBindTexture(GL_TEXTURE_2D, textures[current_texture])

    # Podstawa ostrosłupa
    glBegin(GL_TRIANGLES)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-5.0, -5.0, 0.0)
    glTexCoord2f(0, 1.0)
    glVertex3f(-5.0, 5.0, 0.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(5.0, -5.0, 0.0)
    glEnd()

    glBegin(GL_TRIANGLES)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-5.0,  5.0, 0.0)
    glTexCoord2f(1, 1.0)
    glVertex3f(5.0, 5.0, 0.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(5.0, -5.0, 0.0)
    glEnd()

    ############################
    # Zmieniamy materiał na kolor dla wewnętrznej strony
    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_inside_color)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_inside_color)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_inside_color)
    glMaterialf(GL_FRONT, GL_SHININESS, 20.0)

    # Podstawa ostrosłupa (wewnątrz) - bez tekstury, kolor wewnętrznej ściany
    glBegin(GL_POLYGON)
    glVertex3d(5, 5, 0)
    glVertex3d(-5, 5, 0)
    glVertex3d(-5, -5, 0)
    glVertex3d(5, -5, 0)
    glEnd()
    ############################

    glBegin(GL_TRIANGLES)
    glTexCoord2f(0, 1.0)
    glVertex3f(-5.0, 5.0, 0.0)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-5.0, -5.0, 0.0)
    glTexCoord2f(0.5, 0.5)
    glVertex3f(0.0, 0.0, 5.0)
    glEnd()

    glBegin(GL_TRIANGLES)
    glTexCoord2f(0.0, 0.0)
    glVertex3f(-5.0,  -5.0, 0.0)
    glTexCoord2f(1.0, 0.0)
    glVertex3f(5.0, -5.0, 0.0)
    glTexCoord2f(0.5, 0.5)
    glVertex3f(0.0, 0.0, 5.0)
    glEnd()

    # Klawisz 'x' włącza i wyłącza ukrywanie ściany bocznej
    if x_key_pressed:
        glBegin(GL_TRIANGLES)
        glTexCoord2f(1.0, 0.0)
        glVertex3f(5.0,  -5.0, 0.0)
        glTexCoord2f(1.0, 1.0)
        glVertex3f(5.0, 5.0, 0.0)
        glTexCoord2f(0.5, 0.5)
        glVertex3f(0.0, 0.0, 5.0)
        glEnd()

    glBegin(GL_TRIANGLES)
    glTexCoord2f(1.0, 1.0)
    glVertex3f(5.0,  5.0, 0.0)
    glTexCoord2f(0.0, 1.0)
    glVertex3f(-5.0, 5.0, 0.0)
    glTexCoord2f(0.5, 0.5)
    glVertex3f(0.0, 0.0, 5.0)
    glEnd()

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
    global x_key_pressed, move_up_down, current_texture
    if key == GLFW_KEY_ESCAPE and action == GLFW_PRESS:
        glfwSetWindowShouldClose(window, GLFW_TRUE)
    if key == GLFW_KEY_X and action == GLFW_PRESS:
        x_key_pressed = 1 - x_key_pressed  # Toggle x_key_pressed
    if key == GLFW_KEY_W and action == GLFW_PRESS:  # Poruszanie w górę
        move_up_down += 1.0
    if key == GLFW_KEY_S and action == GLFW_PRESS:  # Poruszanie w dół
        move_up_down -= 1.0
    if key == GLFW_KEY_T and action == GLFW_PRESS:  # Przełączanie tekstury
        current_texture = 1 - current_texture  # Toggle texture

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
