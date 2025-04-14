from algebraics.ui.gl_widget import GLWidget


from PyQt6.QtWidgets import QColorDialog, QGridLayout, QHBoxLayout, QPushButton, QVBoxLayout, QWidget


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Algebraic numbers")
        main_layout = QHBoxLayout()

        self.gl_widget = GLWidget()

        control_layout = QVBoxLayout()
        self.color_layout = QVBoxLayout()
        self.color_buttons = {}

        self.max_degree = len(self.gl_widget.colors_by_degree)

        self.add_initial_color_buttons()

        modify_layout = QHBoxLayout()
        self.minus_btn = QPushButton("-")
        self.minus_btn.clicked.connect(self.remove_color_button)
        if self.max_degree <= 1:
            self.minus_btn.setDisabled(True)

        self.plus_btn = QPushButton("+")
        self.plus_btn.clicked.connect(self.add_new_color_button)
        if self.max_degree >= self.gl_widget.max_degree:
            self.plus_btn.setDisabled(True)

        modify_layout.addWidget(self.minus_btn)
        modify_layout.addWidget(self.plus_btn)

        control_layout.addLayout(self.color_layout)
        control_layout.addLayout(modify_layout)

        zoom_in_btn = QPushButton("Zoom In")
        zoom_in_btn.clicked.connect(self.zoom_in)
        control_layout.addWidget(zoom_in_btn)
        zoom_out_btn = QPushButton("Zoom Out")
        zoom_out_btn.clicked.connect(self.zoom_out)
        control_layout.addWidget(zoom_out_btn)

        translate_layout = QGridLayout()
        up_btn = QPushButton("Up")
        up_btn.clicked.connect(self.move_up)
        left_btn = QPushButton("Left")
        left_btn.clicked.connect(self.move_left)
        right_btn = QPushButton("Right")
        right_btn.clicked.connect(self.move_right)
        down_btn = QPushButton("Down")
        down_btn.clicked.connect(self.move_down)
        translate_layout.addWidget(up_btn, 0, 1)
        translate_layout.addWidget(left_btn, 1, 0)
        translate_layout.addWidget(right_btn, 1, 2)
        translate_layout.addWidget(down_btn, 2, 1)
        control_layout.addLayout(translate_layout)

        control_layout.addStretch(1)
        control_widget = QWidget()
        control_widget.setLayout(control_layout)

        main_layout.addWidget(control_widget)
        main_layout.addWidget(self.gl_widget, stretch=1)
        self.setLayout(main_layout)

    def add_initial_color_buttons(self):
        btn = QPushButton(f"Default")
        color = self.gl_widget.default_color
        btn.setStyleSheet(f"background-color: rgb({color[0]*255},{color[1]*255},{color[2]*255});")
        btn.clicked.connect(lambda _, idx="default": self.select_color(idx))
        self.color_buttons["default"] = btn
        self.color_layout.addWidget(btn)

        for degree in range(1, self.max_degree + 1):
            color = self.gl_widget.colors_by_degree[degree]
            btn = QPushButton(f"Degree {degree}")
            btn.setStyleSheet(f"background-color: rgb({color[0]*255},{color[1]*255},{color[2]*255});")
            btn.clicked.connect(lambda _, idx=degree: self.select_color(idx))
            self.color_buttons[degree] = btn
            self.color_layout.addWidget(btn)

    def add_new_color_button(self):
        self.max_degree += 1

        btn = QPushButton(f"Degree {self.max_degree}")
        btn.setStyleSheet("background-color: rgb(255,255,255);")
        btn.clicked.connect(lambda _, idx=self.max_degree: self.select_color(idx))
        self.color_buttons[self.max_degree] = btn
        self.gl_widget.colors_by_degree[self.max_degree] = [1.0, 1.0, 1.0]
        self.color_layout.addWidget(btn)

        if self.max_degree >= 1:
            self.minus_btn.setDisabled(False)
        
        if self.max_degree >= self.gl_widget.max_degree:
            self.plus_btn.setDisabled(True)

        self.gl_widget.update()

    def remove_color_button(self):
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

    def select_color(self, degree: int | str):
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