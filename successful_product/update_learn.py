from manimlib import *

"""
updater如果不使用dt参数，是很明显的被动触发方式
animation --> updater
执行动画的过程中，animation会作用于一个mob
mob的某些属性会在每一帧发生变化
而updater可以跟踪这些属性变化

updater如果使用dt参数，是很明显的主动触发方式
可以精确控制每一帧的行为
"""
class test(Scene):
    def construct(self):
        circle = Circle()
        dot = Dot()
        self.add(circle, dot)
        
        def circle_updater(mob, dt):
            mob.shift(dt * RIGHT)
        
        dot.add_updater(circle_updater)
        self.add(dot)  # Don't forget to add the dot to the scene if it hasn't been added already.

        self.wait(5)  # The updater will work during this time.

        dot.remove_updater(circle_updater)  # Optionally, remove the updater if it's no longer needed.

"""
链式触发
animation(circle) --> updater(dot) --> updater(text)
"""
class test1(Scene):
    def construct(self):
        circle = Circle()
        dot = Dot()
        text = Text("hello world")
        self.add(circle, dot, text)
        
        def dot_updater(mob):
            mob.move_to(circle.get_edge_center(RIGHT))

        def text_updater(mob):
            mob.move_to(dot.get_center() + UP * 2)
        
        dot.add_updater(dot_updater)
        text.add_updater(text_updater)

        self.add(dot)  # Don't forget to add the dot to the scene if it hasn't been added already.

        self.play(circle.animate.move_to(RIGHT * 4), run_time=3)  # The updater will work during this time.

        dot.remove_updater(dot_updater)  # Optionally, remove the updater if it's no longer needed.

# 对于updater来说，play和wait是一样的

class test2(Scene):
    def construct(self):
        circle = Circle()
        square = Square().shift(RIGHT*3).set_color(BLUE_E)
        dot = Dot()
        text = Text("hello world")
        self.add(circle, dot, text)
        
        def dot_updater(mob):
            mob.move_to(circle.get_edge_center(RIGHT))

        def text_updater(mob):
            mob.move_to(dot.get_center() + UP * 2)
        
        dot.add_updater(dot_updater)
        text.add_updater(text_updater)

        # 非常有启发
        self.play(Transform(circle, square), run_time=3)  # The updater will work during this time.
        #self.play(TransformFromCopy(circle, square), run_time=3)

        dot.remove_updater(dot_updater)  # Optionally, remove the updater if it's no longer needed.