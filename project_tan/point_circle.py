from manimlib import *

class test(Scene):
    def construct(self):
        c = Circle()
        #line = Line(c.get_center(), c.point_at_angle(PI/3))
        line = Line(c.get_center(), c.point_from_proportion(1/6))
        self.add(c,line)
