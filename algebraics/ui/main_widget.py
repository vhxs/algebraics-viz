from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QColorDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from algebraics.ui.gl_widget import GLWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Algebraic numbers")
        self.gl_widget = GLWidget()
        self.max_degree = len(self.gl_widget.colors_by_degree)

        main = QHBoxLayout(self)
        main.addWidget(self._create_control_panel())
        main.addWidget(self.gl_widget, stretch=1)

    def _create_control_panel(self) -> QWidget:
        container = QWidget()
        v = QVBoxLayout(container)
        v.addLayout(self._create_color_controls())
        v.addLayout(self._create_modify_buttons())

        v.addWidget(self._create_separator())

        v.addLayout(self._create_zoom_controls())
        v.addLayout(self._create_translate_controls())
        v.addWidget(QLabel("Radius Length"))
        v.addWidget(self._create_radius_slider())

        v.addWidget(self._create_separator())

        v.addLayout(self._create_parameter_controls())
        v.addWidget(self._create_generate_button())
        v.addStretch()
        return container
    
    def _create_default_color_button(self):
        btn = QPushButton(f"Default")
        color = self.gl_widget.default_color
        btn.setStyleSheet(f"background-color: rgb({color[0]*255},{color[1]*255},{color[2]*255});")
        btn.clicked.connect(lambda _, idx="default": self._select_color(idx))
        self.color_buttons["default"] = btn
        self.color_layout.addWidget(btn)

    def _create_color_controls(self) -> QVBoxLayout:
        self.color_layout = QVBoxLayout()
        self.color_buttons = {}
        
        self._create_default_color_button()

        for degree in range(1, self.max_degree + 1):
            color = self.gl_widget.colors_by_degree[degree]
            btn = QPushButton(f"Degree {degree}")
            btn.setStyleSheet(f"background-color: rgb({color[0]*255},{color[1]*255},{color[2]*255});")
            btn.clicked.connect(lambda _, idx=degree: self._select_color(idx))
            self.color_buttons[degree] = btn
            self.color_layout.addWidget(btn)
        return self.color_layout

    def _create_modify_buttons(self) -> QHBoxLayout:
        h = QHBoxLayout()
        self.minus_btn = QPushButton("Remove degree")
        self.minus_btn.clicked.connect(self._remove_color_button)
        self.minus_btn.setDisabled(self.max_degree <= 1)
        self.plus_btn = QPushButton("Add degree")
        self.plus_btn.clicked.connect(self._add_new_color_button)
        self.plus_btn.setDisabled(self.max_degree >= self.gl_widget.max_degree)
        h.addWidget(self.minus_btn)
        h.addWidget(self.plus_btn)
        return h

    def _create_zoom_controls(self) -> QVBoxLayout:
        v = QVBoxLayout()
        for label, slot in [("Zoom In", self.zoom_in), ("Zoom Out", self.zoom_out)]:
            btn = QPushButton(label)
            btn.clicked.connect(slot)
            v.addWidget(btn)
        return v

    def _create_translate_controls(self) -> QGridLayout:
        directions = {
            "Up": self.move_up,
            "Left": self.move_left,
            "Right": self.move_right,
            "Down": self.move_down,
        }
        positions = {"Up": (0,1), "Left": (1,0), "Right": (1,2), "Down": (2,1)}
        grid = QGridLayout()
        for name, slot in directions.items():
            btn = QPushButton(name)
            btn.clicked.connect(slot)
            grid.addWidget(btn, *positions[name])
        return grid

    def _create_parameter_controls(self) -> QHBoxLayout:
        h = QHBoxLayout()
        self.degree_spin = QSpinBox()
        self.degree_spin.setValue(self.gl_widget.max_degree)
        self.length_spin = QSpinBox()
        self.length_spin.setValue(self.gl_widget.max_length)
        for label, widget in [("Degree", self.degree_spin), ("Length", self.length_spin)]:
            h.addWidget(QLabel(label))
            h.addWidget(widget)
        return h

    def _create_generate_button(self) -> QPushButton:
        btn = QPushButton("Generate")
        btn.clicked.connect(lambda: self._update_circles(
            self.length_spin.value(),
            self.degree_spin.value()
        ))
        return btn
    
    def _create_separator(self) -> QFrame:
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)

        return separator

    def _update_circles(self, max_length: int, max_degree: int):
        self.gl_widget.generate_circles_by_degree(max_length, max_degree + 1)
        self.gl_widget.update()

        self._remove_all_color_buttons()
        self.max_degree = max_degree

        for degree in range(1, self.max_degree + 1):
            color = self.gl_widget.colors_by_degree[degree]
            btn = QPushButton(f"Degree {degree}")
            btn.setStyleSheet(f"background-color: rgb({color[0]*255},{color[1]*255},{color[2]*255});")
            btn.clicked.connect(lambda _, idx=degree: self._select_color(idx))
            self.color_buttons[degree] = btn
            self.color_layout.addWidget(btn)

    def _add_new_color_button(self):
        self.max_degree += 1

        btn = QPushButton(f"Degree {self.max_degree}")
        btn.setStyleSheet("background-color: rgb(255,255,255);")
        btn.clicked.connect(lambda _, idx=self.max_degree: self._select_color(idx))
        self.color_buttons[self.max_degree] = btn
        self.gl_widget.colors_by_degree[self.max_degree] = [1.0, 1.0, 1.0]
        self.color_layout.addWidget(btn)

        if self.max_degree >= 1:
            self.minus_btn.setDisabled(False)
        
        if self.max_degree >= self.gl_widget.max_degree:
            self.plus_btn.setDisabled(True)

        self.gl_widget.update()

    def _remove_all_color_buttons(self):
        for btn in self.color_buttons.values():
            btn.setParent(None)
        self.color_buttons.clear()

        self._create_default_color_button()

    def _remove_color_button(self):
        if self.max_degree > 0:
            btn = self.color_buttons.pop(self.max_degree)
            btn.setParent(None)
            self.gl_widget.colors_by_degree.pop(self.max_degree)
            self.max_degree -= 1

            if self.max_degree < 1:
                self.minus_btn.setDisabled(True)

            if self.max_degree < self.gl_widget.max_degree:
                self.plus_btn.setDisabled(False)

            self.gl_widget.update()

    def _select_color(self, degree: int | str):
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_buttons[degree].setStyleSheet(
                    f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});"
                )
            if isinstance(degree, int):
                self.gl_widget.colors_by_degree[degree] = [color.red() / 255., color.green() / 255., color.blue() / 255.]
            else:
                self.gl_widget.default_color = [color.red() / 255., color.green() / 255., color.blue() / 255.]
            self.gl_widget.update()

    def _create_radius_slider(self):
        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(1, 20)
        slider.setValue(10)
        slider.valueChanged.connect(self.gl_widget.update_radius_scale)

        return slider

    def zoom_in(self):
        self.gl_widget.zoom_in()

    def zoom_out(self):
        self.gl_widget.zoom_out()

    def move_left(self):
        self.gl_widget.move_left()

    def move_right(self):
        self.gl_widget.move_right()

    def move_up(self):
        self.gl_widget.move_up()

    def move_down(self):
        self.gl_widget.move_down()