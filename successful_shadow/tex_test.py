from manimlib import *


class TextExample(Scene):
    def construct(self):
        # To run this scene properly, you should have "Consolas" font in your computer
        # for full usage, you can see https://github.com/3b1b/manim/pull/680
        text = Text("Here is a text", font="Consolas", font_size=90)
        difference = Text(
            """
            The most important difference between Text and TexText is that\n
            you can change the font more easily, but can't use the LaTeX grammar
            """,
            font="Arial", font_size=24,
            # t2c is a dict that you can choose color for different text
            t2c={"Text": BLUE, "TexText": BLUE, "LaTeX": ORANGE}
        )
        VGroup(text, difference).arrange(DOWN, buff=1)
        self.play(Write(text))
        self.play(FadeIn(difference, UP))
        self.wait(3)

        fonts = Text(
            "And you can also set the font according to different words",
            font="Arial",
            t2f={"font": "Consolas", "words": "Consolas"},
            t2c={"font": BLUE, "words": GREEN}
        )
        fonts.set_width(FRAME_WIDTH - 1)
        slant = Text(
            "And the same as slant and weight",
            font="Consolas",
            t2s={"slant": ITALIC},
            t2w={"weight": BOLD},
            t2c={"slant": ORANGE, "weight": RED}
        )
        VGroup(fonts, slant).arrange(DOWN, buff=0.8)
        self.play(FadeOut(text), FadeOut(difference, shift=DOWN))
        self.play(Write(fonts))
        self.wait()
        self.play(Write(slant))
        self.wait()

class temp2(Scene):
    def construct(self):
        difference = Text(
            """
            The most important difference between Text and TexText is that\n
            you can change the font more easily, but can't use the LaTeX grammar
            """,
            font="Arial", font_size=24,
            # t2c is a dict that you can choose color for different text
            t2c={"Text": BLUE, "TexText": BLUE, "LaTeX": ORANGE}
        )
        self.add(difference)


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
        vm.set_points(pi.get_all_points())
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