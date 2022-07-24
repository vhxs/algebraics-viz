package main

import (
	"fmt"
	_ "image/png"
	"math"
	"math/cmplx"
	"math/rand"
)

// https://www.wolfe.id.au/2020/03/10/starting-a-go-project/
// https://commons.wikimedia.org/wiki/File:Algebraicszoom.png
// https://kylewbanks.com/blog/tutorial-opengl-with-golang-part-1-hello-opengl
// https://learnopengl.com/book/book_pdf.pdf

func rand_double(max float64) float64 {
	return rand.Float64() * max
}

func findroots_inner(coefs []complex128, deg int, roots []complex128) []complex128 {
	var root complex128
	if deg == 1 {
		root = -coefs[0] / coefs[1]
		roots = append(roots, root)
		return roots
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

		if math.Pow(cmplx.Abs(or-root), 2) <= 1e-20 {
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
	roots := make([]complex128, 0)
	roots = findroots_inner(coefs, deg, roots)
	return roots
}

func main() {
	coefs := []complex128{complex(1, 0), complex(0, 0), complex(-1, 0)}
	roots := findroots(coefs, 2)

	fmt.Print(roots)
	return
}
