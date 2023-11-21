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
        self.play(FadeOut(pi_group),FadeIn(pi_group_copy), run_time=1)


        word = Text("Abandon").scale(2).shift(UP*6.5+LEFT*2.2).set_color_by_gradient(RED, BLUE)
        self.play(Write(word))

        pis[0].look_at(LEFT)
        pis[1].shrug()
        self.wait()

        meaning_1 = Text("V-T If you abandon a place, thing, or person, you\n        leave the place, thing, or person permanently or for a long time, \n        especially when you should not do so.", 
                         font_size=40,
                         t2c={'abandon': BLUE, 'V-T': RED})
        meaning_1.next_to(word, DOWN*2).shift(RIGHT*2.2)
        self.play(FadeIn(meaning_1))
        sentence_1 = Text("\n•  He claimed that his parents had abandoned him.", font_size=40, t2c={'abandoned': BLUE})
        sentence_1.next_to(meaning_1, DOWN*2)
        self.play(Write(sentence_1))

        image_boy = ImageMobject("dall-boy.png").rotate(PI/2)\
                                                .scale(2)\
                                                .set_opacity(1)\
                                                .rotate(-PI/2)\
                                                .shift(DOWN*2.5)
        image_boy.target = image_boy.copy().set_opacity(1)

        self.play(pis[0].thinks("what a lonely boy!"),
                  run_time=1,
                  )
        
        self.play(FadeIn(image_boy, rate_func=slow_into), run_time=2)
        self.wait(2)

        self.clear()

        image_path = ImageMobject("dall-path.png").scale(1.5)
        image_house = ImageMobject("dall-house.png").scale(1.5)
        image_boy = ImageMobject("dall-boy.png").rotate(PI/2).scale(1.5)

        radius = image_path.get_height()/2
        image_path.move_to(radius * OUT)
        image_house.move_to(radius * OUT)
        image_boy.move_to(radius * OUT)

        result = [image_path]
        # result.extend([
        #     image_path.copy().rotate(PI / 2, axis=vect, about_point=ORIGIN)
        #     for vect in compass_directions(4)
        # ])
        result.append(image_house.copy().rotate(PI/2, RIGHT, about_point=ORIGIN))
        result.append(image_boy.copy().rotate(PI/2, UP, about_point=ORIGIN))
        result = Group(*result).space_out_submobjects(1.01)
        self.add(*result)   

        word_fix = Text("Abandon", t2w={"Abandon": BOLD}).scale(3).set_color_by_gradient(RED, BLUE).shift(UP*3)
        word_fix.fix_in_frame()

        frame = self.camera.frame
        def update_frame(frame, dt):
            frame.increment_theta(-0.1 * dt)

        self.play(frame.animate.reorient(60, 70),Write(word_fix), run_time=2)
        frame.add_updater(update_frame)

        self.wait(5)
        