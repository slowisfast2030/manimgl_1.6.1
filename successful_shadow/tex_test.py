from manimlib import *

class test(Scene):
    def construct(self):
        to_isolate = ["B^2", "C^2", "=", "+", "A^2"]

        # t = Tex("A^2", "+", "B^2", "=", "C^2")
        # self.add(t)

        c = Tex("A^2 + B^2 = C^2", isolate=to_isolate)
        # c.shift(DOWN)
        # self.add(c)
        
        #print(t.submobjects)
        for index, smob in  enumerate(c.submobjects):
            print(index, smob)
            self.add(smob.shift(0.5*index*DOWN))
        