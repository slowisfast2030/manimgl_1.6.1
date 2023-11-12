from manimlib import *

class ChangeInAreaOverChangeInX(Scene):
    def construct(self):
        fractions = []
        for pair in ("Change in area", "Change in $x$"), ("$d(x^2)$", "$dx$"):
            top, bottom = list(map(TexText, pair))
            top.set_color(YELLOW)
            bottom.set_color(BLUE_B)
            frac_line = Tex("-")
            frac_line.stretch_to_fit_width(top.get_width())
            top.next_to(frac_line, UP, SMALL_BUFF)
            bottom.next_to(frac_line, DOWN, SMALL_BUFF)
            fractions.append(VGroup(
                top, frac_line, bottom
            ))
        words, symbols = fractions

        self.play(Write(words[0], run_time = 1))
        self.play(*list(map(Write, words[1:])), run_time = 1)
        self.wait()
        self.play(Transform(words, symbols))
        self.wait()

class test(Scene):
    CONFIG = {
        "square_width": 3,
        "square_color": GREEN,
        "square_fill_opacity": 0.75,
        "dx" : 0.25,
        "dx_color" : BLUE_B,
    }
    def construct(self):
        self.add_function_label()
        self.introduce_square()
        self.increase_area()
    
    def add_function_label(self):
        label = Tex("f(x) = x^2")
        label.next_to(ORIGIN, RIGHT, buff = (self.square_width-3)/2.)
        label.to_edge(UP)
        self.add(label)
        self.function_label = label

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

        self.square = square
        self.side_braces = braces

    def increase_area(self):
        color_kwargs = {
            "fill_color" : YELLOW,
            "fill_opacity" : self.square_fill_opacity,
            "stroke_width" : 0,
        }
        right_rect = Rectangle(
            width = self.dx,
            height = self.square_width,
            **color_kwargs
        )
        bottom_rect = right_rect.copy().rotate(-PI/2)
        right_rect.next_to(self.square, RIGHT, buff = 0)
        bottom_rect.next_to(self.square, DOWN, buff = 0)
        corner_square = Square(
            side_length = self.dx,
            **color_kwargs
        )
        corner_square.next_to(self.square, DOWN+RIGHT, buff = 0)

        right_line = Line(
            self.square.get_corner(UP+RIGHT),
            self.square.get_corner(DOWN+RIGHT),
            stroke_width = 0
        )
        bottom_line = Line(
            self.square.get_corner(DOWN+RIGHT),
            self.square.get_corner(DOWN+LEFT),
            stroke_width = 0
        )
        corner_point = VectorizedPoint(
            self.square.get_corner(DOWN+RIGHT)
        )

        little_braces = VGroup()
        for vect in RIGHT, DOWN:
            brace = Brace(
                corner_square, vect, 
                buff = SMALL_BUFF,
            )
            text = brace.get_tex("dx", buff = SMALL_BUFF)
            text.set_color(self.dx_color)
            brace.add(text)
            little_braces.add(brace)

        right_brace, bottom_brace = self.side_braces
        self.play(
            Transform(right_line, right_rect),
            Transform(bottom_line, bottom_rect),
            Transform(corner_point, corner_square),
            right_brace.next_to, right_rect, RIGHT, SMALL_BUFF,
            bottom_brace.next_to, bottom_rect, DOWN, SMALL_BUFF,
        )
        self.remove(corner_point, bottom_line, right_line)
        self.add(corner_square, bottom_rect, right_rect)
        self.play(*list(map(GrowFromCenter, little_braces)))
        self.wait()
        self.play(*it.chain(*[
            [mob.shift, vect*SMALL_BUFF]
            for mob, vect in [
                (right_rect, RIGHT),
                (bottom_rect, DOWN),
                (corner_square, DOWN+RIGHT),
                (right_brace, RIGHT),
                (bottom_brace, DOWN),
                (little_braces, DOWN+RIGHT)
            ]
        ]))