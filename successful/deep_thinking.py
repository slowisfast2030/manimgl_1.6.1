from manimlib import *

class test(Scene):
    def construct(self):
        c = Circle().shift(LEFT)
        partial_circle = Arc(start_angle=0, angle=PI)
        s = Square().shift(RIGHT)
        line = Line(RIGHT*2, LEFT*2)
        self.play(Transform(partial_circle, line))