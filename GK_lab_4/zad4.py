import sys
import math
from glfw.GLFW import *
from OpenGL.GL import *
from OpenGL.GLU import *

# View position
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

# Light properties
light_ambient = [0.1, 0.1, 0.1, 1.0]
light_diffuse = [0.8, 0.8, 0.8, 1.0]
light_specular = [1.0, 1.0, 1.0, 1.0]
light_position = [0.0, 0.0, 10.0, 1.0]

# Function to initialize OpenGL
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
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)

# Function to calculate normal for a point on the surface
def calculate_normal(x, y, z):
    length = math.sqrt(x**2 + y**2 + z**2)
    return [x / length, y / length, z / length]

# Function to render the egg model
def render(time):
    global theta, phi

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    # Look-at camera setup
    gluLookAt(viewer[0], viewer[1], viewer[2], 0.0, 0.0, 0.0, 0.0, 1.0, 0.0)

    # Visualize the light source position
    glPushMatrix()  # Save the current matrix before transforming it
    glTranslatef(light_position[0], light_position[1], light_position[2])
    quadric = gluNewQuadric()
    gluQuadricDrawStyle(quadric, GLU_LINE)
    gluSphere(quadric, 0.5, 6, 5)
    gluDeleteQuadric(quadric)
    glPopMatrix()  # Restore the previous matrix state after rendering light

    # Rotate the egg model
    glPushMatrix()  # Save the current matrix before transforming the egg
    glRotatef(theta, 0.0, 1.0, 0.0)

    slices = 20
    stacks = 20
    radius_x = 3.0
    radius_y = 3.0
    radius_z = 4.0

    for i in range(slices):
        lat0 = math.pi * (-0.5 + float(i) / slices)
        lat1 = math.pi * (-0.5 + float(i + 1) / slices)

        for j in range(stacks):
            lon0 = 2 * math.pi * float(j) / stacks
            lon1 = 2 * math.pi * float(j + 1) / stacks

            # Calculate the vertex positions
            x0 = radius_x * math.cos(lat0) * math.cos(lon0)
            y0 = radius_y * math.sin(lat0)
            z0 = radius_z * math.cos(lat0) * math.sin(lon0)

            x1 = radius_x * math.cos(lat1) * math.cos(lon0)
            y1 = radius_y * math.sin(lat1)
            z1 = radius_z * math.cos(lat1) * math.sin(lon0)

            x2 = radius_x * math.cos(lat1) * math.cos(lon1)
            y2 = radius_y * math.sin(lat1)
            z2 = radius_z * math.cos(lat1) * math.sin(lon1)

            x3 = radius_x * math.cos(lat0) * math.cos(lon1)
            y3 = radius_y * math.sin(lat0)
            z3 = radius_z * math.cos(lat0) * math.sin(lon1)

            # Calculate the normal vectors
            normal0 = calculate_normal(x0, y0, z0)
            normal1 = calculate_normal(x1, y1, z1)
            normal2 = calculate_normal(x2, y2, z2)
            normal3 = calculate_normal(x3, y3, z3)

            # Draw the first triangle
            glBegin(GL_TRIANGLES)
            glNormal3f(normal0[0], normal0[1], normal0[2])
            glVertex3f(x0, y0, z0)

            glNormal3f(normal1[0], normal1[1], normal1[2])
            glVertex3f(x1, y1, z1)

            glNormal3f(normal2[0], normal2[1], normal2[2])
            glVertex3f(x2, y2, z2)
            glEnd()

            # Draw the second triangle
            glBegin(GL_TRIANGLES)
            glNormal3f(normal0[0], normal0[1], normal0[2])
            glVertex3f(x0, y0, z0)

            glNormal3f(normal2[0], normal2[1], normal2[2])
            glVertex3f(x2, y2, z2)

            glNormal3f(normal3[0], normal3[1], normal3[2])
            glVertex3f(x3, y3, z3)
            glEnd()

    glPopMatrix()  # Restore the matrix state after rendering the egg

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
    glfwTerminate()

if __name__ == '__main__':
    main()
