from manimlib import *

class FrameTest(Scene):
    def construct(self):
        c = Circle()
        s = Square()
        frame = self.camera.frame
        frame.set_height(20)

        self.play(Transform(c, s))
