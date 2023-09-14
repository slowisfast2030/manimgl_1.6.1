from manimlib import *

class test(Scene):
    def construct(self):
        #to_isolate = ["A^2", "B^2", "C^2", "=", "+"]
        #to_isolate = ["A^2", "B^2", "C^2"]
        #to_isolate = ["A^2", "C^2"]
        to_isolate = ["+"]

        # Tex类传入的文本中间的空格会被处理, 多个空格会被合并为一个空格
        # 传入isolate后，文本会被isolate中给定的字符进行分隔
        c = Tex("A^2 + B^2 = C^2", isolate=to_isolate)
    
        for index, smob in  enumerate(c.submobjects):
            print(f"Index {index}: Value {smob}      String: {smob.tex_string}")
            self.add(smob.shift(0.5*index*DOWN))
            #self.add(smob)
        
class test1(Scene):
    def construct(self):
        c = SingleStringTex("A  BC")
        for index, smob in  enumerate(c.submobjects):
            print(f"Index {index}: Value {smob}")
            self.add(smob.copy().shift(index*RIGHT).shift(UP*3))

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