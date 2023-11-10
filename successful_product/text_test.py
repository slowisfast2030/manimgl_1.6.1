from manimlib import *

class test(Scene):
    def construct(self):
        text = Text("E = MC^2")
        self.add(text)
        # textext = TexText("""
        #     Or thinking of the plane as $\\mathds{C}$,\\\\
        #     this is the map $z \\rightarrow z^2$
        # """).shift(DOWN)
        textext = Tex("E = MC^2").shift(DOWN)
        self.add(textext)