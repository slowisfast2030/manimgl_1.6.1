import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

class test(Scene):
    def construct(self):
        pi = PiCreature(color=BLUE_E)
        print(pi.parts)
        for index, part in enumerate(pi.parts):
            self.add(part.shift(index*RIGHT))