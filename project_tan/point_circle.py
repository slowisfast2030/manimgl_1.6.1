from manimlib import *

class test(Scene):
    def construct(self):
        c = Circle()
        line = Line(c.get_center(), c.point_at_angle(PI/3))
        self.add(c,line)
