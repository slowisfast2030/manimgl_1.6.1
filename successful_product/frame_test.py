from manimlib import *

class FrameTest(Scene):
    def construct(self):
        c = Circle()
        s = Square()

        frame = self.camera.frame
        frame.set_height(16)
        frame.move_to(np.array([0,0,-16]))
        location = frame.get_implied_camera_location()
        print(location)

        frame_copy = frame.copy()
        frame_copy.scale(0.5).shift(UP+RIGHT)
        self.add(frame_copy)

        self.play(Transform(c, s))
