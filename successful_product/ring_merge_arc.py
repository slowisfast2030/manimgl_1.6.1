from manimlib import *

class test(Scene):
    def construct(self):
        """
        一个很惊喜的发现:
        第4个点和第10个点可以采用插值的方式得到
        也可以直接使用第3个点和第9个点
        """
        vm = VMobject()
        outer_circle = Circle(radius=3).get_points()[:3]
        inner_circle = Circle(radius=2).get_points()[:3]

        zero = outer_circle[0].copy()
        first = outer_circle[1].copy() 
        second = outer_circle[2].copy()

        three = outer_circle[2].copy()
        five = inner_circle[2].copy() 
        #four = interpolate(three, five, 0.5)
        four = three.copy()

        six = inner_circle[2].copy()
        seven = inner_circle[1].copy() 
        eight = inner_circle[0].copy()

        nine = inner_circle[0].copy()
        eleven = outer_circle[0].copy()
        #ten = interpolate(nine, eleven, 0.5)  
        ten = eleven.copy()
        

        
        # 合并点并添加到 VMobject
        points_to_add = [zero, first, second, 
                         three, four, five, 
                         six, seven, eight,
                         nine, ten, eleven]
        
         
        vm.append_points(points_to_add)
        vm.set_fill(BLUE, 0.2)
        vm.set_stroke(width=1)
        self.add(vm)
        print(vm.get_triangulation())

        for index, point in enumerate(vm.get_points()):
            dot = Dot(point)
            if index < 21:
                label = Text(str(index), font_size=24).next_to(dot, DOWN, buff=0.1)
            else:
                label = Text(str(index), font_size=24).next_to(dot, UP, buff=0.1)
            self.add(dot, label)

        rec = Rectangle(width=4, height=1).set_fill(BLUE, 0.2).rotate(-PI/2)
        for index, point in enumerate(rec.get_points()):
            dot = Dot(point)
            if index < 21:
                label = Text(str(index), font_size=24).next_to(dot, DOWN, buff=0.1)
            else:
                label = Text(str(index), font_size=24).next_to(dot, UP, buff=0.1)
            self.add(dot, label)

        self.play(Transform(vm, rec))
        self.wait()


class test_elegent(Scene):
    def construct(self):
        """
        直接用两个圆的点集来构造
        """
        vm = VMobject()
        outer_circle = Circle(radius=3).rotate(PI/2).get_points()[:21]
        inner_circle = Circle(radius=2).rotate(PI/2).get_points()[:21][::-1]
        # print(type(outer_circle))
        # print(type(inner_circle))
        # print(outer_circle)
        # print(inner_circle)

        """
        在两段圆弧的端点处进行插值
        """
        line1 = [outer_circle[-1], 
                 interpolate(outer_circle[-1], inner_circle[0], 0.5),
                 inner_circle[0]]
        
        line2 = [inner_circle[-1],
                interpolate(inner_circle[-1], outer_circle[0], 0.5),
                outer_circle[0]]
        
        points_to_add = list(outer_circle) + line1 + list(inner_circle) + line2
        #points_to_add = list(outer_circle) + line1 + list(inner_circle)
        vm.append_points(points_to_add)
        vm.set_fill(BLUE, 0.2)
        vm.set_stroke(width=1)
        self.add(vm)
        print(vm.get_triangulation())
        vm.R = 3
        vm.dR = 1
        vm.shift(UP).scale(0.8)

        for index, point in enumerate(vm.get_points()):
            dot = Dot(point)
            
            label = Text(str(index), font_size=24).next_to(dot, UP, buff=0.1)
            self.add(dot, label)


        rec =  self.get_unwrapped(vm).scale(0.5).shift(DOWN*2.5)
        for index, point in enumerate(rec.get_points()):
            dot = Dot(point)
            
            label = Text(str(index), font_size=24).next_to(dot, UP, buff=0.1)
            self.add(dot, label)
        self.add(rec)   

        #self.play(Transform(vm, rec))
        self.wait()    

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