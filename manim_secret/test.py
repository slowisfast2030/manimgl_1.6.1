from manimlib import *

class test_demo(Scene):
    def construct(self):
        c = Circle()
        s = Square()
        
        self.add(c,s)
        print(self.mobjects)
        
        self.play(Transform(c, s), run_time=1)
        self.wait(1)
        
                  