from manimlib import *

class test(Scene):
    def construct(self):
        t = Tex("A^2", "+", "B^2", "=", "C^2")
        self.add(t)

        c = Tex("A^2 + B^2 = C^2").shift(DOWN)
        self.add(c)
        
        print(t.submobjects)
        print(c.submobjects)