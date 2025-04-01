import math
from typing import Annotated
from pydantic import BaseModel, AfterValidator, computed_field
import numpy as np
import random
import pytest
from OpenGL.GL import *
import glfw

MAX_ATTEMPTS_PER_ROOT = 500
MAX_ITERATIONS = 10 * MAX_ATTEMPTS_PER_ROOT

def drop_ending_zeros(coefficients: list[complex]):
    index = len(coefficients) - 1
    while index >= 0 and coefficients[index] == 0:
        index -= 1
    return coefficients[:index+1]

COLORS = [
	[1, 0, 0],
	[0, 1, 0],
	[0, 0, 1],
	[0.7, 0.7, 0],
	[1, 0.6, 0],
	[0, 1, 1],
	[1, 0, 1],
	[0.6, 0.6, 0.6],
]
NUM_SIDES = 50

class CircleParams(BaseModel):
    x_center: float
    y_center: float
    radius: float
    num_sides: int
    r: float
    g: float
    b: float

class ComplexPolynomial(BaseModel):
    coefficients: Annotated[list[complex], AfterValidator(drop_ending_zeros)]

    @computed_field
    @property
    def degree(self) -> int:
        return len(self.coefficients) - 1
    
    def divide_in_place(self, root: complex):
        degree = self.degree
        for n in range(degree, 0, -1):
            self.coefficients[n - 1] += root * self.coefficients[n]
        
        self.coefficients[:degree] = self.coefficients[1:degree + 1]
        self.coefficients.pop()

class Roots(BaseModel):
    roots: list[complex]
    length: int

    @computed_field
    @property
    def degree(self) -> int:
        return len(self.roots) - 1


def create_circle(params: CircleParams) -> int:
    num_vertices = params.num_sides + 2
    vertices = [params.x_center, params.y_center, 0, params.r, params.g, params.b]

    for i in range(1, num_vertices):
        angle = i * 2.0 * np.pi / params.num_sides
        x = params.x_center + params.radius * np.cos(angle)
        y = params.y_center + params.radius * np.sin(angle)
        vertices.extend([x, y, 0, params.r, params.g, params.b])
    
    vertices = np.array(vertices, dtype=np.float32)
    
    VAO = glGenVertexArrays(1)
    VBO = glGenBuffers(1)
    
    glBindVertexArray(VAO)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(0))
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * 4, ctypes.c_void_p(3 * 4))
    glEnableVertexAttribArray(0)
    glEnableVertexAttribArray(1)
    
    glBindVertexArray(0)
    
    return VAO

def create_circles(roots: list[Roots]) -> list[int]:
    VAOs: list[int] = []

    for root_set in roots:
        if root_set.degree < 8:
            color = COLORS[root_set.degree]
        else:
            color = [1, 1, 1]
        for root in root_set.roots:
            circle_parameters = CircleParams(
                x_center=root.real,
                y_center=root.imag,
                radius=math.sqrt(root_set.length),
                num_sides=NUM_SIDES,
                r=color[0],
                g=color[1],
                b=color[2]
            )

            VAOs.append(create_circle(circle_parameters))

    return VAOs

def compile_shader(source: str, shader_type: int) -> int:
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    
    if glGetShaderiv(shader, GL_COMPILE_STATUS) == GL_FALSE:
        log_length = glGetShaderiv(shader, GL_INFO_LOG_LENGTH)
        log = glGetShaderInfoLog(shader).decode('utf-8')
        raise RuntimeError(f"Failed to compile shader: {log}")
    
    return shader

def new_program(vertex_shader_source: str, fragment_shader_source: str) -> int:
    vertex_shader = compile_shader(vertex_shader_source, GL_VERTEX_SHADER)
    fragment_shader = compile_shader(fragment_shader_source, GL_FRAGMENT_SHADER)
    
    program = glCreateProgram()
    glAttachShader(program, vertex_shader)
    glAttachShader(program, fragment_shader)
    glLinkProgram(program)
    
    if glGetProgramiv(program, GL_LINK_STATUS) == GL_FALSE:
        log = glGetProgramInfoLog(program).decode('utf-8')
        raise RuntimeError(f"Failed to link program: {log}")
    
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)
    
    return program

def random_complex(scale=2):
    return complex(random.uniform(-scale / 2, scale / 2), random.uniform(-scale / 2, scale / 2))

def find_roots(polynomial: ComplexPolynomial) -> tuple[bool, list[complex]]:
    roots: list[complex] = []

    while (degree := polynomial.degree) > 0:
        if degree == 1:
            root = -polynomial.coefficients[0] / polynomial.coefficients[1]
            roots.append(root)
            break
        
        candidate_root = random_complex()
        iteration, reset_counter = 0, 0
        
        while True:
            if reset_counter == MAX_ATTEMPTS_PER_ROOT:
                candidate_root = random_complex()
                reset_counter = 0
            else:
                reset_counter += 1
            
            if iteration >= MAX_ITERATIONS:
                return False, None
            iteration += 1
            
            previous_root = candidate_root
            polynomial_value, derivative_value, power_term = 0, 0, 1
            
            for n in range(degree):
                polynomial_value += power_term * polynomial.coefficients[n]
                derivative_value += power_term * polynomial.coefficients[n + 1] * (n + 1)
                power_term *= candidate_root
            
            polynomial_value += power_term * polynomial.coefficients[degree]
            candidate_root -= polynomial_value / derivative_value
            
            if abs(previous_root - candidate_root) ** 2 <= 1e-20:
                break
        
        # The candidate root is an approximate root according to the stopping criteria
        roots.append(candidate_root)

        # Apply synthetic division
        polynomial.divide_in_place(candidate_root)
    
    return True, roots

def compute_all_roots(max_length: int) -> list[Roots]:
    roots: list[Roots] = []
    
    # The length of a polynomial is a sum of the absolute values of its coefficients.
    # Iterating over integer polynomials of a particular length gives us a way to enumerate
    # these polynomials, since there are finitely many such polynomials.
    for length in range(2, max_length + 1):
        positive_coefficients = [0] * length
        
        # bits is an integer that encodes a bit vector.
        for bits in range((1 << (length - 1)) - 1, -1, -2):
            positive_coefficients[0] = 0
            degree = 0
            
            for shift in range(length - 2, -1, -1):
                if (bits >> shift) & 1:
                    positive_coefficients[degree] += 1
                else:
                    degree += 1
                    positive_coefficients[degree] = 0
                
            if degree <= 0:
                continue
                
            num_non_zero = sum(1 for i in range(degree + 1) if positive_coefficients[i] != 0)
            if num_non_zero == 0:
                continue
            
            for sign_bits in range((1 << (num_non_zero - 1)) - 1, -1, -1):
                coefficients = [0] * (degree + 1)
                sign_pointer = 1
                
                for c in range(degree, -1, -1):
                    coef = complex(float(positive_coefficients[c]), 0)
                    if positive_coefficients[c] == 0 or c == degree:
                        coefficients[c] = coef
                    else:
                        coefficients[c] = coef if sign_bits & sign_pointer else -coef
                        sign_pointer <<= 1
                
                polynomial = ComplexPolynomial(coefficients=coefficients)
                did_converge, root_set = find_roots(polynomial)
                if did_converge:
                    roots.append(Roots(
                        roots=root_set,
                        length=length
                    ))
    
    return roots

def test_quadratic():
    polynomial = ComplexPolynomial(coefficients=[complex(-3, 0), complex(2, 0), complex(1, 0)])
    success, roots = find_roots(polynomial)
    assert success
    assert pytest.approx(roots[0].real, rel=1e-5) == 1.0
    assert pytest.approx(roots[1].real, rel=1e-5) == -3.0

def test_cubic():
    polynomial = ComplexPolynomial(coefficients=[complex(-6, 0), complex(11, 0), complex(-6, 0), complex(1, 0)])
    success, roots = find_roots(polynomial)
    assert success
    expected_roots = [1.0, 2.0, 3.0]
    root_reals = sorted([root.real for root in roots])
    for root, expected in zip(root_reals, expected_roots):
        assert pytest.approx(root, rel=1e-5) == expected

def main():
    if not glfw.init():
        raise RuntimeError("Failed to initialize GLFW")
    
    glfw.window_hint(glfw.RESIZABLE, glfw.FALSE)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
    
    window = glfw.create_window(1000, 1000, "Algebraics", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Failed to create GLFW window")
    
    glfw.make_context_current(window)
    
    if not glGetString(GL_VERSION):
        glfw.terminate()
        raise RuntimeError("Failed to initialize OpenGL")
    
    vertex_shader_source = """
    #version 330 core
    layout (location = 0) in vec3 aPos;
    layout (location = 1) in vec3 aColor;
    out vec3 ourColor;
    void main() {
        gl_Position = vec4(aPos, 1.0);
        ourColor = aColor;
    }
    """
    
    fragment_shader_source = """
    #version 330 core
    out vec4 FragColor;
    in vec3 ourColor;
    void main() {
        FragColor = vec4(ourColor, 1.0);
    }
    """
    
    program = new_program(vertex_shader_source, fragment_shader_source)
    
    glEnable(GL_BLEND)
    glBlendFunc(GL_ONE, GL_ONE)
    glDisable(GL_DEPTH_TEST)

    root_sets = compute_all_roots(12)
    VAOs = create_circles(root_sets)
    
    while not glfw.window_should_close(window):
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        glUseProgram(program)
        
        for vao in VAOs:
            glBindVertexArray(vao)
            glDrawArrays(GL_TRIANGLE_FAN, 0, NUM_SIDES + 2)
        
        glfw.swap_buffers(window)
        glfw.poll_events()
    
    glfw.terminate()

if __name__ == "__main__":
    # pytest.main()
    # compute_all_roots(12)
    main()