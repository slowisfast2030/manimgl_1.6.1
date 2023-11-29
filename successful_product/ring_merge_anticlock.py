from manimlib import *

"""
圆环和长条都可以实现
但是动画效果不好
需要研究下怎样对齐点集
"""
class test(Scene):
    def construct(self):
        ring = Circle(radius = 2).center()
        ring.set_stroke(width = 0.5)
        ring.set_fill(RED,0.5)

        # 将ring的点集变为顺时针
        ring.rotate(PI, RIGHT)

        for index, point in enumerate(ring.get_points()):
            dot = Dot(point)
            if index < 24:
                label = Text(str(index), font_size=24).next_to(dot, point-ring.get_center(), buff=0.1)
            else:
                label = Text(str(index), font_size=24).next_to(dot, ring.get_center()-point, buff=0.1)
                pass
            self.add(dot, label)

        self.add(ring)
