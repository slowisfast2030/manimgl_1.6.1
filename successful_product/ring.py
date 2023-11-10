from manimlib import *

class test(Scene):
    def construct(self):
        radius = 2
        dR = 0.2

        outer_ring = Circle(radius=radius + dR)
        # 创建内圆
        inner_ring = Circle(radius=radius)
        inner_ring.rotate(PI, RIGHT)  # 使用 PI 代替 np.pi

        # 使用差运算代替 append_vectorized_mobject
        ring = Difference(outer_ring, inner_ring)
        ring.set_stroke(width=0)  # 设置描边宽度
        ring.set_fill(color=GREEN, opacity=1.0)  # 设置填充颜色和不透明度

        self.add(ring)