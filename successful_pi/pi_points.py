import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext_new import *

class test(Scene):
    def construct(self):
        # p = NumberPlane()
        # self.add(p)

        modes = ('plain', 'happy', 'sad')
        pi = PiCreature(mode='plain')
        mob = pi[0][0][0]
        self.add(mob)
        print(mob.get_all_points())