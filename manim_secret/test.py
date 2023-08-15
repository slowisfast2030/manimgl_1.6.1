from manimlib import *

class test(Scene):
    def construct(self):
        c = Circle()
        s = Square()
        self.play(Transform(c, s))
        self.wait(1)
                  