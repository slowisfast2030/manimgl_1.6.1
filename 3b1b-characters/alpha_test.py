import sys
sys.path.append("/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-characters")

from manimlib import *
#from alphabet_creature import AlphabetCreature
from alphabet_creature_upgrade import AlphabetCreature

"""
因为将AlphabetCreature的math_mode属性改为False
要注意区分A和$A$
"""
class test_body(Scene):
    def construct(self):
        a = AlphabetCreature(r"$\Omega$", flip_at_start=False, color=RED)
        body = a[0]
        self.add(body)
        self.wait()

"""
这个测试用例已经将blink和look方法的返回值修改为动画了
"""
class test_omega(Scene):
    def construct(self):
        a = AlphabetCreature(r"t", 
                             flip_at_start=False, 
                             color=RED,
                             eye_scale=0.3,
                             eye_buffer=0.0,
                             eye_prop=[0.5, 0.25])
        self.add(a)
        print(a.submobjects)
        self.play(a.look(LEFT), rate_func=there_and_back)
        self.wait(1)
        self.play(a.blink(), rate_func=there_and_back)
        self.wait(1)
        self.play(a.says("hello!"))
        #self.wait(1)
        self.play(a.debubble()) 
        self.wait(1)

class test(Scene):
    def construct(self):
        a = AlphabetCreature("$\Omega$", flip_at_start=False, color=RED)
        aa = a.copy()
        self.add(a)
        self.wait()
        print(a.submobjects)
        a.look(LEFT)
        a.blink()
        self.wait(0.2)
        self.add(aa)
        self.wait(1)

class test_letter(Scene):
    def construct(self):
        a = AlphabetCreature("\pi", flip_at_start=False, color=TEAL)
        self.add(a)
        self.play(a.change("\pi"))


class test1(Scene):
    def construct(self):
        a = SingleStringTex("AB")
        self.add(a)
        print(a.submobjects)


class MyCircle(Circle):
    CONFIG = {
        "color": YELLOW_A
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

class test2(Scene):
    def construct(self):
        c = MyCircle()
        self.add(c)
