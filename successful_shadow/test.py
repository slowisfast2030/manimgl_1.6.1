from manimlib import *

class test(ThreeDScene):
    def construct(self):
        frame = self.camera.frame
        frame.reorient(-20, 80)
        axes = ThreeDAxes()
        self.add(axes)
        self.wait()