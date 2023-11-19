from manimlib import *

class FrameTest(Scene):
    def construct(self):
        c = Circle().move_to([0,0,10])
        s = Square()
        frame = self.camera.frame
        frame.set_height(8)
        frame.move_to(np.array([0,0,0]))

        frame_copy = frame.copy()
        frame_copy.scale(0.5).shift(UP+RIGHT)
        self.add(frame_copy)

        self.play(Transform(c, s))
