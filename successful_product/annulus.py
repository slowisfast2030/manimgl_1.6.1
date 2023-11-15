from manimlib import *

class test(Scene):
    def construct(self):
        rings = AnnularSector(inner_radius=1, outer_radius=2, angle=4/4*PI).set_fill(BLUE)
        self.add(rings)
        c = Square().set_fill(RED, 1)
        c.shift(LEFT*3)
        self.add(c)
