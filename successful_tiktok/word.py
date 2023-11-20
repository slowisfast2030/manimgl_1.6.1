import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

class test(Scene):
    def construct(self):

        colors = color_gradient([BLUE, GREEN], 3)
        pis = [PiCreature(color=color).scale(0.5) for color in colors]
        pi_group = VGroup(*pis)
        pi_group.arrange(RIGHT).shift(DOWN)
        self.add(pi_group)
        self.wait()

        # pi2.look_at(LEFT)
        # self.wait()

        # pi2.shrug()
        # self.wait()