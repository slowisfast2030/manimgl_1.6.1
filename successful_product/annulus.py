from manimlib import *

class test(Scene):
    def construct(self):
        rings = Annulus(inner_radius=1, outer_radius=2).set_fill(BLUE)
        self.add(rings)
