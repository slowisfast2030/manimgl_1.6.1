from manimlib import *

"""
将circle的点集设置为顺时针
会出现奇怪的渲染效果

为了正常渲染
需要执行: ring.get_triangulation() 

manimgl ring_merge_anticlock.py test -o -s
"""
class test(Scene):
    def construct(self):
        ring = Circle(radius = 2, n_components=8).center()
        ring.set_stroke(width = 0.5)
        ring.set_fill(RED,0.5)

        # 将ring的点集变为顺时针
        ring.rotate(PI, RIGHT)

        print(ring.get_triangulation())

        for index, point in enumerate(ring.get_points()):
            dot = Dot(point)
            label = Text(str(index), font_size=24).next_to(dot, point-ring.get_center(), buff=0.1)
            
            self.add(dot, label)

        self.add(ring)
