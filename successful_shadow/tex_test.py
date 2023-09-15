from manimlib import *

class temp1(Scene):
    def construct(self):
        t = TexText("A B", math_mode=False)

        items = BulletedList(
            "Recap",
            "Intuitive walkthrough",
            "Derivatives in \\\\ computational graphs"
            )
        
        pi = SingleStringTex("\Omega")
        pi = SingleStringTex("\partial")
        pi = SingleStringTex("\pi")
        vm = VMobject()
        vm.set_points(pi.get_all_points()[:159])
        vm.scale(20)
        self.add(vm.set_fill(GREEN, .0))
        for point in vm.get_points():
            dot = Dot(point).scale(0.5).set_color(RED)
            self.add(dot) 
        

class temp(Scene):
    def construct(self):
        to_isolate = ["+", "="]
        tex_to_color_map = {
                "A": BLUE,
                "B": TEAL,
                "C": GREEN,
            }
        #tex_to_color_map={}
        
        c = Tex("A^2","+B^2","=C^2", isolate=to_isolate, arg_separator="", tex_to_color_map=tex_to_color_map)
        c.set_color_by_tex("2", RED_D)

        c.slice_by_tex(start_tex="+", stop_tex="C").set_color(YELLOW_B)

        for smob in c.submobjects:
            print(smob, smob.tex_string)

        subsubmob = c.submobjects[0].submobjects[0]
        self.add(c.copy().shift(LEFT*2))

        vm = VMobject()
        vm.set_points(subsubmob.get_points())
        vm.scale(20).shift(RIGHT*3)
        self.add(vm)
        for point in vm.get_points():
            dot = Dot(point).scale(0.5).set_color(RED)
            self.add(dot)
        
        
        


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
        print("family 0: ", c.family[0])

        print("\nsubmobjects")
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