import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

class test(Scene):
    def construct(self):

        colors = color_gradient([BLUE, GREEN], 3)
        pis = [PiCreature(color=color).scale(0.8) for color in colors]
        pi_group = VGroup(*pis)
        pi_group.arrange(RIGHT).shift(DOWN*5)
        self.add(pi_group)
        self.wait()
        word = Text("Abandon").scale(2).shift(UP*6.5+LEFT*2.2).set_color(RED)
        self.play(Write(word))

        pis[0].look_at(LEFT)
        pis[1].shrug()
        self.wait()

        meaning_1 = Text("V-T If you abandon a place, thing, or person, you leave the place, thing, or person permanently or for a long time, especially when you should not do so.         •  He claimed that his parents had abandoned him.")
        meaning_1.next_to(word, DOWN)
        self.add(meaning_1)
        self.wait()
        