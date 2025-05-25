# Visualizing the Algebraic Numbers

An algebraic number is any complex number that is a root of some polynomial with integer coefficients. The algebraic numbers
are a subset (and more specifically, a subfield) of the complex numbers.

Mathematicians have explored several ways of visualizing the algebraic numbers, including the visualization on Wikipedia. This code
is a Python rewrite of original C code that generated the Wikipedia visualization. It has a simple GUI that lets the user change
some parameters of the visualization, including changing the color palette or the radius of drawn circles.

Here's a screenshot of the application:

![image](assets/screenshot.png)

## Running the application

This project's dependencies are managed by [uv](https://github.com/astral-sh/uv), so if you'll need to install this first. Once installed, run:

```uv venv && uv sync```

to create a virtual environment and installed dependencies, and then:

```uv run app.py```

to run the application.

This repository also include a GitHub Action that builds and publishes an executable to run the application (using [`pyinstaller`](https://pyinstaller.org/en/stable/)), but this is still experimental and not thoroughly tested.