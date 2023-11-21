from manimlib import *

class test(Scene):
    def construct(self):
        cube = Cube().scale(2)
        self.add(cube)

        frame = self.camera.frame
        def update_frame(frame, dt):
            frame.increment_theta(-0.1 * dt)

        self.play(frame.animate.reorient(30, 70), run_time=2)
        frame.add_updater(update_frame)
        self.wait(3)