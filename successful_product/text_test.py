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

        self.add(text, tex, textext)