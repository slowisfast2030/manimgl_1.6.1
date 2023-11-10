from manimlib import *

class test(Scene):
    def construct(self):
        frame = self.camera.frame
        frame.reorient(20, 70)
        def update_frame(frame, dt):
            frame.increment_theta(-0.2 * dt)
        frame.add_updater(update_frame)
        
        line = Line3D(LEFT, RIGHT, color=RED)
        self.add(line)
        self.wait(3)