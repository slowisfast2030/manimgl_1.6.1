from manimlib import *

class test(Scene):
    def construct(self):
        # 创建一个圆环
        annulus = Annulus(inner_radius=1, outer_radius=2, color=BLUE)

        # 将圆环添加到场景中
        self.add(annulus)

        # 保持展示一段时间
        self.wait(2)
