from manimlib import *

class bl(Scene):
    def construct(self):
        c1 = Circle().shift(LEFT*0.7).set_fill(RED, 0.8)
        c2 = Circle().shift(RIGHT*0.7).set_fill(GREEN, 0.8)
        self.add(c1, c2)

        c = Intersection(c1, c2)
        self.add(c)

        self.wait()