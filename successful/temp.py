from manimlib import *

class test(Scene):
    def construct(self):

        c = Circle()
        print(c.get_points())
        for p in c.get_points():
            self.add(Dot(p).set_color(YELLOW_E).set_opacity(0.5))

        c.resize_points(300)
        print("-"*100)
        print(c.get_points())
        for p in c.get_points():
            self.add(Dot(p).set_color(RED))

        # cc = Circle().set_points(c.get_points())
        # self.add(cc)
        self.wait(1)    
