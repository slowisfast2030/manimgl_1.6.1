import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

class test(Scene):
    def construct(self):

        colors = color_gradient([BLUE, GREEN], 3)
        pis = [PiCreature(color=color).scale(0.8) for color in colors]
        pis[1].set_color(GREY_BROWN).scale(1.3)
        pi_group = VGroup(*pis)
        pi_group.arrange(RIGHT)
        self.play(FadeIn(pi_group))
        self.play(pis[1].says("today, we will leran a new word, abandon!"))
        self.play(pis[1].debubble())
        self.wait()
        pi_group_copy = pi_group.shift(DOWN*5).copy()
        self.play(FadeOut(pi_group),FadeIn(pi_group_copy), run_time=2)


        word = Text("Abandon").scale(2).shift(UP*6.5+LEFT*2.2).set_color(RED)
        self.play(Write(word))

        pis[0].look_at(LEFT)
        pis[1].shrug()
        self.wait()

        meaning_1 = Text("V-T If you abandon a place, thing, or person, you\n        leave the place, thing, or person permanently or for a long time, \n        especially when you should not do so.", 
                         font_size=40,
                         t2c={'abandon': BLUE, 'V-T': RED})
        meaning_1.next_to(word, DOWN).shift(RIGHT*2.2)
        self.play(FadeIn(meaning_1))
        sentence_1 = Text("\n•  He claimed that his parents had abandoned him.", font_size=40)
        sentence_1.next_to(meaning_1, DOWN)
        self.play(Write(sentence_1))

        meaning_2 = Text("V-T If you abandon an activity or piece of work, you\n        stop doing it before it is finished.", 
                         font_size=40,
                         t2c={'abandon': BLUE, 'V-T': RED})
        meaning_2.next_to(meaning_1, 4*DOWN)
        self.play(FadeIn(meaning_2))
        sentence_2 = Text("\n•  The authorities have abandoned any attempt to\n distribute food in an orderly fashion. ", font_size=40)
        sentence_2.next_to(meaning_2, DOWN)
        self.play(Write(sentence_2))

        meaning_3 = Text("V-T  If you abandon an idea or way of thinking, you \n        stop having that idea or thinking in that way.", 
                         font_size=40,
                         t2c={'abandon': BLUE, 'V-T': RED})
        meaning_3.next_to(meaning_2, 6*DOWN)
        self.play(FadeIn(meaning_3))
        sentence_3 = Text("\n•  Logic had prevailed and he had abandoned the\n idea.", font_size=40)
        sentence_3.next_to(meaning_3, DOWN)
        self.play(Write(sentence_3))

        frame = self.camera.frame
        def update_frame(frame, dt):
            frame.increment_theta(-0.1 * dt)
        self.play(frame.animate.reorient(40, 70), run_time=2)
        frame.add_updater(update_frame)
        self.wait(3)



        
        