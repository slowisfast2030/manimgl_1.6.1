import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

"""
需要注意两点：

1.当用vscode打开路径在/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1的项目的时候
点击下面的`manim_imports_ext_new`是可以正常跳转的
是因为在
/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/.vscode/settings.json文件中进行了配置
{
    "python.analysis.extraPaths": [
        "./3b1b-videos-master"
    ]
}

2.当在/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master/_2017/eoc路径下执行
manimgl chapter1.py
为了不报错, 需要执行
import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

两者缺一不可！！！
"""
from manim_imports_ext_new import *
#print("all is well")
#exit()

"""
下面这一行应该注释掉
Car和MoveCar在custom/drawings.py中定义
已经在manim_imports_ext_new.py中导入
"""
#from _2017.eoc.chapter2 import Car, MoveCar


class Eoc1Thumbnail(GraphScene):
    CONFIG = {

    }

    def construct(self):
        title = TexText(
            "The Essence of\\\\Calculus",
            tex_to_color_map={
                "\\emph{you}": YELLOW,
            },
        )
        subtitle = TexText("Chapter 1")
        subtitle.match_width(title)
        subtitle.scale(0.75)
        subtitle.next_to(title, DOWN)
        # title.add(subtitle)
        title.set_width(FRAME_WIDTH - 2)
        title.to_edge(UP)
        title.set_stroke(BLACK, 8, background=True)
        # answer = OldTexText("...yes")
        # answer.to_edge(DOWN)

        axes = Axes(
            x_range=(-1, 5),
            y_range=(-1, 5),
            y_axis_config={
                "include_tip": False,
            },
            x_axis_config={
                "unit_size": 2,
            },
        )
        axes.set_width(FRAME_WIDTH - 1)
        axes.center().to_edge(DOWN)
        axes.shift(DOWN)
        self.x_axis = axes.x_axis
        self.y_axis = axes.y_axis
        self.axes = axes

        graph = self.get_graph(self.func)
        rects = self.get_riemann_rectangles(
            graph,
            x_min=0, x_max=4,
            dx=0.2,
        )
        rects.set_submobject_colors_by_gradient(BLUE, GREEN)
        rects.set_opacity(1)
        rects.set_stroke(BLACK, 1)

        self.add(axes)
        self.add(graph)
        self.add(rects)
        # self.add(title)
        # self.add(answer)

        # 为了视频能够渲染出来, 需要加上下面这一行
        self.wait(1)

    def func(slef, x):
        return 0.35 * ((x - 2)**3 - 2 * (x - 2) + 6)