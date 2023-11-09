from manimlib import *

class test(Scene):
    def construct(self):
        rect = Rectangle().set_color(BLUE)
        ball_1 = Dot().set_color(RED)
        ball_2 = Dot().set_color(YELLOW)
        self.play(
            ShowCreation(rect, run_time=2),
            UpdateFromFunc(ball_1, lambda m: m.move_to(rect.get_end())),
            ball_2.animate.move_to(rect.get_end())              
        )

class test1(Scene):
    def construct(self):
        rect = Rectangle().set_color(BLUE)
        ball_1 = Dot().set_color(RED)
        self.add(rect, ball_1)
        ball_1.add_updater(lambda m: m.move_to(rect.get_end()))
        self.play(
            ShowCreation(rect, run_time=2)         
        )