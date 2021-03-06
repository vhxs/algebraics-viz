package main

import (
	"fmt"
	_ "image/png"
	"math"
	"math/cmplx"
	"math/rand"
	"runtime"
	"strings"

	"github.com/go-gl/gl/v4.5-core/gl"
	"github.com/go-gl/glfw/v3.3/glfw"
)

// https://www.wolfe.id.au/2020/03/10/starting-a-go-project/
// https://commons.wikimedia.org/wiki/File:Algebraicszoom.png
// https://kylewbanks.com/blog/tutorial-opengl-with-golang-part-1-hello-opengl
// https://learnopengl.com/book/book_pdf.pdf
// https://vkguide.dev/

func rand_double(max float64) float64 {
	return rand.Float64() * max
}

func findroots_inner(coefs []complex128, deg int, roots []complex128) (bool, []complex128) {
	var root complex128
	if deg == 1 {
		root = -coefs[0] / coefs[1]
		roots = append(roots, root)
		return true, roots
	}

	var n int
	var f, d, p, or complex128
	root = complex(rand_double(2)-1, rand_double(2)-1)
	var i int = 0
	var j int = 0

	// Newton's method
	for {
		if j == 500 {
			root = complex(rand_double(2)-1, rand_double(2)-1)
			j = 0
		} else {
			j++
		}

		if i >= 5000 {
			// doesn't converge
			return false, nil
		}
		i++

		or = root
		f = 0
		d = 0
		p = 1

		// evaluating the polynomial and its derivative at a candidate root
		for n = 0; n < deg; n++ {
			f += p * coefs[n]
			d += p * coefs[n+1] * complex(float64(n+1), 0)
			p *= root
		}
		f += p * coefs[deg]
		root -= f / d

		if math.Pow(cmplx.Abs(or-root), 2) <= 1e-20 {
			break
		}
	}

	// add root
	roots = append(roots, root)

	// reduce degree of polynomial by 1
	for n = deg; n > 0; n-- {
		coefs[n-1] += root * coefs[n]
	}
	for n = 0; n < deg; n++ {
		coefs[n] = coefs[n+1]
	}
	return findroots_inner(coefs, deg-1, roots)
}

func findroots(coefs []complex128, deg int) (bool, []complex128) {
	roots := make([]complex128, 0)
	return findroots_inner(coefs, deg, roots)
}

// find roots of polynomials up to a certain length
// as a way to bound the number of polynomials over which to compute the roots of
// https://en.wikipedia.org/wiki/height_function#height_of_a_polynomial

// The algebraic numbers are precisely those complex numbers that are roots
// of polynomials with integer coefficients
func compute_all_roots(max_length int) ([]complex128, []int, []int) {
	points := make([]complex128, 0)
	lengths := make([]int, 0)
	degs := make([]int, 0)

	// iterate over polynomial length
	for length := 2; length <= max_length; length++ {
		fmt.Printf("Length: %d\n", length)
		pos_coefs := make([]int, length)

		// iterate over integer partitions of length
		// partitions are represented as bit strings
		for bits := 1<<(length-1) - 1; bits >= 0; bits -= 2 {
			pos_coefs[0] = 0

			// iterate over bits in the representation
			// to construct a sequence of positive integers
			deg := 0
			for shift := length - 2; shift >= 0; shift-- {
				if (bits>>shift)&1 == 1 {
					pos_coefs[deg] += 1
				} else {
					deg += 1
					pos_coefs[deg] = 0
				}

				if deg <= 0 {
					continue
				}

				// count nonzero elements
				num_non_zero := 0
				for i := deg; i >= 0; i-- {
					if pos_coefs[i] != 0 {
						num_non_zero += 1
					}
				}

				if num_non_zero == 0 {
					continue
				}

				// use bit string to represent signs
				for sign_bits := 1<<(num_non_zero-1) - 1; sign_bits >= 0; sign_bits-- {
					coefs := make([]complex128, deg+1)

					// determine each coefficient in a polynomial
					sign := 1
					for c := deg; c >= 0; c-- {
						coef := complex(float64(pos_coefs[c]), 0)
						if pos_coefs[c] == 0 || c == deg {
							coefs[c] = coef
						} else {
							if sign_bits&sign == 1 {
								coefs[c] = coef
							} else {
								coefs[c] = -coef
							}
						}
					}

					// now that we have a polynomial, try to find roots
					did_converge, roots := findroots(coefs, deg)
					if did_converge {
						points = append(points, roots...)
						for i := 0; i < len(roots); i++ {
							lengths = append(lengths, length)
							degs = append(degs, deg)
						}
					}
				}
			}
		}
	}

	return points, lengths, degs
}

func compileShader(source string, shaderType uint32) (uint32, error) {
	shader := gl.CreateShader(shaderType)

	csources, free := gl.Strs(source)
	gl.ShaderSource(shader, 1, csources, nil)
	free()
	gl.CompileShader(shader)

	var status int32
	gl.GetShaderiv(shader, gl.COMPILE_STATUS, &status)
	if status == gl.FALSE {
		var logLength int32
		gl.GetShaderiv(shader, gl.INFO_LOG_LENGTH, &logLength)

		log := strings.Repeat("\x00", int(logLength+1))
		gl.GetShaderInfoLog(shader, logLength, nil, gl.Str(log))

		return 0, fmt.Errorf("failed to compile %v: %v", source, log)
	}

	return shader, nil
}

func newProgram(vertexShaderSource, fragmentShaderSource string) (uint32, error) {
	vertexShader, err := compileShader(vertexShaderSource, gl.VERTEX_SHADER)
	if err != nil {
		return 0, err
	}

	fragmentShader, err := compileShader(fragmentShaderSource, gl.FRAGMENT_SHADER)
	if err != nil {
		return 0, err
	}

	program := gl.CreateProgram()

	gl.AttachShader(program, vertexShader)
	gl.AttachShader(program, fragmentShader)
	gl.LinkProgram(program)

	var status int32
	gl.GetProgramiv(program, gl.LINK_STATUS, &status)
	if status == gl.FALSE {
		var logLength int32
		gl.GetProgramiv(program, gl.INFO_LOG_LENGTH, &logLength)

		log := strings.Repeat("\x00", int(logLength+1))
		gl.GetProgramInfoLog(program, logLength, nil, gl.Str(log))

		return 0, fmt.Errorf("failed to link program: %v", log)
	}

	gl.DeleteShader(vertexShader)
	gl.DeleteShader(fragmentShader)

	return program, nil
}

func init() {
	runtime.LockOSThread()
}

func framebuffer_size_callback(window *glfw.Window, width int, length int) {
	gl.Viewport(0, 0, int32(width), int32(length))
}

// https://stackoverflow.com/questions/59468388/how-to-use-gl-triangle-fan-to-draw-a-circle-in-opengl
func createCircle(xCenter float32, yCenter float32, radius float32, numSides int, r float32, g float32, b float32) uint32 {
	var VAO uint32
	var VBO uint32

	numVertices := numSides + 2

	vertices := []float32{xCenter, yCenter, 0, r, g, b}

	for i := 1; i < numVertices; i++ {
		x := xCenter + radius*float32(math.Cos(float64(i)*2.0*math.Pi/float64(numSides)))
		y := yCenter + radius*float32(math.Sin(float64(i)*2.0*math.Pi/float64(numSides)))
		vertices = append(vertices, x, y, 0, r, g, b)
	}

	gl.GenVertexArrays(1, &VAO)
	gl.GenBuffers(1, &VBO)

	gl.BindVertexArray(VAO)
	gl.BindBuffer(gl.ARRAY_BUFFER, VBO)

	gl.BufferData(gl.ARRAY_BUFFER, len(vertices)*4, gl.Ptr(vertices), gl.STATIC_DRAW)

	gl.VertexAttribPointerWithOffset(0, 3, gl.FLOAT, false, 6*4, 0)
	gl.VertexAttribPointerWithOffset(1, 3, gl.FLOAT, false, 6*4, 3*4)
	gl.EnableVertexAttribArray(0)
	gl.EnableVertexAttribArray(1)

	gl.BindVertexArray(0)

	return VAO
}

func createCircles(points []complex128, lengths []int, degs []int, numSides int) []uint32 {
	colors := [][]float32{
		{1, 0, 0},
		{0, 1, 0},
		{0, 0, 1},
		{0.7, 0.7, 0},
		{1, 0.6, 0},
		{0, 1, 1},
		{1, 0, 1},
		{0.6, 0.6, 0.6},
	}

	VAOs := make([]uint32, 0)

	for i := 0; i < len(points); i++ {
		xCenter := real(points[i])
		yCenter := imag(points[i])
		radius := math.Pow(0.5, float64(lengths[i]))

		var color []float32
		if degs[i] < 8 {
			color = colors[degs[i]-1]
		} else {
			color = []float32{1, 1, 1}
		}

		VAO := createCircle(float32(xCenter), float32(yCenter), float32(radius), numSides, color[0], color[1], color[2])
		VAOs = append(VAOs, VAO)
	}

	return VAOs
}

func main() {
	points, lengths, degs := compute_all_roots(12)

	// references:
	// https://github.com/JoeyDeVries/LearnOpenGL/blob/master/src/1.getting_started/2.1.hello_triangle/hello_triangle.cpp
	// https://github.com/go-gl/example/blob/master/gl41core-cube/cube.go
	// https://github.com/cstegel/opengl-samples-golang/blob/master/hello-triangle/hello_triangle.go

	err := glfw.Init()
	if err != nil {
		panic(err)
	}
	defer glfw.Terminate()

	glfw.WindowHint(glfw.Resizable, glfw.False)
	glfw.WindowHint(glfw.ContextVersionMajor, 4)
	glfw.WindowHint(glfw.ContextVersionMinor, 1)
	glfw.WindowHint(glfw.OpenGLProfile, glfw.OpenGLCoreProfile)
	glfw.WindowHint(glfw.OpenGLForwardCompatible, glfw.True)

	window, err := glfw.CreateWindow(1000, 1000, "Algebraics", nil, nil)
	if err != nil {
		panic(err)
	}

	window.MakeContextCurrent()

	// Initialize Glow
	if err := gl.Init(); err != nil {
		panic(err)
	}

	window.SetFramebufferSizeCallback(framebuffer_size_callback)

	vertexShaderSource := `
	#version 450 core

    layout (location = 0) in vec3 aPos;
	layout (location = 1) in vec3 aColor;

	out vec3 ourColor;

    void main()

    {

       gl_Position = vec4(aPos.x, aPos.y, aPos.z, 1.0);
	   ourColor = aColor;

    }` + "\x00"

	fragmentShaderSource := `
	#version 450 core

    out vec4 FragColor;
	in vec3 ourColor;

    void main()

    {

       FragColor = vec4(ourColor, 1.0f);

    }` + "\x00"

	// shaders
	program, err := newProgram(vertexShaderSource, fragmentShaderSource)
	if err != nil {
		panic(err)
	}

	numSides := 50

	VAOs := createCircles(points, lengths, degs, numSides)

	gl.Enable(gl.BLEND)
	gl.BlendFunc(gl.ONE, gl.ONE)
	gl.Disable(gl.DEPTH_TEST)

	for !window.ShouldClose() {
		// Do OpenGL stuff.

		gl.ClearColor(0, 0, 0, 1)
		gl.Clear(gl.COLOR_BUFFER_BIT)

		gl.UseProgram(program)

		for v := 0; v < len(VAOs); v++ {
			gl.BindVertexArray(VAOs[v])
			gl.DrawArrays(gl.TRIANGLE_FAN, 0, int32(numSides)+2)
		}

		window.SwapBuffers()
		glfw.PollEvents()
	}
}
