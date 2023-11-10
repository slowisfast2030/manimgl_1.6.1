from manimlib import *

class test(ThreeDScene):
    def construct(self) -> None:
        frame = self.camera.frame
        frame.reorient(20, 70)
        def update_frame(frame, dt):
            frame.increment_theta(-0.2 * dt)
        frame.add_updater(update_frame)

        