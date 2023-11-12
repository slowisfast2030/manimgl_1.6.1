from manimlib import *

class test(Scene):
    CONFIG = {
        "square_width": 3,
        "square_color": GREEN,
        "square_fill_opacity": 0.75,
    }
    def construct(self):
        self.add_function_label()
        self.introduce_square()
    
    def add_function_label(self):
        label = Tex("f(x) = x^2")
        label.next_to(ORIGIN, RIGHT, buff = (self.square_width-3)/2.)
        label.to_edge(UP)
        self.add(label)

    def introduce_square(self):
        square = Square(
            side_length = self.square_width,
            stroke_width = 0,
            fill_opacity = self.square_fill_opacity,
            fill_color = self.square_color,
        )
        square.to_corner(UP+LEFT, buff = LARGE_BUFF)
        x_squared = Tex("x^2")
        x_squared.move_to(square)

        braces = VGroup()
        for vect in RIGHT, DOWN:
            brace = Brace(square, vect)
            text = brace.get_tex("x")
            brace.add(text)
            braces.add(brace)

        self.play(
            DrawBorderThenFill(square)
        )
        self.play(*list(map(GrowFromCenter, braces)))
        self.play(Write(x_squared))