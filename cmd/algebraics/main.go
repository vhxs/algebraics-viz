package main

import (
	"math"
	"math/cmplx"
	"math/rand"
	"runtime"

	"github.com/go-gl/glfw/v3.3/glfw"
	// "github.com/go-gl/gl/v3.3-core/gl"
)

func init() {
	// This is needed to arrange that main() runs on main thread.
	// See documentation for functions that are only allowed to be called from the main thread.
	runtime.LockOSThread()
}

// https://www.wolfe.id.au/2020/03/10/starting-a-go-project/
// https://commons.wikimedia.org/wiki/File:Algebraicszoom.png

func rand_double(max float64) float64 {
	return rand.Float64() * max
}

// TODO: need to pass roots by reference.

func findroots_inner(coefs []complex128, deg int, roots []complex128) {
	var root complex128
	if (deg == 1) {
		root = -coefs[0] / coefs[1]
		roots = append(roots, root)
		return
	}

	var n int
	var f, d, p, or complex128
	root = complex(rand_double(2) - 1, rand_double(2) - 1)
	var i int = 0
	var j int = 0

	// probably Newton's method...?
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
			p *= root
			f += p * coefs[n]
			d += p * coefs[n+1] * complex(float64(n+1), 0)
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
		findroots_inner(coefs, deg-1, roots)
	}
}

func findroots(coefs []complex128, deg int) []complex128 {
	roots := make([]complex128, deg)
	findroots_inner(coefs, deg, roots)
	return roots
}

func main() {
	err := glfw.Init()
	if err != nil {
		panic(err)
	}
	defer glfw.Terminate()

	window, err := glfw.CreateWindow(640, 480, "Testing", nil, nil)
	if err != nil {
		panic(err)
	}

	window.MakeContextCurrent()

	for !window.ShouldClose() {
		// Do OpenGL stuff.
		window.SwapBuffers()
		glfw.PollEvents()
	}

	// https://pkg.go.dev/github.com/go-gl/gl/v2.1/gl
}