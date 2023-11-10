from manimlib import *

class test(Scene):
    def construct(self):
        overbrace = Tex(r"\overbrace{}").shift(UP)
        underbrace = Tex(r"\underbrace{}")
        
        self.add(underbrace, overbrace)