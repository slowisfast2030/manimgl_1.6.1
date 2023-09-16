import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

LEFT_EYE_INDEX: int = 0
RIGHT_EYE_INDEX: int = 1
LEFT_PUPIL_INDEX: int = 2
RIGHT_PUPIL_INDEX: int = 3
BODY_INDEX: int = 4
MOUTH_INDEX: int = 5

class test(Scene):
    def construct(self):
        pi = PiCreature(color=BLUE_E)
        parts = pi.parts

        original_irises=VGroup(parts[LEFT_EYE_INDEX], parts[RIGHT_EYE_INDEX])
        original_pupils=VGroup(parts[LEFT_PUPIL_INDEX], parts[RIGHT_PUPIL_INDEX])
        self.add(original_irises)
        #self.add(original_pupils)