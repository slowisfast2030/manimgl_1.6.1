import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

class test(Scene):
    def construct(self):

        colors = color_gradient([BLUE, GREEN], 2)
        pis = [PiCreature(color=color).scale(0.8) for color in colors]
        pis[1].set_color(GREY_BROWN).scale(1.3).shift(UP*1.2)
        pi_group = VGroup(*pis)
        pi_group.arrange(RIGHT, buff=0.9)
        self.play(FadeIn(pi_group))
        self.play(pis[1].says("today, we will \nleran abandon!"))
        self.play(pis[1].debubble())
        self.wait()
        pi_group_copy = pi_group.shift(DOWN*5).copy()
        self.play(FadeOut(pi_group),FadeIn(pi_group_copy), run_time=2)


        word = Text("Abandon").scale(2).shift(UP*6.5+LEFT*2.2).set_color(BLUE)
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

        image_boy = ImageMobject("dall-boy.png").rotate(PI/2).scale(1.5).rotate(-PI/2)

        self.play(pis[1].says("hi"),
                  #FadeIn(image_boy)
                  )
        



        # word_fix = Text("Abandon", t2w={"Abandon": BOLD}).scale(3).set_color(RED).shift(UP*2)
        # word_fix.fix_in_frame()
        # pis[0].fix_in_frame()
        # pis[1].fix_in_frame()
        # pis[2].fix_in_frame()

        # frame = self.camera.frame
        # def update_frame(frame, dt):
        #     frame.increment_theta(-0.1 * dt)
        # self.play(frame.animate.reorient(30, 70),Write(word_fix), run_time=2)
        # frame.add_updater(update_frame)

        # self.wait(7)



        
        