from manimlib import *

class bl(Scene):
    def construct(self):
        c1 = Circle().shift(LEFT*0.7)
        c2 = Circle().shift(RIGHT*0.7)
        self.add(c1, c2)

        #c = Intersection(c1, c2).set_fill(TEAL, 0)
        c = Union(c1, c2).set_fill(TEAL, 0)
        self.add(c)

        self.wait()
