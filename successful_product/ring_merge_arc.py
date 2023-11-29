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
        outer_circle = Circle(radius=3).get_points()[:3]
        inner_circle = Circle(radius=2).get_points()[:3]