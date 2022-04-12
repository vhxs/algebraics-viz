package main

import (
	"log"
	"math"
	"math/cmplx"
	"math/rand"
	"runtime"

	"github.com/go-gl/gl/v4.1-core/gl"
	"github.com/go-gl/glfw/v3.3/glfw"
)

func init() {
	// This is needed to arrange that main() runs on main thread.
	// See documentation for functions that are only allowed to be called from the main thread.
	runtime.LockOSThread()
}

// https://www.wolfe.id.au/2020/03/10/starting-a-go-project/
// https://commons.wikimedia.org/wiki/File:Algebraicszoom.png
// https://kylewbanks.com/blog/tutorial-opengl-with-golang-part-1-hello-opengl

// VAO and VBO tutorial: https://www.youtube.com/watch?v=WMiggUPst-Q
// https://stackoverflow.com/a/50408198
// glVertex2f deprecated... explains why there is no gl.Vertex2f

func rand_double(max float64) float64 {
	return rand.Float64() * max
}

func findroots_inner(coefs []complex128, deg int, roots []complex128) []complex128 {
	var root complex128
	if (deg == 1) {
		root = -coefs[0] / coefs[1]
		roots = append(roots, root)
		return roots
	}

	var n int
	var f, d, p, or complex128
	root = complex(rand_double(2) - 1, rand_double(2) - 1)
	var i int = 0
	var j int = 0

	// Newton's method
	for {
		if (j == 500) {
			root = complex(rand_double(2) - 1, rand_double(2) - 1)
			j = 0
		} else {
			j++
		}

		if (i >= 5000) {
			// nonconv = 1, doesn't converge
			break
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

		if (math.Pow(cmplx.Abs(or - root), 2) <= 1e-20) {
			break
		}
	}
	// fq[i]++
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

func findroots(coefs []complex128, deg int) []complex128 {
	var roots = make([]complex128, 0)
	roots = findroots_inner(coefs, deg, roots)
	return roots
}

const width = 800
const height = 600

// initOpenGL initializes OpenGL and returns an intiialized program.
func initOpenGL() uint32 {
    if err := gl.Init(); err != nil {
            panic(err)
    }
    version := gl.GoStr(gl.GetString(gl.VERSION))
    log.Println("OpenGL version", version)

    prog := gl.CreateProgram()
    gl.LinkProgram(prog)
    return prog
}

// initGlfw initializes glfw and returns a Window to use.
func initGlfw() *glfw.Window {
    if err := glfw.Init(); err != nil {
            panic(err)
    }
    
    glfw.WindowHint(glfw.Resizable, glfw.False)
    glfw.WindowHint(glfw.ContextVersionMajor, 4) // OR 2
    glfw.WindowHint(glfw.ContextVersionMinor, 1)
    glfw.WindowHint(glfw.OpenGLProfile, glfw.OpenGLCoreProfile)
    glfw.WindowHint(glfw.OpenGLForwardCompatible, glfw.True)

    window, err := glfw.CreateWindow(width, height, "Algebraics", nil, nil)
    if err != nil {
            panic(err)
    }
    window.MakeContextCurrent()

    return window
}

func draw(window *glfw.Window, program uint32) {
    gl.Clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)
    gl.UseProgram(program)

	// gl.VertexAttrib2f(0, 50, 50)
    
    glfw.PollEvents()
    window.SwapBuffers()
}

func main() {
    runtime.LockOSThread()

    window := initGlfw()
    defer glfw.Terminate()
    
    program := initOpenGL()

    for !window.ShouldClose() {
        draw(window, program)
    }
}