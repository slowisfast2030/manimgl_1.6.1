"""
如果不添加这个路径
from alphabet_creature_upgrade import AlphabetCreature
会报错
"""
import sys
sys.path.append("/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-linus-creatures")

from manimlib import *
from alphabet_creature_upgrade import AlphabetCreature

"""
因为将AlphabetCreature的math_mode属性改为False
要注意区分A和$A$
"""
class test_body(Scene):
    def construct(self):
        a = AlphabetCreature(r"$\pi$", flip_at_start=False, color=RED)
        self.add(a)
        self.wait()

"""
这个测试用例已经将blink和look方法的返回值修改为动画了
更加丝滑
"""
class test_omega(Scene):
    def construct(self):
        a = AlphabetCreature(r"A", 
                             flip_at_start=False, 
                             start_corner=ORIGIN,
                             color=RED,
                             eye_scale=0.3,
                             eye_buffer=0.09,
                             eye_prop=[0.5, 0.1])
        a.scale(1)
        self.add(a)
        self.play(a.look(LEFT))
        self.wait(1)
        self.play(a.blink())
        self.wait(1)
        self.play(a.says("hello world!"))
        self.play(a.debubble()) 
        self.wait(1)