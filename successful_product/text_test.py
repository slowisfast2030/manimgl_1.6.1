from manimlib import *

class test(Scene):
    def construct(self):
        text = Text("E = MC^2")
    
        tex = Tex("E = MC^2").shift(DOWN)

        textext = TexText("""
            Or thinking of the plane as $\\mathds{C}$,\\\\
            this is the map $z \\rightarrow z^2$
        """).shift(DOWN*2)

        self.add(text, tex, textext)