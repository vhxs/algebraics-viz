from typing import Annotated
from pydantic import AfterValidator, BaseModel, computed_field


class RootSet(BaseModel):
    """
    Corresponds to roots of a single-variable complex polynomial
    """
    roots: list[complex]
    length: int

    @computed_field
    @property
    def degree(self) -> int:
        return len(self.roots) - 1
    
def drop_ending_zeros(coefficients: list[complex]):
    index = len(coefficients) - 1
    while index >= 0 and coefficients[index] == 0:
        index -= 1
    return coefficients[:index+1]

class ComplexPolynomial(BaseModel):
    coefficients: Annotated[list[complex], AfterValidator(drop_ending_zeros)]

    @computed_field
    @property
    def degree(self) -> int:
        return len(self.coefficients) - 1
    
    @computed_field
    @property
    def length(self) -> float:
        return sum(abs(coefficient) for coefficient in self.coefficients)
    
    def divide_in_place(self, root: complex):
        degree = self.degree
        for n in range(degree, 0, -1):
            self.coefficients[n - 1] += root * self.coefficients[n]
        
        self.coefficients[:degree] = self.coefficients[1:degree + 1]
        self.coefficients.pop()