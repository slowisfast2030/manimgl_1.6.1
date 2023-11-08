from manimlib import *

class test(Scene):
    def construct(self):
        circle = Circle()
        dot = Dot()
        self.add(circle, dot)
        
        def circle_updater(mob, dt):
            #circle.shift(RIGHT * dt)
            #mob.move_to(circle.get_edge_center(RIGHT))
            mob.shift(dt * RIGHT)
        
        dot.add_updater(circle_updater)
        self.add(dot)  # Don't forget to add the dot to the scene if it hasn't been added already.

        self.wait(5)  # The updater will work during this time.

        dot.remove_updater(circle_updater)  # Optionally, remove the updater if it's no longer needed.

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
        dot = Dot()
        text = Text("hello world")
        self.add(circle, dot, text)
        
        def dot_updater(mob):
            mob.move_to(circle.get_edge_center(RIGHT))

        def text_updater(mob):
            mob.move_to(dot.get_center() + UP * 2)
        
        dot.add_updater(dot_updater)
        text.add_updater(text_updater)

        self.play(Transform(circle, circle.copy().shift(RIGHT*3)), run_time=3)  # The updater will work during this time.

        dot.remove_updater(dot_updater)  # Optionally, remove the updater if it's no longer needed.