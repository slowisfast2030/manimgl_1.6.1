"""
深度思考：
1.执行`from manimlib import *`的时候, 本质上会执行`from manimlib.__init__ import *`
2.python解释器是如何知道manimlib文件夹的位置呢? 是不是安装时候加manimlib所在的路径添加到了sys.path中? 很有可能

--->
在这份文件中可以执行`from manimlib import *`其实是一件很奇怪的事
更进一步, 在manimgl_1.6.1文件夹下的任何位置（包括多层嵌套）都可以执行`from manimlib import *`
这里就会涉及两个问题:
python编译器是如何知道manimlib文件夹的位置的? (应该是在安装的时候sys.path加入了manimlib所在的路径)
vscode编辑器是如何知道manimlib文件夹的位置的? (修改.vscode/settings.json文件? 但并没有显示修改)
"""
from manimlib import *
from manimlib.mobject.svg.tex_mobject import * # 这一行冗余了

"""
默认的搜索路径: 当前文件所在的路径
"""
from custom.backdrops import *
from custom.banner import *
from custom.characters.pi_creature import *
from custom.characters.pi_creature_animations import *
"""
File "pi.py", line 4, in <module>
    from manim_imports_ext import *
File "/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master/manim_imports_ext.py", line 12, in <module>
from custom.characters.pi_creature_scene import *
File "/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master/custom/characters/pi_creature_scene.py", line 21, in <module>
from manimlib.scene.interactive_scene import InteractiveScene # 潜在风险
File "/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/manimlib/scene/interactive_scene.py", line 14, in <module>
from manimlib.constants import ARROW_SYMBOLS, CTRL_SYMBOL, DELETE_SYMBOL, SHIFT_SYMBOL
ImportError: cannot import name 'ARROW_SYMBOLS' from 'manimlib.constants' (/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/manimlib/constants.py)

这个报错值得深入研究!
当执行`from manim_imports_ext import *`的时候
会依次执行manim_imports_ext.py文件里的每一行
当执行到`from custom.characters.pi_creature_scene import * `
会跳转到pi_creature_scene.py执行每一行
在21行会遇到`from manimlib.scene.interactive_scene import InteractiveScene`
此时就会跳转到interactive_scene.py文件
执行到14行
`from manimlib.constants import ARROW_SYMBOLS, CTRL_SYMBOL, DELETE_SYMBOL, SHIFT_SYMBOL`
导入的变量还没有定义, 进而报错
"""
#from custom.characters.pi_creature_scene import * 
from custom.deprecated import *
from custom.drawings import *
from custom.end_screen import *
from custom.filler import *
from custom.logo import *
from custom.opening_quote import *
