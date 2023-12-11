from manim import *

class test(Scene):
    def construct(self):
        # # 设DA=x，则DE=x, BD=4-x
        # text1 = Tex(r"设 DA=x, 则 DE=x, BD=4-x").next_to(ORIGIN, DOWN, buff=2).scale(0.7)
        # self.play(Write(text1))
        # self.wait()

        # # 勾股定理
        # text2 = Tex(r"在直角三角形DEB中, 由勾股定理可得:").next_to(text1, DOWN, buff=0.5).scale(0.7)
        # self.play(Write(text2))
        # self.wait()

        # # Here, we continue using MathTex for purely mathematical expressions
        # text3 = MathTex(r"BD^2=DE^2+BD^2").next_to(text2, DOWN, buff=0.5).scale(0.7)
        # self.play(Write(text3))
        # self.wait()

        # text4 = MathTex(r"(3-x)^2=(4-3)^2 + x^2").next_to(text3, DOWN, buff=0.5).scale(0.7)
        # self.play(Write(text4))
        # self.wait()

        # text5 = MathTex(r"x=\frac{4}{3}").next_to(text4, DOWN, buff=0.5).scale(0.7)
        # self.play(Write(text5))
        # self.wait()
        text = Tex("This is: $x^2 + y^2 = z^2$")
        self.play(Write(text))
        self.wait()



class LineBreakTex(Scene):
    def construct(self):
        text = Tex("This is a very long line of text that we ", 
                   "will break manually using \\\\ ", 
                   "to create a new line.")
        self.play(Write(text))
        self.wait()
