from pydantic import BaseModel


class Circle(BaseModel):
    x_center: float
    y_center: float
    radius: float
    red: float = 1.0
    green: float = 1.0
    blue: float = 1.0

    def set_color(self, color: list[float]):
        if len(color) != 3:
            raise ValueError("Incorrect number of elements in color vector")
        
        self.red = color[0]
        self.green = color[1]
        self.blue = color[2]