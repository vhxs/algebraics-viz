from typing import Generator, Optional
from algebraics.polynomial.models import ComplexPolynomial, RootSet
from dynaconf import Dynaconf
import random

from algebraics.polynomial.partition import enumerate_partitions, generate_signs


settings = Dynaconf(
    settings_files=["settings.toml"],
    environments=False
)

def random_complex(scale=2):
    return complex(random.uniform(-scale / 2, scale / 2), random.uniform(-scale / 2, scale / 2))

def find_roots(polynomial: ComplexPolynomial) -> Optional[RootSet]:
    """
    find_roots will take a polynomial of degree N and attempt to find all N roots.
    By the fundamental theorem of algebra, we know that such a polynomial has N roots.
    """
    roots: list[complex] = []
    original_length = polynomial.length

    while (degree := polynomial.degree) > 0:
        if degree == 1:
            root = -polynomial.coefficients[0] / polynomial.coefficients[1]
            roots.append(root)
            break

        success = False
        for _ in range(settings.POLYNOMIAL.MAX_ROOT_INITIALIZATIONS):
            candidate_root = random_complex()

            for _ in range(settings.POLYNOMIAL.MAX_ATTEMPTS_PER_ROOT):
                previous_root = candidate_root
                polynomial_value, derivative_value, power_term = 0, 0, 1
                
                for n in range(degree):
                    polynomial_value += power_term * polynomial.coefficients[n]
                    derivative_value += power_term * polynomial.coefficients[n + 1] * (n + 1)
                    power_term *= candidate_root
                
                polynomial_value += power_term * polynomial.coefficients[degree]
                candidate_root -= polynomial_value / derivative_value
                
                if abs(previous_root - candidate_root) ** 2 <= 1e-20:
                    success = True
                    break

            if success: break
        
        if success:
            # The candidate root is an approximate root according to the stopping criteria
            roots.append(candidate_root)

            # Apply synthetic division using the root we just found
            polynomial.divide_in_place(candidate_root)
        else:
            return None
    
    # Return a RootSet
    return RootSet(
        roots=roots,
        length=original_length
    )

def enumerate_polynomials_sjbrooks(max_length: int) -> Generator[ComplexPolynomial]:
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
                
                yield ComplexPolynomial(coefficients=coefficients)

def enumerate_polynomials(max_length: int, max_degree: int) -> Generator[ComplexPolynomial]:
    for length in range(max_length):
        for degree in range(max_degree):
            for partition in enumerate_partitions(length + degree, degree):
                coefficients = [x - 1 for x in partition]
                if coefficients and coefficients[-1] != 0:
                    yield from map(
                        lambda coefs: ComplexPolynomial(coefficients=[complex(x, 0) for x in coefs]),
                        generate_signs(coefficients)
                    )

if __name__ == "__main__":
    for polynomial in enumerate_polynomials(4, 4):
        print([int(x.real) for x in polynomial.coefficients])