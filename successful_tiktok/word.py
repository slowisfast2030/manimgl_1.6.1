import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

class test(Scene):
    def construct(self):

        pi2 = PiCreature(color=BLUE_E)
        self.add(pi2)
        pi2.move_to(DOWN*2)
        self.wait()

        pi2.look_at(LEFT)
        self.wait()

        pi2.shrug()
        self.wait()