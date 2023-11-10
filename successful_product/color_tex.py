from manimlib import *

class test(Scene):
    def construct(self):
        # Create the integral expression
        integral_tex = Tex(r"\int_a^b f(x) \,dx = S", 
                               isolate=["\int", "a", "b", "f(x)", "dx", "S"])

        # Apply different colors to each part of the expression
        integral_tex.set_color_by_tex_to_color_map({
            "\int": RED,
            "a": WHITE,
            "b": BLUE,
            "f(x)": YELLOW,
            "dx": ORANGE,
            "S": PURPLE
        })

        # Display the expression
        self.play(Write(integral_tex))
        self.wait()
