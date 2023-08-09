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


class test1(Scene):
    def construct(self):

        c = Tex(r"\pi").scale(0.2).set_color(TEAL)
        cg = c.get_grid(10, 10, 5)
        self.add(cg)
        self.wait(1)

class test2(Scene):
    def construct(self):
        c = Circle()
        print(c.data)
        print("-"*100)
        print(c.uniforms)

        self.add(c)
        self.wait(1)