import pytest

from algebraics.polynomial.models import ComplexPolynomial
from algebraics.polynomial.polynomial import find_roots


def test_quadratic():
    polynomial = ComplexPolynomial(
        coefficients=[complex(-3, 0), complex(2, 0), complex(1, 0)],
        length=6
    )
    root_set = find_roots(polynomial)
    assert root_set is not None
    assert pytest.approx(root_set.roots[0].real, rel=1e-5) == 1.0
    assert pytest.approx(root_set.roots[1].real, rel=1e-5) == -3.0

def test_cubic():
    polynomial = ComplexPolynomial(
        coefficients=[complex(-6, 0), complex(11, 0), complex(-6, 0), complex(1, 0)],
        length=24
        )
    root_set = find_roots(polynomial)
    assert root_set is not None
    expected_roots = [1.0, 2.0, 3.0]
    root_reals = sorted([root.real for root in root_set.roots])
    for root, expected in zip(root_reals, expected_roots):
        assert pytest.approx(root, rel=1e-5) == expected