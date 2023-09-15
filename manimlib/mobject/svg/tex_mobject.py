from __future__ import annotations

from typing import Iterable, Sequence, Union
from functools import reduce
import operator as op
import colour
import re

from manimlib.constants import *
from manimlib.mobject.geometry import Line
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.config_ops import digest_config
from manimlib.utils.tex_file_writing import tex_to_svg_file
from manimlib.utils.tex_file_writing import get_tex_config
from manimlib.utils.tex_file_writing import display_during_execution

ManimColor = Union[str, colour.Color, Sequence[float]]


SCALE_FACTOR_PER_FONT_POINT = 0.001

"""
VMobjectFromSVGPath  ---> SingleStringTex ---> Tex
前面的对象作为后面对象的submobjects

一个Tex类的submobjects结构:
Index 0: Value SingleStringTex      String: A^2
0 VMobjectFromSVGPath
1 VMobjectFromSVGPath
Index 1: Value SingleStringTex      String: +
0 VMobjectFromSVGPath
Index 2: Value SingleStringTex      String: B^2
0 VMobjectFromSVGPath
1 VMobjectFromSVGPath
Index 3: Value SingleStringTex      String: =
0 VMobjectFromSVGPath
Index 4: Value SingleStringTex      String: C^2
0 VMobjectFromSVGPath
1 VMobjectFromSVGPath
"""

"""
思考一:
c = SingleStringTex("XYZ")
c.family有4个元素
后面3个分别是x,y,z
第一个究竟是什么？不显示

思考二:
当传入的字符串中有空格时, 会被自动删除
SingleStringTex("XYZ")和SingleStringTex("XY Z")
的显示效果一致

思考三:
" A B C " ---> 去掉首尾空格 ---> latex ---> svg ---> vmob

思考四:
每一个smob都会有自己的空间坐标
单独显示一个smob的时候, 也会遵循自己的空间坐标
疑问: smob的空间坐标是在哪里被确定的?应该是在latex中渲染的时候就被确定了
"""
class SingleStringTex(SVGMobject):
    """
    单个字符串渲染出的 SVGMobject
    """
    CONFIG = {
        "height": None,
        "fill_opacity": 1.0,
        "stroke_width": 0,
        "svg_default": {
            "color": WHITE,
        },
        "path_string_config": {
            "should_subdivide_sharp_curves": True,
            "should_remove_null_curves": True,
        },
        "font_size": 48,
        "alignment": "\\centering",
        "math_mode": True,
        "organize_left_to_right": False,
    }

    def __init__(self, tex_string: str, **kwargs):
        """只传入一个字符串``tex_string``"""
        assert isinstance(tex_string, str)
        self.tex_string = tex_string
        super().__init__(**kwargs)

        if self.height is None:
            self.scale(SCALE_FACTOR_PER_FONT_POINT * self.font_size)
        if self.organize_left_to_right:
            self.organize_submobjects_left_to_right()

    @property
    def hash_seed(self) -> tuple:
        return (
            self.__class__.__name__,
            self.svg_default,
            self.path_string_config,
            self.tex_string,
            self.alignment,
            self.math_mode
        )

    def get_file_path(self) -> str:
        """
        将self.tex_string的内容插入tex模版
        经过latex处理后生成svg文件
        这里返回的就是svg文件的path

        父类中有一个generate_mobject()方法
        会调用当前方法, 获得svg文件的路径
        进而解析svg文件得到vmobs, 并将其作为submobs
        """
        # 获取待渲染的完整tex文件内容（完整模版）
        full_tex = self.get_tex_file_body(self.tex_string)
        
        with display_during_execution(f"Writing \"{self.tex_string}\""):
            file_path = tex_to_svg_file(full_tex)
            #print(file_path)
        return file_path

    def get_tex_file_body(self, tex_string: str) -> str:
        new_tex = self.get_modified_expression(tex_string)
        if self.math_mode:
            new_tex = "\\begin{align*}\n" + new_tex + "\n\\end{align*}"

        new_tex = self.alignment + "\n" + new_tex
        #print(new_tex)
        """
        \centering
        \begin{align*}
        A  BC
        \end{align*}

        显示的时候A和B之间的空格消失了, 这是latex的align环境的行为
        """

        tex_config = get_tex_config()
        # 返回待渲染的完整tex文件内容
        return tex_config["tex_body"].replace(
            tex_config["text_to_replace"],
            new_tex
        )

    def get_modified_expression(self, tex_string: str) -> str:
        return self.modify_special_strings(tex_string.strip())

    def modify_special_strings(self, tex: str) -> str:
        """
        对传入的特殊str进行处理

        部分处理: 去掉首尾空格, 去掉中间空格
        """
        tex = tex.strip()
        should_add_filler = reduce(op.or_, [
            # Fraction line needs something to be over
            tex == "\\over",
            tex == "\\overline",
            # Makesure sqrt has overbar
            tex == "\\sqrt",
            tex == "\\sqrt{",
            # Need to add blank subscript or superscript
            tex.endswith("_"),
            tex.endswith("^"),
            tex.endswith("dot"),
        ])
        if should_add_filler:
            filler = "{\\quad}"
            tex += filler

        should_add_double_filler = reduce(op.or_, [
            tex == "\\overset",
            # TODO: these can't be used since they change
            # the latex draw order.
            # tex == "\\frac", # you can use \\over as a alternative 
            # tex == "\\dfrac",
            # tex == "\\binom",
        ])
        if should_add_double_filler:
            filler = "{\\quad}{\\quad}"
            tex += filler

        if tex == "\\substack":
            tex = "\\quad"

        if tex == "":
            tex = "\\quad"

        # To keep files from starting with a line break
        if tex.startswith("\\\\"):
            tex = tex.replace("\\\\", "\\quad\\\\")

        tex = self.balance_braces(tex)

        # Handle imbalanced \left and \right
        num_lefts, num_rights = [
            len([
                s for s in tex.split(substr)[1:]
                if s and s[0] in "(){}[]|.\\"
            ])
            for substr in ("\\left", "\\right")
        ]
        if num_lefts != num_rights:
            tex = tex.replace("\\left", "\\big")
            tex = tex.replace("\\right", "\\big")

        for context in ["array"]:
            begin_in = ("\\begin{%s}" % context) in tex
            end_in = ("\\end{%s}" % context) in tex
            if begin_in ^ end_in:
                # Just turn this into a blank string,
                # which means caller should leave a
                # stray \\begin{...} with other symbols
                tex = ""
        return tex

    def balance_braces(self, tex: str) -> str:
        """
        Makes Tex resiliant to unmatched braces
        """
        """
        匹配大括号
        """
        num_unclosed_brackets = 0
        for i in range(len(tex)):
            if i > 0 and tex[i - 1] == "\\":
                # So as to not count '\{' type expressions
                continue
            char = tex[i]
            if char == "{":
                num_unclosed_brackets += 1
            elif char == "}":
                if num_unclosed_brackets == 0:
                    tex = "{" + tex
                else:
                    num_unclosed_brackets -= 1
        tex += num_unclosed_brackets * "}"
        return tex

    def get_tex(self) -> str:
        return self.tex_string

    def organize_submobjects_left_to_right(self):
        self.sort(lambda p: p[0])
        return self


"""
函数作为黑箱, 可以先拿一个例子测一下, 看输入输出
在明确了输入输出的情况下, 看代码事半功倍

切忌: 一上来就啃代码, 极其低效
"""
"""
VMobjectFromSVGPath  ---> SingleStringTex ---> Tex

Tex类嵌套了svg文件中的每一个element
可以在Tex对象中取出任何一个VMobjectFromSVGPath对象

c = Tex("A^2","+B^2","=C^2", isolate=["+", "="], arg_separator="")
subsubmob = c.submobjects[0].submobjects[0]
"""
class Tex(SingleStringTex):
    """
    用于生成 LaTeX 公式(align 环境)
    """
    CONFIG = {
        "arg_separator": "",
        "isolate": [],
        "tex_to_color_map": {},
    }

    def __init__(self, *tex_strings: str, **kwargs):
        """可传入多个 ``tex_strings``
        
        - ``arg_separator`` 表示每两个字符串之间的字符，默认为空格
        - ``isolate`` 列表中放有想要单独拆开的字符串，可以不用手动拆开
        - ``tex_to_color_map`` 为一个字典，会根据其中的键自动拆开字符串用于上色
        """
        digest_config(self, kwargs)
        self.tex_strings = self.break_up_tex_strings(tex_strings) # 字符串重组
        full_string = self.arg_separator.join(self.tex_strings)
        # print("="*78)
        # print(self.tex_strings)
        # print(full_string)
        # print("="*78)
        """
        ['A^2', '+', 'B^2', '=', 'C^2']
        A^2+B^2=C^2
        """
        # 这里把full_string传递给了父类的初始化函数
        super().__init__(full_string, **kwargs)

        # 执行了break_up_by_substrings()方法后, self.submobjects发生了翻天覆地的变化
        self.break_up_by_substrings() # submob结构重组

        self.set_color_by_tex_to_color_map(self.tex_to_color_map)

        if self.organize_left_to_right:
            self.organize_submobjects_left_to_right()

    def break_up_tex_strings(self, tex_strings: Iterable[str]) -> Iterable[str]:
        # Separate out any strings specified in the isolate
        # or tex_to_color_map lists.
        """
        根据isolate 和 tex_to_color_map 
        对输入tex_strings进行字符串重组

        比如:
        c = Tex("A^2","+B^2","=C^2", isolate=["+", "="], arg_separator="")
        输入
        tex_strings = ["A^2","+B^2","=C^2"]
        输出
        ['A^2', '+', 'B^2', '=', 'C^2']
        """
        substrings_to_isolate = [*self.isolate, *self.tex_to_color_map.keys()]
        if len(substrings_to_isolate) == 0:
            return tex_strings
        patterns = (
            "({})".format(re.escape(ss))
            for ss in substrings_to_isolate
        )
        pattern = "|".join(patterns)
        pieces = []
        for s in tex_strings:
            if pattern:
                pieces.extend(re.split(pattern, s))
            else:
                pieces.append(s)
        return list(filter(lambda s: s, pieces))

    def break_up_by_substrings(self):
        """
        Reorganize existing submojects one layer
        deeper based on the structure of tex_strings (as a list
        of tex_strings)
        """
        """
        将VMobjectFromSVGPath对象进行submob结构重组
        注意: 是根据break_up_tex_strings方法的字符串重组结果进行submob结构重复


        c = Tex("A^2","+B^2","=C^2", isolate=["+", "="], arg_separator="")

        before:
        [<manimlib.mobject.svg.svg_mobject.VMobjectFromSVGPath object at 0x7f8e8276cd30>, #A
        <manimlib.mobject.svg.svg_mobject.VMobjectFromSVGPath object at 0x7f8e82a78ca0>,  #2
        <manimlib.mobject.svg.svg_mobject.VMobjectFromSVGPath object at 0x7f8e82a90520>,  #+
        <manimlib.mobject.svg.svg_mobject.VMobjectFromSVGPath object at 0x7f8e82a90b20>,  #B
        <manimlib.mobject.svg.svg_mobject.VMobjectFromSVGPath object at 0x7f8e82a90730>,  #2
        <manimlib.mobject.svg.svg_mobject.VMobjectFromSVGPath object at 0x7f8e82aa73d0>,  #=
        <manimlib.mobject.svg.svg_mobject.VMobjectFromSVGPath object at 0x7f8e82aa7a90>,  #C
        <manimlib.mobject.svg.svg_mobject.VMobjectFromSVGPath object at 0x7f8e82aa7610>]  #2

        after:
        [<manimlib.mobject.svg.tex_mobject.SingleStringTex object at 0x7f8e82a10fa0>, #A^2
        <manimlib.mobject.svg.tex_mobject.SingleStringTex object at 0x7f8e8276a250>,  #+
        <manimlib.mobject.svg.tex_mobject.SingleStringTex object at 0x7f8e82aad340>,  #B^2
        <manimlib.mobject.svg.tex_mobject.SingleStringTex object at 0x7f8e82ab7160>,  #=
        <manimlib.mobject.svg.tex_mobject.SingleStringTex object at 0x7f8e82752eb0>]  #C^2
        
        也就是把每一个VMobjectFromSVGPath对象
        添加进了对应的SingleStringTex的submobjects
        """
        if len(self.tex_strings) == 1:
            submob = self.copy()
            self.set_submobjects([submob])
            return self
        new_submobjects = []
        curr_index = 0
        config = dict(self.CONFIG)
        config["alignment"] = ""
        # ['A^2', '+', 'B^2', '=', 'C^2']
        for tex_string in self.tex_strings:
            tex_string = tex_string.strip()
            if len(tex_string) == 0:
                continue
            # 此时已经拿到了每一个VMobjectFromSVGPath, 再执行一遍会不会冗余
            # 从后面的代码来看, 并没有用这里再执行生成的VMobjectFromSVGPath
            # 因为空间位置变了
            sub_tex_mob = SingleStringTex(tex_string, **config)
            # 难道只是为了获取这个量?
            num_submobs = len(sub_tex_mob)
            if num_submobs == 0:
                continue
            new_index = curr_index + num_submobs
            # 将VMobjectFromSVGPath对象加入SingleStringTex对象的submobjects
            sub_tex_mob.set_submobjects(self[curr_index:new_index])
            new_submobjects.append(sub_tex_mob)
            curr_index = new_index
        # 将SingleStringTex对象加入Tex对象的submobjects
        self.set_submobjects(new_submobjects)
        return self

    def get_parts_by_tex(
        self,
        tex: str,
        substring: bool = True,
        case_sensitive: bool = True
    ) -> VGroup:
        """
        to_isolate = ["+", "="]
        tex_to_color_map = {}
        
        c = Tex("A^2","+B^2","=C^2", isolate=to_isolate, arg_separator="", tex_to_color_map=tex_to_color_map)
        c.set_color_by_tex("C", PINK)

        需要注意, 此时c的submobjects有5个元素:
        SingleStringTex A^2
        SingleStringTex +
        SingleStringTex B^2
        SingleStringTex =
        SingleStringTex C^2
        
        当给C染色的时候, 会给整个C^2整体染色
        当给2染色的时候, 会给A^2, B^2和C^2整体染色

        -------------------------------------
        需要注意的是, 如果

        to_isolate = ["+", "="]
        tex_to_color_map = {
                "A": BLUE,
                "B": TEAL,
                "C": GREEN,
            }
        c = Tex("A^2","+B^2","=C^2", isolate=to_isolate, arg_separator="", tex_to_color_map=tex_to_color_map)
        此时c的submobjects有8个元素:
        SingleStringTex A
        SingleStringTex ^2
        SingleStringTex +
        SingleStringTex B
        SingleStringTex ^2
        SingleStringTex =
        SingleStringTex C
        SingleStringTex ^2

        因为isolate和tex_to_color_map都会用来重组字符串
        """
        def test(tex1, tex2):
            if not case_sensitive:
                tex1 = tex1.lower()
                tex2 = tex2.lower()
            if substring:
                return tex1 in tex2
            else:
                return tex1 == tex2

        """
        这里返回的是原submob的索引
        指向的是同一个对象
        """
        return VGroup(*filter(
            lambda m: isinstance(m, SingleStringTex) and test(tex, m.get_tex()),
            self.submobjects
        ))

    def get_part_by_tex(self, tex: str, **kwargs) -> SingleStringTex | None:
        all_parts = self.get_parts_by_tex(tex, **kwargs)
        return all_parts[0] if all_parts else None

    def set_color_by_tex(self, tex: str, color: ManimColor, **kwargs):
        """
        给 ``tex`` 上颜色为 ``color``，注意此时 ``tex`` 要独立存在，否则会给包含 ``tex`` 的也上色
        """
        self.get_parts_by_tex(tex, **kwargs).set_color(color)
        return self

    def set_color_by_tex_to_color_map(
        self,
        tex_to_color_map: dict[str, ManimColor],
        **kwargs
    ):
        """
        根据 ``texs_to_color_map`` 上色，同样，会给包含键的全部上色，不会自动拆分
        """
        for tex, color in list(tex_to_color_map.items()):
            self.set_color_by_tex(tex, color, **kwargs)
        return self

    def index_of_part(self, part: SingleStringTex, start: int = 0) -> int:
        return self.submobjects.index(part, start)

    def index_of_part_by_tex(self, tex: str, start: int = 0, **kwargs) -> int:
        part = self.get_part_by_tex(tex, **kwargs)
        return self.index_of_part(part, start)

    def slice_by_tex(
        self,
        start_tex: str | None = None,
        stop_tex: str | None = None,
        **kwargs
    ) -> VGroup:
        if start_tex is None:
            start_index = 0
        else:
            start_index = self.index_of_part_by_tex(start_tex, **kwargs)

        if stop_tex is None:
            return self[start_index:]
        else:
            stop_index = self.index_of_part_by_tex(stop_tex, start=start_index, **kwargs)
            return self[start_index:stop_index]

    def sort_alphabetically(self) -> None:
        """
        根据字典序给子物体排序
        """
        self.submobjects.sort(key=lambda m: m.get_tex())

    def set_bstroke(self, color: ManimColor = BLACK, width: float = 4):
        self.set_stroke(color, width, background=True)
        return self


class TexText(Tex):
    """ 用于生成 LaTeX 文字，默认每行之间居中
    
    传入的两个字符串之间无分隔 (即 ``arg_separator=""``)
    """
    CONFIG = {
        "math_mode": False,
        "arg_separator": "",
    }


class BulletedList(TexText):
    """
    项目列表
    """
    CONFIG = {
        "buff": MED_LARGE_BUFF,
        "dot_scale_factor": 2,
        "alignment": "",
    }

    def __init__(self, *items: str, **kwargs):
        """ 
        支持多个字符串，每个一行；也支持一个字符串，使用 LaTeX 的换行 (\\\\)
        """
        line_separated_items = [s + "\\\\" for s in items]
        TexText.__init__(self, *line_separated_items, **kwargs)
        for part in self:
            dot = Tex("\\cdot").scale(self.dot_scale_factor)
            dot.next_to(part[0], LEFT, SMALL_BUFF)
            part.add_to_back(dot)
        self.arrange(
            DOWN,
            aligned_edge=LEFT,
            buff=self.buff
        )

    def fade_all_but(self, index_or_string: int | str, opacity: float = 0.5) -> None:
        """把除了 ``index_or_string`` 之外的不透明度均设为 ``opacity``
        
        ``index_or_string`` 可以传入子物体的下标，也可以传入一个字符串
        """
        arg = index_or_string
        if isinstance(arg, str):
            part = self.get_part_by_tex(arg)
        elif isinstance(arg, int):
            part = self.submobjects[arg]
        else:
            raise Exception("Expected int or string, got {0}".format(arg))
        for other_part in self.submobjects:
            if other_part is part:
                other_part.set_fill(opacity=1)
            else:
                other_part.set_fill(opacity=opacity)


class TexFromPresetString(Tex):
    CONFIG = {
        # To be filled by subclasses
        "tex": None,
        "color": None,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        Tex.__init__(self, self.tex, **kwargs)
        self.set_color(self.color)


class Title(TexText):
    """
    标题
    """
    CONFIG = {
        "scale_factor": 1,
        "include_underline": True,
        "underline_width": FRAME_WIDTH - 2,
        # This will override underline_width
        "match_underline_width_to_text": False,
        "underline_buff": MED_SMALL_BUFF,
    }

    def __init__(self, *text_parts: str, **kwargs):
        """``include_underline=True`` 会添加下划线（默认添加）
        ``underline_width`` 下划线的长度（默认屏幕宽 - 2 个单位）
        ``match_underline_width_to_text=True`` 时将下划线的长度和文字匹配（默认为 False）
        """
        TexText.__init__(self, *text_parts, **kwargs)
        self.scale(self.scale_factor)
        self.to_edge(UP)
        if self.include_underline:
            underline = Line(LEFT, RIGHT)
            underline.next_to(self, DOWN, buff=self.underline_buff)
            if self.match_underline_width_to_text:
                underline.match_width(self)
            else:
                underline.set_width(self.underline_width)
            self.add(underline)
            self.underline = underline
