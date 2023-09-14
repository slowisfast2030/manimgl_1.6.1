from manimlib import *

class test(Scene):
    def construct(self):
        #to_isolate = ["A^2", "B^2", "C^2", "=", "+"]
        #to_isolate = ["A^2", "B^2", "C^2"]
        #to_isolate = ["A^2", "C^2"]
        to_isolate = ["+"]

        # Tex类传入的文本中间的空格会被处理, 多个空格会被合并为一个空格
        c = Tex("A^2 + B^2 = C^2", isolate=to_isolate)
    
        for index, smob in  enumerate(c.submobjects):
            print(f"Index {index}: Value {smob}      String: {smob.tex_string}")
            self.add(smob.shift(0.5*index*DOWN))
            #self.add(smob)
        