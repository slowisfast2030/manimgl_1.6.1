from manimlib import *

class test(Scene):
    CONFIG = {
        "square_width": 5,
    }
    def construct(self):
        label = Tex("f(x) = x^2")
        label.next_to(ORIGIN, RIGHT, buff = (self.square_width-3)/2.)
        label.to_edge(UP)
        self.add(label)