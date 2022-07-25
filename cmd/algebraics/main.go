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

// find roots of polynomials up to a certain height
// as a way to bound the number of polynomials over which to compute the roots of
// https://en.wikipedia.org/wiki/Height_function#Height_of_a_polynomial

// The algebraic numbers are precisely those complex numbers that are roots
// of polynomials with integer coefficients
func compute_all_roots(max_height int) []complex128 {
	points := make([]complex128, 0)

	// iterate over polynomial height
	for height := 2; height <= max_height; height++ {
		fmt.Printf("Height: %d\n", height)
		pos_coefs := make([]int, height)

		// iterate over integer partitions of height
		// partitions are represented as bit strings
		for bits := 1<<(height-1) - 1; bits >= 0; bits -= 2 {
			pos_coefs[0] = 0

			// iterate over bits in the representation
			// to construct a sequence of positive integers
			deg := 0
			for shift := height - 2; shift >= 0; shift-- {
				if (bits>>shift)&1 == 1 {
					pos_coefs[deg] += 1
				} else {
					deg += 1
					pos_coefs[deg] = 0
				}

				if deg == 0 {
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
					}
				}
			}
		}
	}

	return points
}

func main() {
	points := compute_all_roots(15)
	fmt.Printf("Number of algebraic numbers computed: %d\n", len(points))

	// next step: plot algebraics on 2d plane using OpenGL
}
