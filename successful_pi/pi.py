import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

class test(Scene):
    def construct(self):
        pi = PiCreature(color=BLUE_E)
        for i in range(len(pi)):
            self.add(pi[i])
            pi[i].move_to(LEFT*3 + i * RIGHT)
            self.add(DecimalNumber(i).next_to(pi[i], UP))
        self.wait()

        pi2 = PiCreature(color=BLUE)
        self.add(pi2)
        pi2.move_to(DOWN*2)
        self.wait()

        pi2.look_at(LEFT)
        self.wait()

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