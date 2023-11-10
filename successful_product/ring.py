from manimlib import *

"""
锯齿状非常明显
是不是cario升级为opengl后的遗留问题
"""
class test(Scene):
    def construct(self):
        radius = 2
        dR = 0.2

        outer_ring = Circle(radius=radius + dR)
        inner_ring = Circle(radius=radius)

        # 使用差运算代替 append_vectorized_mobject
        ring = Difference(outer_ring, inner_ring)
        ring.set_stroke(width=0)  # 设置描边宽度
        ring.set_fill(color=GREEN, opacity=1.0)  # 设置填充颜色和不透明度

        self.add(ring)
        
        