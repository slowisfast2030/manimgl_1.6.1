import sys
sys.path.append("/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-characters")

from manimlib import *
from alphabet_creature import AlphabetCreature

class test(Scene):
    def construct(self):
        a = AlphabetCreature("\Omega")
        self.add(a)
        print(a.submobjects)