import ctypes
import sys
from glfw.GLFW import *
import glm
import numpy
from OpenGL.GL import *
from OpenGL.GLU import *

# Zmienna do przechowywania programu renderowania i innych zasobów OpenGL
rendering_program = None
vertex_array_object = None
vertex_buffer = None
P_matrix = None

# Parametry kamery
camera_offset_x = 0.0
camera_offset_y = 0.0
camera_distance = 20.0
last_mouse_x = 0.0
last_mouse_y = 0.0
mouse_pressed = False


# Funkcja do kompilacji shaderów
def compile_shaders():
    vertex_shader_source = """
        #version 330 core

        layout(location = 0) in vec3 position;  // Pozycja wierzchołka
        layout(location = 1) in vec4 vertex_color;  // Kolor wierzchołka

        uniform mat4 M_matrix;  // Macierz modelu
        uniform mat4 V_matrix;  // Macierz widoku
        uniform mat4 P_matrix;  // Macierz projekcji

        out vec3 frag_color;  // Kolor w fragment shaderze
        out float y_position;  // Przesyłamy pozycję Y wierzchołka

        // Funkcja generująca losową liczbę
        float random(float seed) {
            return fract(sin(seed) * 43758.5453123);
        }

        void main(void) {
            // Translacja instancji
            int x = (gl_InstanceID % 10) - 4;  // Obliczamy pozycję wierzchołka w siatce
            int y = (gl_InstanceID / 10) - 4;
            mat4 translation_matrix = mat4(1.0);
            translation_matrix[3] = vec4(x * 2.0, y * 2.0, 0.0, 1.0);  // Translacja na podstawie ID instancji

            // Deformacja wierzchołków
            float deformation = random(gl_VertexID * 0.1 + gl_InstanceID * 0.5);
            vec3 new_position = position + vec3(deformation, deformation, deformation);  // Zmieniamy pozycję wierzchołka

            // Finalna pozycja wierzchołka
            gl_Position = P_matrix * V_matrix * M_matrix * translation_matrix * vec4(new_position, 1.0);

            // Przekazujemy kolor oraz pozycję Y do fragment shader
            frag_color = vertex_color.rgb;
            y_position = position.y;  // Przekazanie wysokości wierzchołka
        }
    """

    fragment_shader_source = """
        #version 330 core

        in vec3 frag_color;  // Odbieramy kolor z vertex shader
        in float y_position;  // Odbieramy wysokość wierzchołka
        out vec4 color;  // Wynikowy kolor dla fragmentu

        uniform float time;  // Czas używany do animacji

        void main(void) {
            // Kolory dla górnej i dolnej połowy, zmienne w pastelowych tonach
            vec3 color_bottom = vec3(0.5 + 0.5 * sin(time), 0.5 + 0.5 * cos(time + 1.0), 0.5 + 0.5 * sin(time + 2.0));
            vec3 color_top = vec3(0.5 + 0.5 * cos(time), 0.5 + 0.5 * sin(time + 1.0), 0.5 + 0.5 * cos(time + 2.0));

            // Przenikanie kolorów na podstawie Y wierzchołka
            float t = smoothstep(-0.5, 0.5, y_position);  // Używamy smoothstep dla płynnego przejścia
            vec3 blended_color = mix(color_bottom, color_top, t);  // Łączenie kolorów

            color = vec4(blended_color, 1.0);  // Finalny kolor
        }
    """

    # Kompilujemy vertex shader
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_shader_source)
    glCompileShader(vertex_shader)

    # Sprawdzanie błędów kompilacji vertex shader
    if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
        print("Vertex shader compilation error:")
        print(glGetShaderInfoLog(vertex_shader).decode("UTF-8"))

    # Kompilujemy fragment shader
    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_shader_source)
    glCompileShader(fragment_shader)

    # Sprawdzanie błędów kompilacji fragment shader
    if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
        print("Fragment shader compilation error:")
        print(glGetShaderInfoLog(fragment_shader).decode("UTF-8"))

    # Łączenie shaderów w program renderujący
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)

    # Sprawdzanie błędów linkowania programu
    if not glGetProgramiv(program, GL_LINK_STATUS):
        print("Program linking error:")
        print(glGetProgramInfoLog(program).decode("UTF-8"))

    # Usuwanie shaderów po zakończeniu kompilacji i linkowania
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    return program


# Funkcja inicjalizująca OpenGL i ustawiająca zasoby
def startup():
    global rendering_program
    global vertex_array_object
    global vertex_buffer

    # Wyświetlanie wersji OpenGL i GLSL
    print("OpenGL {}, GLSL {}\n".format(
        glGetString(GL_VERSION).decode('UTF-8').split()[0],
        glGetString(GL_SHADING_LANGUAGE_VERSION).decode('UTF-8').split()[0]
    ))

    # Ustawienie rozmiaru widoku i włączenie testu głębokości
    update_viewport(None, 800, 800)
    glEnable(GL_DEPTH_TEST)

    # Kompilowanie shaderów
    rendering_program = compile_shaders()

    # Tworzenie i wiązanie tablicy wierzchołków
    vertex_array_object = glGenVertexArrays(1)
    glBindVertexArray(vertex_array_object)

    # Dane wierzchołków (pozycje i kolory)
    vertex_data = numpy.array([
        -0.5, -0.5, -0.5, 0.8, 0.6, 0.7, 1.0,  # Pastelowy róż
        0.5, -0.5, -0.5, 0.6, 0.8, 0.7, 1.0,  # Pastelowy zielony
        0.5, 0.5, -0.5, 0.7, 0.8, 0.6, 1.0,  # Pastelowy żółty
        -0.5, 0.5, -0.5, 0.7, 0.6, 0.9, 1.0,  # Pastelowy niebieski
        -0.5, -0.5, 0.5, 0.8, 0.5, 0.5, 1.0,  # Pastelowy czerwony
        0.5, -0.5, 0.5, 0.7, 0.6, 0.5, 1.0,  # Pastelowy pomarańczowy
        0.5, 0.5, 0.5, 0.9, 0.7, 0.6, 1.0,  # Pastelowy fiolet
        -0.5, 0.5, 0.5, 0.6, 0.7, 0.8, 1.0  # Pastelowy turkusowy
    ], dtype='float32')

    # Indeksy do rysowania sześcianu
    index_data = numpy.array([
        0, 1, 2, 2, 3, 0,  # Front
        4, 5, 6, 6, 7, 4,  # Back
        0, 1, 5, 5, 4, 0,  # Bottom
        2, 3, 7, 7, 6, 2,  # Top
        1, 2, 6, 6, 5, 1,  # Right
        0, 3, 7, 7, 4, 0  # Left
    ], dtype='uint32')

    # Tworzenie buforów wierzchołków i indeksów
    vertex_buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

    index_buffer = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, index_buffer)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

    # Ustawienie wskaźników do danych wierzchołków
    stride = 7 * 4  # 7 floats per vertex, 4 bytes per float
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))
    glEnableVertexAttribArray(1)


# Funkcja do zamykania i czyszczenia zasobów
def shutdown():
    global rendering_program
    global vertex_array_object
    global vertex_buffer

    # Usuwanie zasobów OpenGL
    glDeleteProgram(rendering_program)
    glDeleteVertexArrays(1, [vertex_array_object])
    glDeleteBuffers(1, [vertex_buffer])


# Funkcja renderująca scenę
def render(time):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)  # Czyszczenie buforów

    global camera_offset_x, camera_offset_y, camera_distance

    # Tworzenie macierzy widoku (V_matrix)
    V_matrix = glm.mat4(1.0)
    V_matrix = glm.translate(V_matrix, glm.vec3(camera_offset_x, camera_offset_y, -camera_distance))

    # Tworzenie macierzy modelu (M_matrix)
    M_matrix = glm.rotate(glm.mat4(1.0), time, glm.vec3(1.0, 1.0, 0.0))

    glUseProgram(rendering_program)  # Użycie programu renderującego

    # Pobieranie lokalizacji uniformów
    M_location = glGetUniformLocation(rendering_program, "M_matrix")
    V_location = glGetUniformLocation(rendering_program, "V_matrix")
    P_location = glGetUniformLocation(rendering_program, "P_matrix")
    time_location = glGetUniformLocation(rendering_program, "time")

    # Ustawianie uniformów
    glUniformMatrix4fv(M_location, 1, GL_FALSE, glm.value_ptr(M_matrix))
    glUniformMatrix4fv(V_location, 1, GL_FALSE, glm.value_ptr(V_matrix))
    glUniformMatrix4fv(P_location, 1, GL_FALSE, glm.value_ptr(P_matrix))
    glUniform1f(time_location, time)  # Przekazanie czasu do shadera

    # Renderowanie instancji
    glDrawElementsInstanced(GL_TRIANGLES, 44, GL_UNSIGNED_INT, None, 100)


# Funkcja aktualizująca widok
def update_viewport(window, width, height):
    global P_matrix

    aspect = width / height
    P_matrix = glm.perspective(glm.radians(70.0), aspect, 0.1, 1000.0)
    glViewport(0, 0, width, height)


# Funkcje do obsługi interakcji z myszką i klawiaturą
def mouse_button_callback(window, button, action, mods):
    global mouse_pressed
    if button == GLFW_MOUSE_BUTTON_LEFT:
        mouse_pressed = action == GLFW_PRESS


def cursor_position_callback(window, xpos, ypos):
    global mouse_pressed, last_mouse_x, last_mouse_y, camera_offset_x, camera_offset_y
    if mouse_pressed:
        dx = xpos - last_mouse_x
        dy = ypos - last_mouse_y
        camera_offset_x += dx * 0.01
        camera_offset_y -= dy * 0.01
    last_mouse_x = xpos
    last_mouse_y = ypos


def scroll_callback(window, xoffset, yoffset):
    global camera_distance
    camera_distance -= yoffset
    camera_distance = max(5.0, min(50.0, camera_distance))  # Ograniczenie dystansu kamery


def keyboard_key_callback(window, key, scancode, action, mods):
    global camera_offset_x, camera_offset_y
    if action == GLFW_PRESS or action == GLFW_REPEAT:
        if key == GLFW_KEY_UP:
            camera_offset_y += 0.5
        elif key == GLFW_KEY_DOWN:
            camera_offset_y -= 0.5
        elif key == GLFW_KEY_LEFT:
            camera_offset_x -= 0.5
        elif key == GLFW_KEY_RIGHT:
            camera_offset_x += 0.5


# Główna funkcja programu
def main():
    glfwSetErrorCallback(lambda error, desc: print(f"GLFW Error {desc}"))

    # Inicjalizacja GLFW
    if not glfwInit():
        sys.exit(-1)

    # Ustawienia dla OpenGL
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3)
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3)

    window = glfwCreateWindow(800, 800, "Kwadraty", None, None)
    if not window:
        glfwTerminate()
        sys.exit(-1)

    # Ustawienie kontekstu i callbacków
    glfwMakeContextCurrent(window)
    glfwSetFramebufferSizeCallback(window, update_viewport)
    glfwSetMouseButtonCallback(window, mouse_button_callback)
    glfwSetCursorPosCallback(window, cursor_position_callback)
    glfwSetScrollCallback(window, scroll_callback)
    glfwSetKeyCallback(window, keyboard_key_callback)
    glfwSwapInterval(1)

    # Uruchomienie inicjalizacji i głównej pętli
    startup()
    while not glfwWindowShouldClose(window):
        render(glfwGetTime())  # Renderowanie na podstawie czasu
        glfwSwapBuffers(window)
        glfwPollEvents()
    shutdown()

    glfwTerminate()  # Zakończenie działania programu


if __name__ == '__main__':
    main()
