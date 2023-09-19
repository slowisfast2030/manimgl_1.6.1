import sys
sys.path.append("/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-characters")

from manimlib import *
from alphabet_creature import AlphabetCreature

class test(Scene):
    def construct(self):
        a = AlphabetCreature("\pi", flip_at_start=False, color=RED)
        aa = a.copy()
        self.add(a)
        self.wait()
        print(a.submobjects)
        a.look(LEFT)
        a.blink()
        self.wait(0.2)
        self.add(aa)
        self.wait(1)

class test_letter(Scene):
    def construct(self):
        a = AlphabetCreature("\pi", flip_at_start=False, color=TEAL)
        self.add(a)
        self.play(a.change("\pi"))


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
