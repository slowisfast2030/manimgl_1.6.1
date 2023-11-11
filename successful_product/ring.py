from manimlib import *

"""
锯齿状非常明显
是不是cario升级为opengl后的遗留问题

可以通过增加内环和外环的分段数来减少锯齿
"""
class test(Scene):
    def construct(self):
        radius = 2
        dR = 0.2

        outer_ring = Circle(radius=radius + dR, n_components=500)
        inner_ring = Circle(radius=radius, n_components=500)
        inner_ring.rotate(PI, RIGHT)

        # 使用差运算代替 append_vectorized_mobject
        ring = Difference(outer_ring, inner_ring)
        #ring = Annulus(inner_radius=radius, outer_radius=radius+dR, n_components=500, mark_paths_closed=True)
        ring.set_stroke(width=0)  # 设置描边宽度
        ring.set_fill(color=GREEN, opacity=1.0)  # 设置填充颜色和不透明度

        self.add(ring)
        #self.play(ShowCreation(ring))

        # rec = Rectangle(width=10, height=0.2).set_color(BLUE_E).set_opacity(0.5)
        # self.play(Transform(ring, rec))
        
        