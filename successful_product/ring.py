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
        print(outer_ring.insert_n_curves_to_point_list(10, outer_ring.get_points()))
        # 创建内圆
        inner_ring = Circle(radius=radius)
        inner_ring_2 = VMobject().set_points(inner_ring.insert_n_curves_to_point_list(10, inner_ring.get_points()))

        # 使用差运算代替 append_vectorized_mobject
        # ring = Difference(outer_ring_2, inner_ring_2)
        # ring.set_stroke(width=0)  # 设置描边宽度
        # ring.set_fill(color=GREEN, opacity=1.0)  # 设置填充颜色和不透明度

        # self.add(ring)
        self.add(inner_ring_2)
        