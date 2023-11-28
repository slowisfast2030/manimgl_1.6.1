from manimlib import *

class test(Scene):
    def construct(self):
        # 创建一个圆形
        circle = Circle()
        circle.set_fill(PINK, opacity=0.5)

        # 创建一个正方形
        square = Square()
        square.set_fill(YELLOW, opacity=0.5)

        # 将正方形放置在圆形的位置
        square.shift(DOWN*3)

        # 展示圆形
        self.add(circle) 

        # 将圆形变成正方形
        self.play(ReplacementTransform(circle, square))
        #self.play(Transform(circle, square))
        self.wait(1)
