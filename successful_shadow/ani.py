from manimlib import *

class ani_add(Scene):
    def construct(self):
        p = NumberPlane()
        self.add(p)

        c = Circle().set_color(RED)
        s = Square().set_color(BLUE)
        t = Triangle().set_color(GREEN)
        c.add(s, t)

        self.play(ShowCreation(c, lag_ratio=1, run_time=3))
        print("\n", "-"*100)
        print(c.submobjects)
        print("-"*100)

class ani_vg(Scene):
    def construct(self):
        p = NumberPlane()
        self.add(p)

        c = Circle().set_color(RED)
        s = Square().set_color(BLUE)
        t = Triangle().set_color(GREEN)
        #c.add(s, t)
        vg = VGroup(c,s,t)

        self.play(ShowCreation(vg, lag_ratio=1, run_time=3))
        print("\n", "-"*100)
        print(vg.submobjects)
        print("-"*100)