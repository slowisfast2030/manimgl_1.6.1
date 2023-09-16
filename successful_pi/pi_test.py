import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

class test(Scene):
    def construct(self):
        pi = PiCreature(color=BLUE_E)
        print(pi.parts)
        self.add(pi.parts[0], pi.parts[2])

        self.add(pi.submobjects[0].copy().shift(DOWN))