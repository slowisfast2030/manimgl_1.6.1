from manimlib import *

"""
圆环和长条都可以实现
但是动画效果不好
需要研究下怎样对齐点集
"""
class test(Scene):
    def construct(self):
        ring = self.get_ring(1, 0.2).rotate(PI/2)
        self.play(FadeIn(ring))

        unwrapped = self.get_unwrapped(ring).shift(DOWN*2) 
        # 点集没有对齐。所以动画很难看
        self.play(Transform(ring, unwrapped))
    
    def get_ring(self, radius, dR, color = RED):
        ring = Circle(radius = radius + dR).center()
        inner_ring = Circle(radius = radius).center()
        # 点睛之笔。特别注意点集的顺序。
        inner_ring.rotate(PI, RIGHT)
        ring.append_vectorized_mobject(inner_ring)
        ring.set_stroke(width = 0.5)
        ring.set_fill(color,1)
        ring.R = radius 
        ring.dR = dR
        return ring
    
    def get_unwrapped(self, ring:VMobject, to_edge = LEFT, **kwargs):
        R = ring.R
        R_plus_dr = ring.R + ring.dR
        n_anchors = ring.get_num_curves()
        # print(n_anchors)
        # print(n_anchors//2)
        # 如果manim没有自己想要的形状，可以自己构造点集
        result = VMobject()
        result.set_points_as_corners([
            interpolate(np.pi*R_plus_dr*LEFT,  np.pi*R_plus_dr*RIGHT, a)
            for a in np.linspace(0, 1, n_anchors//2)
        ]+[
            interpolate(np.pi*R*RIGHT+ring.dR*UP,  np.pi*R*LEFT+ring.dR*UP, a)
            for a in np.linspace(0, 1, n_anchors//2)
        ])
        result.set_style(
            stroke_color = ring.get_stroke_color(),
            stroke_width = ring.get_stroke_width(),
            fill_color = ring.get_fill_color(),
            fill_opacity = ring.get_fill_opacity(),
        )

        return result


class CircleToSquare(Scene):
    def construct(self):
        # Create a circle
        circle = Circle().scale(2)
        circle.set_fill(PINK, opacity=0.5).shift(LEFT*3)

        # Iterate over the points of the circle and add dots with labels
        for index, point in enumerate(circle.get_points()):
            dot = Dot(point)
            label = Text(str(index), font_size=24).next_to(dot, DOWN, buff=0.1)
            self.add(dot, label)

        # Create a square
        square = Square().scale(2).rotate(-PI/4)
        square.set_fill(YELLOW, opacity=0.5).shift(RIGHT*3)

        # Iterate over the points of the square and add dots with labels
        for index, point in enumerate(square.get_points()):
            dot = Dot(point)
            label = Text(str(index), font_size=24).next_to(dot, DOWN, buff=0.1)
            self.add(dot, label)

        # Transform the circle into the square
        self.play(Transform(circle, square))

        # Keep the final shape displayed
        self.wait(2)

