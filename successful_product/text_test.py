from manimlib import *

class test(Scene):
    def construct(self):
        text = Text("E = mc^2")
    
        tex = Tex("E", " = ", "m", "c^2").shift(DOWN)
        tex.set_color_by_tex_to_color_map({
                "E": BLUE,
                "m": TEAL,
                "c": GREEN,
            })

        # textext = TexText("""
        #     Or thinking of the plane as $\\mathds{C}$,\\\\
        #     this is the map $z \\rightarrow z^2$
        # """).shift(DOWN*2.5)
        textext = TexText("This is a combination of text and a LaTeX formula: $E=mc^2$").shift(DOWN*2)

        #self.add(text, tex, textext)

        integral_tex = Tex(
            r"\int_a^b f(x) \,dx = S", isolate=["a", "b", "\int", "f(x)", "dx"]
        ).shift(DOWN)

        # Set different colors for different parts of the formula
        integral_tex.set_color_by_tex_to_color_map({
            "\int": RED,  # Color for the integral symbol
            "b": ORANGE,     # Color for the 'a' variable
            "dx": GREEN,   # Color for the 'dx' part
            "=": YELLOW,   # Color for the '=' symbol
            "a": WHITE,    # Color for the 'b' variable
            "f(x)": BLUE_E,    # Color for the 'f(x)' part
        })

        # Add the formula to the scene
        self.add(integral_tex)