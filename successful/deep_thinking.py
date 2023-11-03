from manimlib import *

class test(Scene):
    def construct(self):
        c = Circle().shift(LEFT)
        s = Square().shift(RIGHT)

        partial_circle = Arc(start_angle=0, angle=PI)
        # 需要这里起始点的顺序，否则会出现不合理的插值结果
        line1 = Line(RIGHT*2, LEFT*2).shift(LEFT*3)
        line2 = Line(LEFT*2, RIGHT*2).shift(LEFT*3)

        self.play(Transform(partial_circle, line1))