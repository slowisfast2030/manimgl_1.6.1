from manimlib import *

class test_demo(Scene):
    def construct(self):
        c = Circle()
        s = Square()
        self.play(Transform(c, s))
        self.wait(1)
                  