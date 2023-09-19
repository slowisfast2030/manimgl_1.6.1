import sys
sys.path.append("/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-characters")

from manimlib import *
from alphabet_creature import AlphabetCreature

class test(Scene):
    def construct(self):
        a = AlphabetCreature("\pi", flip_at_start=True)
        self.add(a)
        print(a.submobjects)

class test1(Scene):
    def construct(self):
        a = SingleStringTex("AB")
        self.add(a)
        print(a.submobjects)


class MyCircle(Circle):
    CONFIG = {
        "color": YELLOW_A
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class test2(Scene):
    def construct(self):
        c = MyCircle()
        self.add(c)
