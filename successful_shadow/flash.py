from manimlib import *

class ShowFlash(Scene):
    def construct(self):
        dot = Dot(ORIGIN, color=YELLOW)
        dot.set_stroke(width=0)
        dot.set_fill(opacity=0)
        self.play(Flash(dot, flash_radius=0.8, line_length=0.6, run_time=2))
        self.wait()