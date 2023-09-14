from manimlib import *

class test(Scene):
    def construct(self):
        #to_isolate = ["A^2", "B^2", "C^2", "=", "+"]
        #to_isolate = ["A^2", "B^2", "C^2"]
        #to_isolate = ["A^2", "C^2"]
        to_isolate = ["+", "="]

        # 传入isolate后，文本会被isolate中给定的字符进行分隔
        # 不论传入几个str, 都会合并成一个
        # 然后根据isolate, 将合并后的str分割
        # 分割后的每一部分str传入SingleStringTex
        c = Tex("A^2","+B^2","=C^2", isolate=to_isolate, arg_separator="")
        print(c.family[0])
        for index, smob in  enumerate(c.submobjects):
            print(f"Index {index}: Value {smob}      String: {smob.tex_string}")
            self.add(smob.copy().shift(0.25*index*DOWN))
            for i, j in enumerate(smob.submobjects):
                print(i,j)

        
class test1(Scene):
    def construct(self):
        c = SingleStringTex("A  BC", organize_left_to_right=False)
        #print(c.family)
        for index, smob in  enumerate(c.submobjects):
            print(f"Index {index}: Value {smob}")
            self.add(smob.copy().shift(UP*3))

        #points = c.submobjects[0].get_points()
        points = c.get_all_points()
        vm = VMobject()
        vm.set_points(points)
        vm.scale(12).set_fill(GREEN, 0)
        self.add(vm)

        for point in vm.get_points():
            dot = Dot(point).set_color(RED).scale(0.5)
            self.add(dot)
        
        #self.add(c.submobjects[0].shift(LEFT*3))

class test2(Scene):
    def construct(self):
        c = Text("QW")
        print(c.submobjects)

        #points = c.submobjects[0].get_points()
        points = c.get_all_points()
        vm = VMobject()
        vm.set_points(points)
        vm.scale(12).set_fill(GREEN, 0)
        self.add(vm)

        for point in vm.get_points():
            dot = Dot(point).set_color(RED).scale(0.5)
            self.add(dot)