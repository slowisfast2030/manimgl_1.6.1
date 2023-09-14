from manimlib import *

class test(Scene):
    def construct(self):
        #to_isolate = ["A^2", "B^2", "C^2", "=", "+"]
        #to_isolate = ["A^2", "B^2", "C^2"]
        to_isolate = ["A^2", "C^2"]

        c = Tex("A^2 + B^2 = C^2", isolate=to_isolate)
    
        for index, smob in  enumerate(c.submobjects):
            print(index, smob, smob.tex_string)
            self.add(smob.shift(0.5*index*DOWN))
        