from pydantic import BaseModel


class Circle(BaseModel):
    x_center: float
    y_center: float
    radius: float
    red: float
    green: float
    blue: float