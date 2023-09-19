import sys
sys.path.append("/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-characters")

from manimlib import *
from alphabet_creature import AlphabetCreature

class test(Scene):
    def construct(self):
        a = AlphabetCreature("Q", start_corner=ORIGIN+LEFT*2)
        self.add(a)
        print(a.submobjects)

class test1(Scene):
    def construct(self):
        a = SingleStringTex("A")
        self.add(a)


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
