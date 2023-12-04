import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

"""

"""
class TestScene(Scene):
    def construct(self):
        pi = PiCreature(color=BLUE_E)
        self.add(pi)  # Add the entire PiCreature to the scene

        # Loop through each part of the PiCreature to add labels and arrows
        for index, part in enumerate(pi):
            # Create a label for each part
            label = Integer(index).next_to(part, RIGHT*4)

            # Create an arrow pointing to ealeftart
            arrow = Arrow(label.get_left(), part.get_center(), buff=0.1)

            # Add the label and arrow to the scene
            self.add(label, arrow)

        self.wait()


class test(Scene):
    def construct(self):
        pi = PiCreature(color=BLUE_E)
        # Use a single loop to add all parts of the PiCreature and the corresponding DecimalNumber
        for index, part in enumerate(pi):
            part.move_to(LEFT * 3 + index * RIGHT)
            number = DecimalNumber(index).next_to(part, UP)
            self.add(part, number)  # Adding both simultaneously for efficiency
        self.wait()


        pi2 = PiCreature(color=BLUE)
        self.add(pi2)
        pi2.move_to(DOWN*2)
        self.wait()

        pi2.look_at(LEFT)
        self.wait()

        # blink的效果有问题
        pi2.blink()
        self.wait()

        pi2.shrug()
        self.wait()

"""
part1: 为编译器所需
import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

part2: 为vscode所需
{
    "python.analysis.extraPaths": [
        "./3b1b-videos-master"
    ]
}

part1需要写在当前文件的开头
part2需要写在settings.json中

如果只写part2
整个文件内的变量都可以正常跳转, 但是无法执行, 会告知:
ModuleNotFoundError: No module named 'manim_imports_ext'

如果只写part1
整个文件内的变量不能正常跳转, 但是可以执行

同时添加part1和part2
技能跳转, 又能执行
"""