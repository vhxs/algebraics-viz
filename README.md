# algebraics-viz

The algebraic numbers are exactly those that are roots of a integer polynomial. They form a subfield of the complex numbers. Since they are dense in R, they are hard to visualize.

The Wikipedia article on the algebraic numbers has a beautiful visualization of them in R^2. The image has with it partially written source code, written by someone who I cannot make the identity of.

Take the partial C code here, rewrite it in Golang: https://commons.wikimedia.org/wiki/File:Algebraicszoom.png

- [x] implemented newton's method to find the roots of a polynomial
- [ ] find the roots of lots and lots of polynomials (implement "precalc")
- [ ] figure out how the hell to draw stuff in OpenGL
