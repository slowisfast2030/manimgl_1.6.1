from manimlib import *

"""
研究点集的对齐问题

在manimgl中:
如果内外环的半径相差很小, 会渲染错误
研究下, 为什么会这样?
个人猜想: 三角剖分

在manimce中:
可以完美解决这个问题

根源:
manimgl的渲染后端: opengl
manimce的渲染后端: cairo(如果选opengl, 代码都会报错)

执行:
manimgl ring_merge_point_align.py test -o -s
"""

class CustomVMobject(VMobject):
    def __str__(self):
        return "Custom ring"

class test(Scene):
    def construct(self):
        """
        直接用两个圆的点集来构造
        """
        vm = CustomVMobject()
        if str(vm) == "Custom ring":
            print("继承成功！")
        """
        经过测试发现
        如果内外环的半径相差很小, 三角剖分返回的索引不一样

        只要将正确的三角剖分索引传递给内外环相差较小的vmobject
        就可以解决这个问题
        需要找到这个索引起作用的地方
        """
        outer_radius = 3
        inner_radius = 2
        vm.R = outer_radius
        vm.dR = outer_radius - inner_radius
        
        
        """
        分别取内外环的点集
        """
        outer_circle = Circle(radius=outer_radius).rotate(PI/2).get_points()[:3]
        inner_circle = Circle(radius=inner_radius).rotate(PI/2).get_points()[:3][::-1]

        """
        在两段圆弧的端点处进行插值
        """
        line1 = [outer_circle[-1], 
                 #interpolate(outer_circle[-1], inner_circle[0], 0.3),
                 interpolate(outer_circle[-1], inner_circle[0], 0.5),
                 inner_circle[0]]
        
        line2 = [inner_circle[-1],
                #interpolate(inner_circle[-1], outer_circle[0], 0.3),
                interpolate(inner_circle[-1], outer_circle[0], 0.5),
                outer_circle[0]]
        
        # 两个圆的点集拼接起来
        points_to_add = list(outer_circle) + line1 + list(inner_circle) + line2
        vm.append_points(points_to_add)

        vm.set_fill(GREEN, 1)
        vm.set_stroke(width=1)
        vm.move_to(ORIGIN)
        vm.rotate(-PI/8).rotate(PI)
        self.add(vm)

        """
        至关重要！
        如果不加这一句, 着色会错误！即使内外环的半径相差很大
        但是对于cairo后端, 不需要这个
        """
        print(vm.get_triangulation())
        
        rec =  self.get_unwrapped(vm).scale(0.5).shift(DOWN*2.5)
        self.add(rec)

        for index, point in enumerate(vm.get_points()):
            dot = Dot(point)
            label = Text(str(index), font_size=24).next_to(dot, point-vm.get_center(), buff=0.1)
            self.add(dot, label)

        for index, point in enumerate(rec.get_points()):
            dot = Dot(point)
            label = Text(str(index), font_size=24).next_to(dot, UP, buff=0.1)
            self.add(dot, label)

        self.play(Transform(vm, rec))
        self.wait()
    
    def get_unwrapped(self, ring:VMobject, to_edge = LEFT, **kwargs):
        R = ring.R
        R_plus_dr = ring.R + ring.dR
        n_anchors = ring.get_num_curves()
        
        # 如果manim没有自己想要的形状，可以自己构造点集
        result = VMobject()
        result.set_points_as_corners([
            interpolate(np.pi*R_plus_dr*LEFT,  np.pi*R_plus_dr*RIGHT, a)
            for a in np.linspace(0, 1, n_anchors//2)
        ]+[
            interpolate(np.pi*R*RIGHT+ring.dR*UP,  np.pi*R*LEFT+ring.dR*UP, a)
            for a in np.linspace(0, 1, n_anchors//2)
        ])

        line = [result.get_points()[-1], 
                interpolate(result.get_points()[-1], result.get_points()[0], 0.5),
                #interpolate(result.get_points()[-1], result.get_points()[0], 0.6),
                result.get_points()[0]] 
        result.append_points(line)

        result.set_style(
            stroke_color = ring.get_stroke_color(),
            stroke_width = ring.get_stroke_width(),
            fill_color = ring.get_fill_color(),
            fill_opacity = ring.get_fill_opacity(),
        )

        return result


