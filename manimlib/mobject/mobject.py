from __future__ import annotations

import sys
import copy
import random
import itertools as it
from functools import wraps
from typing import Iterable, Callable, Union, Sequence

import colour
import moderngl
import numpy as np
import numpy.typing as npt

from manimlib.constants import *
from manimlib.utils.color import color_gradient
from manimlib.utils.color import get_colormap_list
from manimlib.utils.color import rgb_to_hex
from manimlib.utils.color import color_to_rgb
from manimlib.utils.config_ops import digest_config
from manimlib.utils.iterables import batch_by_property
from manimlib.utils.iterables import list_update
from manimlib.utils.iterables import resize_array
from manimlib.utils.iterables import resize_preserving_order
from manimlib.utils.iterables import resize_with_interpolation
from manimlib.utils.iterables import make_even
from manimlib.utils.iterables import listify
from manimlib.utils.bezier import interpolate
from manimlib.utils.bezier import integer_interpolate
from manimlib.utils.paths import straight_path
from manimlib.utils.simple_functions import get_parameters
from manimlib.utils.space_ops import angle_of_vector
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import rotation_matrix_transpose
from manimlib.shader_wrapper import ShaderWrapper
from manimlib.shader_wrapper import get_colormap_code
from manimlib.event_handler import EVENT_DISPATCHER
from manimlib.event_handler.event_listner import EventListner
from manimlib.event_handler.event_type import EventType

"""
TimeBasedUpdater is a type alias for a function that takes two parameters: 
a "Mobject" (which represents a graphical object) and 
a float(which represents time). This function does not return anything (None).
"""
TimeBasedUpdater = Callable[["Mobject", float], None]
NonTimeUpdater = Callable[["Mobject"], None]
"""
Updater is a union type alias that can be either a TimeBasedUpdater or a NonTimeUpdater.
"""
Updater = Union[TimeBasedUpdater, NonTimeUpdater]
"""
ManimColor is a union type alias that can be either a str, a colour.Color object, 
or a sequence of float values.
"""
ManimColor = Union[str, colour.Color, Sequence[float]]


class Mobject(object):
    """
    Mathematical Object
    数学对象（屏幕上所有物体的超类）
    """
    CONFIG = {
        "color": WHITE,
        "opacity": 1,
        "dim": 3,  # TODO, get rid of this
        # Lighting parameters
        # ...
        # Larger reflectiveness makes things brighter when facing the light
        "reflectiveness": 0.0,
        # Larger shadow makes faces opposite the light darker
        "shadow": 0.0,
        # Makes parts bright where light gets reflected toward the camera
        "gloss": 0.0,
        # 着色器相关代码所在的文件夹，manimlib/shaders/
        "shader_folder": "",
        # 渲染的基元，子类会进行修改
        "render_primitive": moderngl.TRIANGLE_STRIP,
        # 纹理路径
        "texture_paths": None,
        # 深度测试
        "depth_test": False,
        # If true, the mobject will not get rotated according to camera position
        "is_fixed_in_frame": False,
        # Must match in attributes of vert shader
        "shader_dtype": [
            ('point', np.float32, (3,)),
        ]
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)

        self.submobjects: list[Mobject] = []
        self.parents: list[Mobject] = [] # self.parents和self.family是什么关系？
        self.family: list[Mobject] = [self]
        # self.data是字典，有一些key对应的value被锁定了，不能修改
        self.locked_data_keys: set[str] = set() # 什么是self.locked_data_keys？
        self.needs_new_bounding_box: bool = True

        self.init_data()
        self.init_uniforms()
        self.init_updaters()
        self.init_event_listners()
        self.init_points()
        self.init_colors()
        self.init_shader_data()

        if self.depth_test:
            self.apply_depth_test()

    """
    The __str__ function is used to return a human-readable, or informal, string representation 
    of an object. This function is called by the built-in print(), str(), and format() functions. 
    If you don't define a str function for a class, then the built-in object implementation calls 
    the repr function instead.
    """
    def __str__(self):
        return self.__class__.__name__

    """
    The add function is used to implement the addition operator (+) for custom objects. 
    This function takes two objects (the operands of +) as arguments and is expected to 
    return the result of the computation.
    """
    def __add__(self, other: Mobject) -> Mobject:
        assert(isinstance(other, Mobject))
        return self.get_group_class()(self, other)

    """
    The mul function is used to implement the multiplication operator (*) for custom objects. 
    This function takes two objects (the operands of *) as arguments and is expected to return 
    the result of the computation.
    """
    def __mul__(self, other: int) -> Mobject:
        assert(isinstance(other, int))
        return self.replicate(other)

    """
    'fill_rgba': array([[0.98823529, 0.38431373, 0.33333333, 0.        ]])
    'stroke_rgba': array([[0.98823529, 0.38431373, 0.33333333, 1.        ]])
    """
    def init_data(self):
        """
        这里需要拓展认知：
        每一个mob的data不仅仅包括points, 还包括bounding_box和rgbas
        """
        """
        RGBA stands for red, green, blue, and alpha. It is a color model that describes 
        how colors are represented and mixed in computer graphics. Each color component 
        (red, green, and blue) has a value ranging from 0 to 255, where 0 means no color 
        and 255 means full color. The alpha component represents the opacity or transparency 
        of the color, with a value ranging from 0 to 255, where 0 means fully transparent 
        and 255 means fully opaque
        """
        self.data: dict[str, np.ndarray] = {
            "points": np.zeros((0, 3)),       # 数列，3个元素
            "bounding_box": np.zeros((3, 3)), # 矩阵，3行3列
            "rgbas": np.zeros((1, 4)),        # 矩阵，1行4列
        }

    def init_uniforms(self):
        """
        这里的uniforms应该怎么翻译?
        不用翻译
        """
        self.uniforms: dict[str, float] = {
            "is_fixed_in_frame": float(self.is_fixed_in_frame),
            "gloss": self.gloss,
            "shadow": self.shadow,
            "reflectiveness": self.reflectiveness,
        }

    def init_colors(self):
        """
        color和opacity属性来源于CONFIG字典

        这是不是就是argb?
        """
        self.set_color(self.color, self.opacity)

    def init_points(self):
        # Typically implemented in subclass, unless purposefully left blank
        pass

    """
    The copy() function in Python is a method that is used to create shallow copies 
    of objects, such as lists, dictionaries, or sets. A shallow copy means that the 
    new object references the same elements as the original object, but does not 
    create new copies of them. This means that if you modify an element in the original 
    object, it will also affect the copied object, and vice versa.
    """
    def set_data(self, data: dict):
        '''设置成员数据，以字典形式传入'''
        for key in data:
            self.data[key] = data[key].copy()
        return self

    def set_uniforms(self, uniforms: dict):
        '''设置 uniform 变量，以字典形式传入'''
        for key in uniforms:
            self.uniforms[key] = uniforms[key]  # Copy?
        return self

    @property
    def animate(self):
        # Borrowed from https://github.com/ManimCommunity/manim/
        return _AnimationBuilder(self)

    # Only these methods should directly affect points

    """
    当new_length小于mob的锚点数量时
    resize_points函数会将mob的锚点数量缩减到new_length

    当new_length大于mob的锚点数量时
    resize_points函数会将mob的锚点数量扩充到new_length

    后面主要有两个使用场景:
    1.清空锚点
    2.对齐锚点
    """
    def resize_points(
        self,
        new_length: int,
        resize_func: Callable[[np.ndarray, int], np.ndarray] = resize_array
    ):
        '''
        重置锚点数组大小

        有一个疑问: 
        这里重置self.data["points"]的大小, 还是拿原来的data["points"]进行填充
        要么重复, 要么截断, 并没有引入新的数据
        这样做有什么用么
        '''
        if new_length != len(self.data["points"]):
            self.data["points"] = resize_func(self.data["points"], new_length)
        self.refresh_bounding_box()
        return self

    def set_points(self, points: npt.ArrayLike):
        '''
        设置锚点

        严格来讲, 应该是anchor和handle
        不过, 这应该是对vmobject子类来说的
        surface子类就没有anchor和handle的概念
        '''
        if len(points) == len(self.data["points"]):
            self.data["points"][:] = points
        elif isinstance(points, np.ndarray):
            self.data["points"] = points.copy()
        else:
            self.data["points"] = np.array(points)
        self.refresh_bounding_box()
        return self

    """
    The np.vstack function is used to stack or concatenate the sequence of input arrays 
    vertically (row-wise) and make them a single array.

    # Import numpy module
    import numpy as np

    # Create two input arrays
    a = np.array([1, 2, 3])
    b = np.array([[4, 5, 6], [7,8,9]])
    c = np.array([[1, 2, 3], [4, 5, 6], [7,8,9]])

    # Stack them vertically using np.vstack
    d = np.vstack((a, b, c))

    # Print the output array
    print(d)

    [[1 2 3]
    [4 5 6]
    [7 8 9]
    [1 2 3]
    [4 5 6]
    [7 8 9]]

    """
    def append_points(self, new_points: npt.ArrayLike):
        '''
        添加锚点
        '''
        self.data["points"] = np.vstack([self.data["points"], new_points])
        self.refresh_bounding_box()
        return self

    def reverse_points(self):
        '''
        反转锚点

        锚点的顺序影响曲线的绘制顺序

        pointwise_become_partial()
        point_from_proportion()
        等函数都和点集的顺序有关系
        '''
        for mob in self.get_family():
            for key in mob.data:
                mob.data[key] = mob.data[key][::-1]
        # 这个函数是在Vmobject类中定义的
        self.refresh_unit_normal()
        return self


    """
    plane = NumberPlane()
    c = Circle().set_color(RED)
    cc = c.copy().set_color(TEAL)
    cc.apply_points_function(
        lambda points: 2*points,
        about_point=c.point_from_proportion(0.125+0.25)
    )

    self.add(c, cc, plane)
    self.wait(1)
    """
    def apply_points_function(
        self,
        func: Callable[[np.ndarray], np.ndarray],
        about_point: np.ndarray = None,
        about_edge: np.ndarray = ORIGIN,
        works_on_bounding_box: bool = False
    ):
        """
        以 ``about_point`` 为不变基准点，或以 ``about_edge`` 为不变基准边，对所有点执行 ``func``
        真是神仙注释:)

        about_edge是为了计算about_point而存在的, 核心还是about_point

        灵魂发问: 为何about_point是核心?
        如果这里的func是矩阵
        矩阵的几何意义是旋转+伸缩(平移需要扩充维度)
        如果规定伸缩比例为1
        那么就是正交矩阵
        那么，正交矩阵的几何意义就是旋转
        这里的about_point就是旋转轴通过的点
        """
        """
        从更高的角度来理解:
        func(arr - about_point) + about_point 和 func(arr)
        本质是一样的
        func(arr) = func(arr - [0, 0, 0]) + [0, 0, 0]
        将func理解为对向量的函数

        举例:
        func = lambda point: 2 * point
        将mob的每个点point放大为2倍
        也可理解为将mob上每个点和原点之间的vector放大为2倍
        """
        # about_point是主要的
        # 如果about_point为None，就用about_edge
        if about_point is None and about_edge is not None:
            about_point = self.get_bounding_box_point(about_edge)

        # family是有自身的，submobjects没有
        for mob in self.get_family():
            """
            arr中的元素是点集的引用
            对引用的操作会改变点集本身
            进而影响到mob
            """
            arrs = []
            """
            好像一直以来误解了一个东西
            arrs中最多有2个元素
            每一个元素都是点集
            """
            if mob.has_points():
                arrs.append(mob.get_points())
            if works_on_bounding_box:
                arrs.append(mob.get_bounding_box())

            for arr in arrs:
                if about_point is None:
                    # func是作用于一个点集，而不是一个点
                    arr[:] = func(arr)
                else:
                    """
                    当about_point为None且about_edge = ORIGIN的时候
                    about_point就是mob的center

                    当func为旋转变换的时候, 旋转中心就是mob的center
                    当func为线性伸缩变换的时候(即所有坐标等比例放大的时候), 伸缩中心就是mob的center
                    """
                    arr[:] = func(arr - about_point) + about_point

        if not works_on_bounding_box:
            self.refresh_bounding_box(recurse_down=True)
        else:
            for parent in self.parents:
                parent.refresh_bounding_box()
        return self

    # Others related to points

    def match_points(self, mobject: Mobject):
        '''
        将自身锚点与 ``mobject`` 的锚点匹配
        '''
        self.set_points(mobject.get_points())
        return self

    def get_points(self) -> np.ndarray:
        '''
        获取物件锚点
        '''
        return self.data["points"]

    def clear_points(self) -> None:
        '''
        清空物件锚点
        '''
        self.resize_points(0)

    def get_num_points(self) -> int:
        '''
        获取锚点数量
        '''
        return len(self.data["points"])

    def get_all_points(self) -> np.ndarray:
        '''
        获取物件所有锚点

        这个函数就可以看出submobjects属性和self.get_family()的区别了
        submobjects属性只包含直接子物件, 而get_family()还包含自身
        '''
        if self.submobjects:
            return np.vstack([sm.get_points() for sm in self.get_family()])
        else:
            return self.get_points()

    def has_points(self) -> bool:
        '''
        判断是否有锚点
        '''
        return self.get_num_points() > 0

    def get_bounding_box(self) -> np.ndarray:
        '''
        获取物件的矩形包围框（碰撞箱）
        
        包含三个元素，分别为左下，中心，右上
        '''
        if self.needs_new_bounding_box:
            self.data["bounding_box"] = self.compute_bounding_box()
            self.needs_new_bounding_box = False
        return self.data["bounding_box"]

    def compute_bounding_box(self) -> np.ndarray:
        '''
        计算包围框
        '''
        all_points = np.vstack([
            self.get_points(),
            *(
                mob.get_bounding_box()
                for mob in self.get_family()[1:]
                if mob.has_points()
            )
        ])
        if len(all_points) == 0:
            return np.zeros((3, self.dim))
        else:
            # Lower left and upper right corners
            """
            为了更加形象的理解, 我们可以假设mob为circle
            将circle的所有锚点放在一个平面上
            那么这个平面的左下角和右上角就是circle的包围框
            """
            mins = all_points.min(0)
            maxs = all_points.max(0)
            mids = (mins + maxs) / 2
            return np.array([mins, mids, maxs])

    def refresh_bounding_box(
        self,
        recurse_down: bool = False,
        recurse_up: bool = True
    ):
        '''
        更新包围框
        '''
        for mob in self.get_family(recurse_down):
            mob.needs_new_bounding_box = True
        if recurse_up:
            for parent in self.parents:
                parent.refresh_bounding_box()
        return self

    def is_point_touching(
        self,
        point: np.ndarray,
        buff: float = MED_SMALL_BUFF
    ) -> bool:
        '''
        判断某一点是否在本物件的包围框范围内
        '''
        bb = self.get_bounding_box()
        mins = (bb[0] - buff)
        maxs = (bb[2] + buff)
        return (point >= mins).all() and (point <= maxs).all()

    # Family matters
    """
    The getitem function is used to implement the indexing or slicing operator ([ ]) 
    for custom objects. This function takes an object and a key as arguments and is 
    expected to return the value associated with that key.
    """
    def __getitem__(self, value):
        if isinstance(value, slice):
            GroupClass = self.get_group_class()
            return GroupClass(*self.split().__getitem__(value))
        return self.split().__getitem__(value)

    """
    The iter function is used to implement the iteration protocol for custom objects. 
    This function takes an object as an argument and is expected to return an iterator 
    object that can traverse the elements of the object. 
    """
    def __iter__(self):
        return iter(self.split())

    """
    The len function is used to implement the len() built-in function for custom objects. 
    This function takes an object as an argument and is expected to return an integer 
    representing the length or size of the object.
    """
    def __len__(self):
        return len(self.split())

    def split(self):
        return self.submobjects

    def assemble_family(self):
        """
        To assemble something means to collect it together or 
        to fit the different parts of it together.
        """
        sub_families = (sm.get_family() for sm in self.submobjects)
        self.family = [self, *it.chain(*sub_families)]
        self.refresh_has_updater_status()
        self.refresh_bounding_box()
        for parent in self.parents:
            parent.assemble_family()
        return self

    def get_family(self, recurse: bool = True):
        if recurse:
            return self.family
        else:
            return [self]

    def family_members_with_points(self):
        return [m for m in self.get_family() if m.has_points()]

    def add(self, *mobjects: Mobject):
        '''
        将 ``mobjects`` 添加到子物体中

        VGroup中所有物体都在self.submobjects列表中
        '''
        if self in mobjects:
            raise Exception("Mobject cannot contain self")
        for mobject in mobjects:
            if mobject not in self.submobjects:
                self.submobjects.append(mobject)
            if self not in mobject.parents:
                mobject.parents.append(self)
        self.assemble_family()
        return self

    def remove(self, *mobjects: Mobject):
        '''
        将 ``mobjects`` 从子物体中移除
        '''
        for mobject in mobjects:
            if mobject in self.submobjects:
                self.submobjects.remove(mobject)
            if self in mobject.parents:
                mobject.parents.remove(self)
        self.assemble_family()
        return self

    def add_to_back(self, *mobjects: Mobject):
        '''
        将 ``mobjects`` 添加到子物体前面（覆盖关系在下）
        '''
        self.set_submobjects(list_update(mobjects, self.submobjects))
        return self

    def replace_submobject(self, index: int, new_submob: Mobject):
        '''
        用新的子物件代替指定索引处的旧子物件
        '''
        old_submob = self.submobjects[index]
        if self in old_submob.parents:
            old_submob.parents.remove(self)
        self.submobjects[index] = new_submob
        self.assemble_family()
        return self

    def insert_submobject(self, index: int, new_submob: Mobject):
        self.submobjects.insert(index, new_submob)
        self.assemble_family()
        return self

    def set_submobjects(self, submobject_list: list[Mobject]):
        '''
        重新设置子物件
        '''
        self.remove(*self.submobjects)
        self.add(*submobject_list)
        return self

    def digest_mobject_attrs(self):
        """
        Ensures all attributes which are mobjects are included
        in the submobjects list.

        确保所有对象属性都包含在子对象列表中
        """
        mobject_attrs = [x for x in list(self.__dict__.values()) if isinstance(x, Mobject)]
        self.set_submobjects(list_update(self.submobjects, mobject_attrs))
        return self

    # Submobject organization

    def arrange(
        self,
        direction: np.ndarray = RIGHT,
        center: bool = True,
        **kwargs
    ):
        '''
        将子物件按照 ``direction`` 方向排列
        '''
        for m1, m2 in zip(self.submobjects, self.submobjects[1:]):
            m2.next_to(m1, direction, **kwargs)
        if center:
            self.center()
        return self

    def arrange_in_grid(
        self,
        n_rows: int | None = None,
        n_cols: int | None = None,
        buff: float | None = None,
        h_buff: float | None = None,
        v_buff: float | None = None,
        buff_ratio: float | None = None,
        h_buff_ratio: float = 0.5,
        v_buff_ratio: float = 0.5,
        aligned_edge: np.ndarray = ORIGIN,
        fill_rows_first: bool = True
    ):
        '''将子物件按表格方式排列

        - ``n_rows``, ``n_cols`` : 行数、列数
        - ``v_buff``, ``h_buff`` : 行距、列距
        - ``aligned_edge`` : 对齐边缘
        '''
        submobs = self.submobjects
        if n_rows is None and n_cols is None:
            n_rows = int(np.sqrt(len(submobs)))
        if n_rows is None:
            n_rows = len(submobs) // n_cols
        if n_cols is None:
            n_cols = len(submobs) // n_rows

        if buff is not None:
            h_buff = buff
            v_buff = buff
        else:
            if buff_ratio is not None:
                v_buff_ratio = buff_ratio
                h_buff_ratio = buff_ratio
            if h_buff is None:
                h_buff = h_buff_ratio * self[0].get_width()
            if v_buff is None:
                v_buff = v_buff_ratio * self[0].get_height()

        x_unit = h_buff + max([sm.get_width() for sm in submobs])
        y_unit = v_buff + max([sm.get_height() for sm in submobs])

        for index, sm in enumerate(submobs):
            if fill_rows_first:
                x, y = index % n_cols, index // n_cols
            else:
                x, y = index // n_rows, index % n_rows
            sm.move_to(ORIGIN, aligned_edge)
            sm.shift(x * x_unit * RIGHT + y * y_unit * DOWN)
        self.center()
        return self

    def replicate(self, n: int) -> Group:
        """
        和arrange_in_grid()函数配合使用

        秀儿
        """
        return self.get_group_class()(
            *(self.copy() for x in range(n))
        )

    def get_grid(self, n_rows: int, n_cols: int, height: float | None = None, **kwargs):
        """
        Returns a new mobject containing multiple copies of this one
        arranged in a grid

        这个函数很有视觉表现力
        """
        grid = self.replicate(n_rows * n_cols)
        grid.arrange_in_grid(n_rows, n_cols, **kwargs)
        if height is not None:
            grid.set_height(height)
        return grid

    def sort(
        self,
        point_to_num_func: Callable[[np.ndarray], float] = lambda p: p[0],
        submob_func: Callable[[Mobject]] | None = None
    ):
        '''对子物件进行排序'''
        if submob_func is not None:
            self.submobjects.sort(key=submob_func)
        else:
            self.submobjects.sort(key=lambda m: point_to_num_func(m.get_center()))
        self.assemble_family()
        return self

    def shuffle(self, recurse: bool = False):
        '''随机打乱子物件的顺序'''
        if recurse:
            for submob in self.submobjects:
                submob.shuffle(recurse=True)
        random.shuffle(self.submobjects)
        self.assemble_family()
        return self

    # Copying

    def copy(self):
        # TODO, either justify reason for shallow copy, or
        # remove this redundancy everywhere
        # return self.deepcopy()
        """
        3b1b的代码中经常使用
        """
        parents = self.parents
        self.parents = []
        copy_mobject = copy.copy(self)
        self.parents = parents

        copy_mobject.data = dict(self.data)
        for key in self.data:
            copy_mobject.data[key] = self.data[key].copy()

        copy_mobject.uniforms = dict(self.uniforms)
        for key in self.uniforms:
            if isinstance(self.uniforms[key], np.ndarray):
                copy_mobject.uniforms[key] = self.uniforms[key].copy()

        copy_mobject.submobjects = []
        copy_mobject.add(*[sm.copy() for sm in self.submobjects])
        copy_mobject.match_updaters(self)

        copy_mobject.needs_new_bounding_box = self.needs_new_bounding_box

        # Make sure any mobject or numpy array attributes are copied
        family = self.get_family()
        for attr, value in list(self.__dict__.items()):
            if isinstance(value, Mobject) and value in family and value is not self:
                setattr(copy_mobject, attr, value.copy())
            if isinstance(value, np.ndarray):
                setattr(copy_mobject, attr, value.copy())
            if isinstance(value, ShaderWrapper):
                setattr(copy_mobject, attr, value.copy())
        return copy_mobject

    def deepcopy(self):
        parents = self.parents
        self.parents = []
        result = copy.deepcopy(self)
        self.parents = parents
        return result

    def generate_target(self, use_deepcopy: bool = False):
        '''通过复制自身作为自己的 target, 生成一个 target 属性'''
        self.target = None  # Prevent exponential explosion
        if use_deepcopy:
            self.target = self.deepcopy()
        else:
            self.target = self.copy()
        return self.target

    def save_state(self, use_deepcopy: bool = False):
        '''保留状态，即复制一份作为 ``saved_state`` 属性'''
        if hasattr(self, "saved_state"):
            # Prevent exponential growth of data
            self.saved_state = None
        if use_deepcopy:
            self.saved_state = self.deepcopy()
        else:
            self.saved_state = self.copy()
        return self

    def restore(self):
        '''恢复为 ``saved_state`` 的状态'''
        if not hasattr(self, "saved_state") or self.save_state is None:
            raise Exception("Trying to restore without having saved")
        self.become(self.saved_state)
        return self

    # Updating

    def init_updaters(self):
        self.time_based_updaters: list[TimeBasedUpdater] = []
        self.non_time_updaters: list[NonTimeUpdater] = []
        self.has_updaters: bool = False
        self.updating_suspended: bool = False

    def update(self, dt: float = 0, recurse: bool = True):
        '''更新物件状态，为 **动画 (Animation)** 、 **更新 (updater)** 调用'''
        if not self.has_updaters or self.updating_suspended:
            return self
        for updater in self.time_based_updaters:
            updater(self, dt)
        for updater in self.non_time_updaters:
            updater(self)
        if recurse:
            for submob in self.submobjects:
                submob.update(dt, recurse)
        return self

    def get_time_based_updaters(self) -> list[TimeBasedUpdater]:
        return self.time_based_updaters

    def has_time_based_updater(self) -> bool:
        return len(self.time_based_updaters) > 0

    def get_updaters(self) -> list[Updater]:
        return self.time_based_updaters + self.non_time_updaters

    def get_family_updaters(self) -> list[Updater]:
        return list(it.chain(*[sm.get_updaters() for sm in self.get_family()]))

    def add_updater(
        self,
        update_function: Updater,
        index: int | None = None,
        call_updater: bool = True
    ):
        '''添加 ``updater`` 函数'''
        if "dt" in get_parameters(update_function):
            updater_list = self.time_based_updaters
        else:
            updater_list = self.non_time_updaters

        if index is None:
            updater_list.append(update_function)
        else:
            updater_list.insert(index, update_function)

        self.refresh_has_updater_status()
        if call_updater:
            self.update(dt=0)
        return self

    def remove_updater(self, update_function: Updater):
        '''移除指定的 ``updater`` 函数'''
        for updater_list in [self.time_based_updaters, self.non_time_updaters]:
            while update_function in updater_list:
                updater_list.remove(update_function)
        self.refresh_has_updater_status()
        return self

    def clear_updaters(self, recurse: bool = True):
        '''清空所有的 ``updater`` 函数'''
        self.time_based_updaters = []
        self.non_time_updaters = []
        self.refresh_has_updater_status()
        if recurse:
            for submob in self.submobjects:
                submob.clear_updaters()
        return self

    def match_updaters(self, mobject: Mobject):
        '''将自己的 ``updater`` 函数与 ``mobject`` 匹配'''
        self.clear_updaters()
        for updater in mobject.get_updaters():
            self.add_updater(updater)
        return self

    def suspend_updating(self, recurse: bool = True):
        '''停止物件更新'''
        self.updating_suspended = True
        if recurse:
            for submob in self.submobjects:
                submob.suspend_updating(recurse)
        return self

    def resume_updating(self, recurse: bool = True, call_updater: bool = True):
        '''恢复物件更新'''
        self.updating_suspended = False
        if recurse:
            for submob in self.submobjects:
                submob.resume_updating(recurse)
        for parent in self.parents:
            parent.resume_updating(recurse=False, call_updater=False)
        if call_updater:
            self.update(dt=0, recurse=recurse)
        return self

    def refresh_has_updater_status(self):
        self.has_updaters = any(mob.get_updaters() for mob in self.get_family())
        return self

    # Transforming operations
    # 这些变换操作基本都是基于apply_points_function函数
    # 完全可以基于apply_function函数
    # 因为两者可以等价

    def shift(self, vector: np.ndarray):
        '''
        相对移动 vector 向量

        不是很理解about_edge = None的意思?
        如果about_edge = None且about_point = None
        那么, 对所有点的操作都是相对于坐标系原点
        '''
        # points是点集, vector是点
        # 广播机制
        self.apply_points_function(
            lambda points: points + vector,
            about_edge=None,
            works_on_bounding_box=True,
        )
        return self

    def scale(
        self,
        scale_factor: float | npt.ArrayLike,
        min_scale_factor: float = 1e-8,
        about_point: np.ndarray | None = None,
        about_edge: np.ndarray = ORIGIN
    ):
        """
        Default behavior is to scale about the center of the mobject.
        The argument about_edge can be a vector, indicating which side of
        the mobject to scale about, e.g., mob.scale(about_edge = RIGHT)
        scales about mob.get_right().

        Otherwise, if about_point is given a value, scaling is done with
        respect to that point.
        """
        """
        放大 (缩小) 到原来的 ``scale_factor`` 倍，可以传入 ``about_point/about_edge``
        """
        if isinstance(scale_factor, Iterable):
            scale_factor = np.array(scale_factor).clip(min=min_scale_factor)
        else:
            scale_factor = max(scale_factor, min_scale_factor)
        self.apply_points_function(
            lambda points: scale_factor * points, # 点集中的每个点都会乘以scale_factor
            about_point=about_point,
            about_edge=about_edge,
            works_on_bounding_box=True,
        )
        for mob in self.get_family():
            mob._handle_scale_side_effects(scale_factor)
        return self

    def _handle_scale_side_effects(self, scale_factor):
        # In case subclasses, such as DecimalNumber, need to make
        # any other changes when the size gets altered
        pass

    def stretch(self, factor: float, dim: int, **kwargs):
        '''
        把 ``dim`` 维度伸缩到原来的 ``factor`` 倍

        自己的思维方式中并没有建立一个array数组的第dim维的概念
        '''
        """
        points[:, dim] *= factor: This line of code is performing an operation 
        on a specific column (dim) of a 2D array (points). The : selects all 
        rows, and dim selects the specified column. Then, *= factor multiplies 
        each element in that column by the value of factor. This line essentially 
        scales the values in the specified column by the factor.
        """
        def func(points):
            points[:, dim] *= factor
            return points
        self.apply_points_function(func, works_on_bounding_box=True, **kwargs)
        return self

    def rotate_about_origin(self, angle: float, axis: np.ndarray = OUT):
        '''
        绕原点旋转 ``angle`` 弧度
        '''
        return self.rotate(angle, axis, about_point=ORIGIN)

    def rotate(
        self,
        angle: float,
        axis: np.ndarray = OUT,
        about_point: np.ndarray | None = None,
        **kwargs
    ):
        '''
        以 ``axis`` 为方向，``angle`` 为角度旋转，``kwargs`` 中可传入 ``about_point``

        result = np.dot(x, y)
        x为mxn阶矩阵
        y为nxp阶矩阵
        则相乘的结果result为mxp阶矩阵
        '''
        rot_matrix_T = rotation_matrix_transpose(angle, axis)
        self.apply_points_function(
            lambda points: np.dot(points, rot_matrix_T), # points是点集
            about_point,
            **kwargs
        )
        return self

    def flip(self, axis: np.ndarray = UP, **kwargs):
        '''
        绕 ``axis`` 轴翻转

        没想到flip是rotate的特例

        可以尝试将mob沿着y=x直线进行翻转
        axis = (1, 1, 0)
        self.rotate(TAU/2, axis/get_norm(axis), **kwargs)
        '''
        return self.rotate(TAU / 2, axis, **kwargs)

    """
    t = Triangle().set_color(RED)
    s = Square().set_color(YELLOW)
    c = Circle().set_color(GREEN)
    
    ani_t = t.animate.apply_function(lambda point: point+RIGHT*3).build()
    ani_s = s.animate.apply_points_function(lambda points: points+LEFT*3).build()
    #ani_c = c.animate.apply_matrix(np.identity(3)*3, about_point=(1,1,0)).build()
    ani_c = c.animate.apply_function(lambda point: np.dot(point, np.identity(3)*3),about_point=(1,1,0)).build()

    self.play(ani_t,
                ani_s,
                ani_c,
                run_time=3)
    """
    def apply_function(self, function: Callable[[np.ndarray], np.ndarray], **kwargs):
        '''
        把 ``function`` 作用到所有锚点上

        这个函数的功能和apply_points_function()函数一样
        为何定义这个函数
        
        apply_points_function()和apply_function()
        的参数都有一个是函数func, 只不过
        apply_points_function()的func作用的是点集
        apply_function()的func作用的是点 

        这个函数其实可以改个名: apply_point_function
        因为是作用在每一个point上

        需要极高的想象力！
        self.play(
            grid.animate.apply_function(
                lambda p: [
                    p[0] + 0.5 * math.sin(p[1]),
                    p[1] + 0.5 * math.sin(p[0]),
                    p[2]
                ]
            ),
            run_time=5,
        )
        '''
        # Default to applying matrix about the origin, not mobjects center
        if len(kwargs) == 0:
            kwargs["about_point"] = ORIGIN
        self.apply_points_function(
            lambda points: np.array([function(p) for p in points]),
            **kwargs
        )
        return self

    def apply_function_to_position(self, function: Callable[[np.ndarray], np.ndarray]):
        '''
        给物体所在的位置执行 ``function``
        '''
        self.move_to(function(self.get_center()))
        return self

    def apply_function_to_submobject_positions(
        self,
        function: Callable[[np.ndarray], np.ndarray]
    ):
        '''
        给所有子物体所在的位置执行 ``function``
        '''
        for submob in self.submobjects:
            submob.apply_function_to_position(function)
        return self

    """
    矩阵乘以向量
    point = np.array([1, 2])
    matrix = np.array([[5, 6],
                       [7, 8]])
    result = np.dot(point, matrix)
    print(result)
    [19 22]
    
    矩阵乘以矩阵
    points = np.array([[1, 2],
                      [3, 4]])
    matrix = np.array([[5, 6],
                       [7, 8]])
    result = np.dot(points, matrix)
    print(result)
    [[19 22]
     [43 50]]
    """
    def apply_matrix(self, matrix: npt.ArrayLike, **kwargs):
        # Default to applying matrix about the origin, not mobjects center
        '''
        把 ``matrix`` 矩阵作用到所有点上

        参考rotate()函数的实现方式
        '''
        if ("about_point" not in kwargs) and ("about_edge" not in kwargs):
            kwargs["about_point"] = ORIGIN
        """
        The np.identity function in Python is part of the NumPy library and is used to 
        create an identity matrix. An identity matrix is a square matrix with ones on 
        the main diagonal and zeros elsewhere. 

        这里取对角线元素为1, 有深意
        """
        full_matrix = np.identity(self.dim)
        matrix = np.array(matrix)
        """
        点睛之笔

        assigning the values of a matrix to a larger matrix. The larger matrix is called 
        full_matrix and it has a size that is greater than or equal to the size of the 
        original matrix. The matrix variable is the original matrix that we want to assign 
        to the larger matrix.

        这里的matrix是二阶方阵
        比如旋转矩阵
        由于mob是三维对象
        所以需要将matrix扩展为三阶方阵
        """
        full_matrix[:matrix.shape[0], :matrix.shape[1]] = matrix
        # 对比下rotate函数
        self.apply_points_function(
            lambda points: np.dot(points, full_matrix.T),
            **kwargs
        )
        return self

    """
    数学和想象力需要增强：思考这种操作的几何意义
    self.play(
        moving_c_grid.animate.apply_complex_function(lambda z: z**2),
        run_time=6,
    )
    """
    def apply_complex_function(self, function: Callable[[complex], complex], **kwargs):
        '''
        施加一个复变函数
        作用在每一个点，而不是点集
        '''
        def R3_func(point):
            x, y, z = point
            # 这里需要思考复数乘法的几何意义
            # 旋转和缩放
            # 可以想象z的幅度和角度
            # z = r*e^(i*theta)
            # z^2 = r^2*e^(i*2*theta)
            # z^2的幅度是r^2, 角度是2*theta
            xy_complex = function(complex(x, y))
            return [
                xy_complex.real,
                xy_complex.imag,
                z
            ]
        return self.apply_function(R3_func, **kwargs)

    def wag(
        self,
        direction: np.ndarray = RIGHT,
        axis: np.ndarray = DOWN,
        wag_factor: float = 1.0
    ):
        '''
        沿 ``axis`` 轴 ``direction`` 方向摇摆 ``wag_factor``
        '''
        for mob in self.family_members_with_points():
            alphas = np.dot(mob.get_points(), np.transpose(axis))
            alphas -= min(alphas)
            alphas /= max(alphas)
            alphas = alphas**wag_factor
            mob.set_points(mob.get_points() + np.dot(
                alphas.reshape((len(alphas), 1)),
                np.array(direction).reshape((1, mob.dim))
            ))
        return self

    # Positioning methods

    def center(self):
        '''
        放到画面中心

        shift操作的核心是找到target_point和align_point
        然后计算shift vector

        target_point: ORIGIN = [0, 0, 0]
        align_point: self.get_center()

        shift vector = target_point - align_point = -self.get_center()
        '''
        self.shift(-self.get_center())
        return self

    def align_on_border(
        self,
        direction: np.ndarray,
        buff: float = DEFAULT_MOBJECT_TO_EDGE_BUFFER
    ):
        """
        Direction just needs to be a vector pointing towards side or
        corner in the 2d plane.
        """
        """
        以 ``direction`` 这个边界对齐

        将mob移到frame的边缘
        buff是边缘和mob的距离
        """
        # 哇！点睛之笔
        # 和`next_to`方法有异曲同工之妙
        # 同时，强化对frame的概念
        target_point = np.sign(direction) * (FRAME_X_RADIUS, FRAME_Y_RADIUS, 0)
        point_to_align = self.get_bounding_box_point(direction)
        shift_val = target_point - point_to_align - buff * np.array(direction)
        # 这里为何取绝对值？
        shift_val = shift_val * abs(np.sign(direction))
        self.shift(shift_val)
        return self

    def to_corner(
        self,
        corner: np.ndarray = LEFT + DOWN,
        buff: float = DEFAULT_MOBJECT_TO_EDGE_BUFFER
    ):
        '''
        和 ``corner`` 这个角落对齐
        '''
        return self.align_on_border(corner, buff)

    def to_edge(
        self,
        edge: np.ndarray = LEFT,
        buff: float = DEFAULT_MOBJECT_TO_EDGE_BUFFER
    ):
        '''
        和 ``edge`` 这个边对齐
        '''
        return self.align_on_border(edge, buff)

    def next_to(
        self,
        mobject_or_point: Mobject | np.ndarray,
        direction: np.ndarray = RIGHT,
        buff: float = DEFAULT_MOBJECT_TO_MOBJECT_BUFFER,
        aligned_edge: np.ndarray = ORIGIN,
        submobject_to_align: Mobject | None = None,
        index_of_submobject_to_align: int | slice | None = None,
        coor_mask: np.ndarray = np.array([1, 1, 1]),
    ):
        '''
        放到 ``mobject_or_point`` 旁边

        任何复杂问题都可以分解为若干个简单的问题
        对于这段源码，简单问题之一：搞清楚`get_bounding_box_point`函数的作用
        '''
        if isinstance(mobject_or_point, Mobject):
            mob = mobject_or_point
            if index_of_submobject_to_align is not None:
                target_aligner = mob[index_of_submobject_to_align]
            else:
                target_aligner = mob
            # 在target的bounding box上找到一个点
            target_point = target_aligner.get_bounding_box_point(
                aligned_edge + direction
            )
        else:
            target_point = mobject_or_point
        if submobject_to_align is not None:
            aligner = submobject_to_align
        elif index_of_submobject_to_align is not None:
            aligner = self[index_of_submobject_to_align]
        else:
            aligner = self
        # 在aligner的bounding box上找到一个点
        point_to_align = aligner.get_bounding_box_point(aligned_edge - direction)
        # mobject的移动就是把这两个点重合
        # shift函数是作用于所有点的，那么解决问题的思路就是找到两个mob的可以对其的点，从而计算出shift vector
        self.shift((target_point - point_to_align + buff * direction) * coor_mask)
        return self

    def shift_onto_screen(self, **kwargs):
        '''
        确保在画面中
        '''
        space_lengths = [FRAME_X_RADIUS, FRAME_Y_RADIUS]
        for vect in UP, DOWN, LEFT, RIGHT:
            dim = np.argmax(np.abs(vect))
            buff = kwargs.get("buff", DEFAULT_MOBJECT_TO_EDGE_BUFFER)
            max_val = space_lengths[dim] - buff
            edge_center = self.get_edge_center(vect)
            # vect是单位向量，下面的点积计算的是edge_center在vect方向上的投影
            if np.dot(edge_center, vect) > max_val:
                self.to_edge(vect, **kwargs)
        return self

    def is_off_screen(self):
        '''
        判断是否在画面外
        '''
        # 思维模型：两个框
        # bounding box是一个框，frame是另一个框
        if self.get_left()[0] > FRAME_X_RADIUS:
            return True
        if self.get_right()[0] < -FRAME_X_RADIUS:
            return True
        if self.get_bottom()[1] > FRAME_Y_RADIUS:
            return True
        if self.get_top()[1] < -FRAME_Y_RADIUS:
            return True
        return False

    def stretch_about_point(self, factor: float, dim: int, point: np.ndarray):
        return self.stretch(factor, dim, about_point=point)

    def stretch_in_place(self, factor: float, dim: int):
        # Now redundant with stretch
        return self.stretch(factor, dim)

    def rescale_to_fit(self, length: float, dim: int, stretch: bool = False, **kwargs):
        old_length = self.length_over_dim(dim)
        if old_length == 0:
            return self
        if stretch:
            self.stretch(length / old_length, dim, **kwargs)
        else:
            self.scale(length / old_length, **kwargs)
        return self

    def stretch_to_fit_width(self, width: float, **kwargs):
        '''拉伸以适应宽度'''
        return self.rescale_to_fit(width, 0, stretch=True, **kwargs)

    def stretch_to_fit_height(self, height: float, **kwargs):
        '''拉伸以适应高度'''
        return self.rescale_to_fit(height, 1, stretch=True, **kwargs)

    def stretch_to_fit_depth(self, depth: float, **kwargs):
        '''拉伸以适应深度'''
        return self.rescale_to_fit(depth, 2, stretch=True, **kwargs)

    def set_width(self, width: float, stretch: bool = False, **kwargs):
        '''保持原比例设置宽度'''
        return self.rescale_to_fit(width, 0, stretch=stretch, **kwargs)

    def set_height(self, height: float, stretch: bool = False, **kwargs):
        '''保持原比例设置高度'''
        return self.rescale_to_fit(height, 1, stretch=stretch, **kwargs)

    def set_depth(self, depth: float, stretch: bool = False, **kwargs):
        '''保持原比例设置深度'''
        return self.rescale_to_fit(depth, 2, stretch=stretch, **kwargs)

    def set_max_width(self, max_width: float, **kwargs):
        '''设置最大宽度'''
        if self.get_width() > max_width:
            self.set_width(max_width, **kwargs)
        return self

    def set_max_height(self, max_height: float, **kwargs):
        '''设置最大高度'''
        if self.get_height() > max_height:
            self.set_height(max_height, **kwargs)
        return self

    def set_max_depth(self, max_depth: float, **kwargs):
        '''设置最大深度'''
        if self.get_depth() > max_depth:
            self.set_depth(max_depth, **kwargs)
        return self

    def set_min_width(self, min_width: float, **kwargs):
        if self.get_width() < min_width:
            self.set_width(min_width, **kwargs)
        return self

    def set_min_height(self, min_height: float, **kwargs):
        if self.get_height() < min_height:
            self.set_height(min_height, **kwargs)
        return self

    def set_min_depth(self, min_depth: float, **kwargs):
        if self.get_depth() < min_depth:
            self.set_depth(min_depth, **kwargs)
        return self

    def set_coord(self, value: float, dim: int, direction: np.ndarray = ORIGIN):
        '''移动到 ``dim`` 维度的 ``value`` 位置'''
        curr = self.get_coord(dim, direction)
        shift_vect = np.zeros(self.dim)
        shift_vect[dim] = value - curr
        self.shift(shift_vect)
        return self

    def set_x(self, x: float, direction: np.ndarray = ORIGIN):
        '''将 x 轴坐标设置为 x'''
        return self.set_coord(x, 0, direction)

    def set_y(self, y: float, direction: np.ndarray = ORIGIN):
        '''将 y 轴坐标设置为 y'''
        return self.set_coord(y, 1, direction)

    def set_z(self, z: float, direction: np.ndarray = ORIGIN):
        '''将 z 轴坐标设置为 z'''
        return self.set_coord(z, 2, direction)

    def space_out_submobjects(self, factor: float = 1.5, **kwargs):
        '''调整子物件的间距为 ``factor`` 倍'''
        """
        这个函数真是太秀了

        self.scale()函数默认的缩放中心是mob的center
        这里的奥妙在于mob的center和每一个submob的中心不一致
        """
        self.scale(factor, **kwargs)
        for submob in self.submobjects:
            submob.scale(1. / factor)
        return self

    def move_to(
        self,
        point_or_mobject: Mobject | np.ndarray,
        aligned_edge: np.ndarray = ORIGIN,
        coor_mask: np.ndarray = np.array([1, 1, 1])
    ):
        '''移动到 ``point_or_mobject`` 的位置'''
        if isinstance(point_or_mobject, Mobject):
            target = point_or_mobject.get_bounding_box_point(aligned_edge)
        else:
            target = point_or_mobject
        point_to_align = self.get_bounding_box_point(aligned_edge)
        self.shift((target - point_to_align) * coor_mask)
        return self

    def replace(self, mobject: Mobject, dim_to_match: int = 0, stretch: bool = False):
        '''放到和 ``mobject`` 的位置，并且大小相同'''
        if not mobject.get_num_points() and not mobject.submobjects:
            self.scale(0)
            return self
        if stretch:
            for i in range(self.dim):
                self.rescale_to_fit(mobject.length_over_dim(i), i, stretch=True)
        else:
            self.rescale_to_fit(
                mobject.length_over_dim(dim_to_match),
                dim_to_match,
                stretch=False
            )
        self.shift(mobject.get_center() - self.get_center())
        return self

    def surround(
        self,
        mobject: Mobject,
        dim_to_match: int = 0,
        stretch: bool = False,
        buff: float = MED_SMALL_BUFF
    ):
        '''环绕着 mobject'''
        self.replace(mobject, dim_to_match, stretch)
        length = mobject.length_over_dim(dim_to_match)
        self.scale((length + buff) / length)
        return self

    def put_start_and_end_on(self, start: np.ndarray, end: np.ndarray):
        '''
        把物体的起点和终点通过旋转缩放放在 ``start`` 和 ``end``
        
        这个函数可以作为一个练习题，自己实现一遍
        '''
        curr_start, curr_end = self.get_start_and_end()
        curr_vect = curr_end - curr_start
        if np.all(curr_vect == 0):
            raise Exception("Cannot position endpoints of closed loop")
        target_vect = end - start
        # 指定about_point是curr_start
        self.scale(
            get_norm(target_vect) / get_norm(curr_vect),
            about_point=curr_start,
        )
        # 以OUT为轴，旋转到xoy平面的投影方向一致
        self.rotate(
            angle_of_vector(target_vect) - angle_of_vector(curr_vect),
        )
        # 需要认真分析
        self.rotate(
            np.arctan2(curr_vect[2], get_norm(curr_vect[:2])) - np.arctan2(target_vect[2], get_norm(target_vect[:2])),
            axis=np.array([-target_vect[1], target_vect[0], 0]),
        )
        self.shift(start - self.get_start())
        return self

    # Color functions

    def set_rgba_array(
        self,
        rgba_array: npt.ArrayLike, # 二维数组
        name: str = "rgbas",
        recurse: bool = False
    ):
        '''
        将 rgbas 成员变量设置为指定的值
        
        在vmobject对象中, 会删除rgbas
        添加fill_rgba和stroke_rgba

        from manimlib import *

        class test(Scene):
            def construct(self): 
                plane = NumberPlane()
                self.add(plane)
                line = Line([-3,-3,0], [3,3,0])
                rgbas = [[0.95882272, 0.0277352,  0.061623,   1.        ]]	
                rgbas = [[0.95882272, 0.0277352,  0.061623,   1.        ],
                        [0.03781613, 0.96890806, 0.05165273, 1.        ],
                        [0.0795209,  0.03976045, 0.90007538, 1.        ]]
                line.set_rgba_array(rgbas, "stroke_rgba")
                self.add(line)
        '''
        for mob in self.get_family(recurse):
            mob.data[name] = np.array(rgba_array)
        return self

    def set_color_by_rgba_func(
        self,
        func: Callable[[np.ndarray], Sequence[float]],
        recurse: bool = True
    ):
        """
        Func should take in a point in R3 and output an rgba value
        """
        """
        传入一个函数，这个函数接受一个三维坐标，将物件按照这个函数的方法设置颜色，包含透明度
        """
        for mob in self.get_family(recurse):
            #rgba_arrayg维度n*4
            rgba_array = [func(point) for point in mob.get_points()]
            mob.set_rgba_array(rgba_array)
        return self

    def set_color_by_rgb_func(
        self,
        func: Callable[[np.ndarray], Sequence[float]],
        opacity: float = 1,
        recurse: bool = True
    ):
        """
        Func should take in a point in R3 and output an rgb value
        """
        """
        传入一个函数，这个函数接受一个三维坐标，将物件按照这个函数的方法设置颜色
        """
        for mob in self.get_family(recurse):
            rgba_array = [[*func(point), opacity] for point in mob.get_points()]
            mob.set_rgba_array(rgba_array)
        return self

    """
    d = Mobject()
    d.set_rgba_array_by_color(color=[RED, GREEN, BLUE], opacity=0.5)
    print(d.data['rgbas'])

    [[0.98823529 0.38431373 0.33333333 0.5       ]
    [0.51372549  0.75686275 0.40392157 0.5       ]
    [0.34509804  0.76862745 0.86666667 0.5       ]]

       
    print(color_to_rgb(RED))
    print(color_to_rgb(GREEN))
    print(color_to_rgb(BLUE))

    [0.98823529 0.38431373 0.33333333]
    [0.51372549 0.75686275 0.40392157]
    [0.34509804 0.76862745 0.86666667]
    """
    def set_rgba_array_by_color(
        self,
        color: ManimColor | None = None,
        opacity: float | None = None,
        name: str = "rgbas",
        recurse: bool = True
    ):
        '''通过颜色设置 rgba_array 成员以染色'''
        max_len = 0
        if color is not None:
            rgbs = np.array([color_to_rgb(c) for c in listify(color)])
            max_len = len(rgbs)
        if opacity is not None:
            opacities = np.array(listify(opacity))
            max_len = max(max_len, len(opacities))

        for mob in self.get_family(recurse):
            if max_len > len(mob.data[name]):
                mob.data[name] = resize_array(mob.data[name], max_len)
            size = len(mob.data[name])
            if color is not None:
                mob.data[name][:, :3] = resize_array(rgbs, size)
            if opacity is not None:
                mob.data[name][:, 3] = resize_array(opacities, size)
        return self

    def set_color(self, color: ManimColor, opacity: float | None = None, recurse: bool = True):
        '''设置颜色'''
        self.set_rgba_array_by_color(color, opacity, recurse=False)
        # Recurse to submobjects differently from how set_rgba_array_by_color
        # in case they implement set_color differently
        if recurse:
            for submob in self.submobjects:
                submob.set_color(color, recurse=True)
        return self

    def set_opacity(self, opacity: float, recurse: bool = True):
        '''设置透明度'''
        self.set_rgba_array_by_color(color=None, opacity=opacity, recurse=False)
        if recurse:
            for submob in self.submobjects:
                submob.set_opacity(opacity, recurse=True)
        return self

    def get_color(self) -> str:
        return rgb_to_hex(self.data["rgbas"][0, :3])

    def get_opacity(self) -> float:
        return self.data["rgbas"][0, 3]

    def set_color_by_gradient(self, *colors: ManimColor):
        '''渐变染色'''
        self.set_submobject_colors_by_gradient(*colors)
        return self

    def set_submobject_colors_by_gradient(self, *colors: ManimColor):
        if len(colors) == 0:
            raise Exception("Need at least one color")
        elif len(colors) == 1:
            return self.set_color(*colors)

        # mobs = self.family_members_with_points()
        mobs = self.submobjects
        new_colors = color_gradient(colors, len(mobs))

        for mob, color in zip(mobs, new_colors):
            mob.set_color(color)
        return self

    def fade(self, darkness: float = 0.5, recurse: bool = True):
        '''变暗'''
        self.set_opacity(1.0 - darkness, recurse=recurse)

    def get_reflectiveness(self) -> float:
        '''获取反光度'''
        return self.uniforms["reflectiveness"]

    def set_reflectiveness(self, reflectiveness: float, recurse: bool = True):
        for mob in self.get_family(recurse):
            mob.uniforms["reflectiveness"] = reflectiveness
        return self

    def get_shadow(self) -> float:
        return self.uniforms["shadow"]

    def set_shadow(self, shadow: float, recurse: bool = True):
        for mob in self.get_family(recurse):
            mob.uniforms["shadow"] = shadow
        return self

    def get_gloss(self) -> float:
        return self.uniforms["gloss"]

    def set_gloss(self, gloss: float, recurse: bool = True):
        for mob in self.get_family(recurse):
            mob.uniforms["gloss"] = gloss
        return self

    # Background rectangle

    def add_background_rectangle(
        self,
        color: ManimColor | None = None,
        opacity: float = 0.75,
        **kwargs
    ):
        # TODO, this does not behave well when the mobject has points,
        # since it gets displayed on top
        from manimlib.mobject.shape_matchers import BackgroundRectangle
        self.background_rectangle = BackgroundRectangle(
            self, color=color,
            fill_opacity=opacity,
            **kwargs
        )
        self.add_to_back(self.background_rectangle)
        return self

    def add_background_rectangle_to_submobjects(self, **kwargs):
        for submobject in self.submobjects:
            submobject.add_background_rectangle(**kwargs)
        return self

    def add_background_rectangle_to_family_members_with_points(self, **kwargs):
        for mob in self.family_members_with_points():
            mob.add_background_rectangle(**kwargs)
        return self

    # Getters
    # get_bounding_box_point函数是核心，其他的很多函数都是基于这个函数
    def get_bounding_box_point(self, direction: np.ndarray) -> np.ndarray:
        """
        给定direction, 获取包围框上的点

        例如:
        给定RIGHT, 获取包围框右边的点
        给定RIGHT+UP, 获取包围框右上角的点

        延伸:
        知道了包围框的三个点，我们就可以计算出包围框上的一些关键点
        如果mob是正方体的, 我们可以计算出六个面和12条边的中心点以及顶点

        c = Cube()
        l = c.get_bounding_box_point(DOWN+RIGHT+IN)
        s = Sphere(radius=0.1).move_to(l).set_color(RED)

        延伸2:
        通过包围框上的点
        我们可以计算出构成mob的边框上的任何一点
        也可以计算出构成mob的面上的任何一点
        """
        bb = self.get_bounding_box()
        # 没有理解indices的作用
        # bb有3个点，我们依次对其编号：0,1,2
        # 对于RIGHT，indices = [2,1,1]
        # 代表着最终返回的点是由bb的第1个点和第2个点计算得出的
        indices = (np.sign(direction) + 1).astype(int)
        # 这样做的原理是什么？
        # 在这里，不要把bb理解成矩阵，理解成三个点构成的列表更好
        # direction上的点都可以由bb上既有的点拼接得到
        return np.array([
            bb[indices[i]][i]
            for i in range(3)
        ])

    def get_edge_center(self, direction: np.ndarray) -> np.ndarray:
        '''
        获取某一边缘的中心
        
        direction: 
        LEFT
        RIGHT
        ...
        '''
        return self.get_bounding_box_point(direction)

    def get_corner(self, direction: np.ndarray) -> np.ndarray:
        '''
        获取某一个角落
        
        direction:
        LEFT+UP
        LEFT+DOWN
        ...
        '''
        return self.get_bounding_box_point(direction)

    def get_center(self) -> np.ndarray:
        return self.get_bounding_box()[1]

    def get_center_of_mass(self) -> np.ndarray:
        return self.get_all_points().mean(0)

    def get_boundary_point(self, direction: np.ndarray) -> np.ndarray:
        all_points = self.get_all_points()
        boundary_directions = all_points - self.get_center()
        norms = np.linalg.norm(boundary_directions, axis=1)
        boundary_directions /= np.repeat(norms, 3).reshape((len(norms), 3))
        index = np.argmax(np.dot(boundary_directions, np.array(direction).T))
        return all_points[index]

    def get_continuous_bounding_box_point(self, direction: np.ndarray) -> np.ndarray:
        dl, center, ur = self.get_bounding_box()
        corner_vect = (ur - center)
        return center + direction / np.max(np.abs(np.true_divide(
            direction, corner_vect,
            out=np.zeros(len(direction)),
            where=((corner_vect) != 0)
        )))

    def get_top(self) -> np.ndarray:
        '''获取上边缘中心'''
        return self.get_edge_center(UP)

    def get_bottom(self) -> np.ndarray:
        '''获取下边缘中心'''
        return self.get_edge_center(DOWN)

    def get_right(self) -> np.ndarray:
        '''获取右边缘中心'''
        return self.get_edge_center(RIGHT)

    def get_left(self) -> np.ndarray:
        '''获取左边缘中心'''
        return self.get_edge_center(LEFT)

    def get_zenith(self) -> np.ndarray:
        '''获取外边缘中心（这里的外，指垂直于屏幕向外的平面）'''
        return self.get_edge_center(OUT)

    def get_nadir(self) -> np.ndarray:
        '''获取内边缘中心（这里的内，指垂直于屏幕向内的平面）'''
        return self.get_edge_center(IN)

    def length_over_dim(self, dim: int) -> float:
        '''在 ``dim`` 维度的长度'''
        bb = self.get_bounding_box()
        return abs((bb[2] - bb[0])[dim])

    def get_width(self) -> float:
        '''获取物件宽度'''
        return self.length_over_dim(0)

    def get_height(self) -> float:
        '''获取物件高度'''
        return self.length_over_dim(1)

    def get_depth(self) -> float:
        '''获取物件深度（即 z 轴方向的宽度）'''
        return self.length_over_dim(2)

    def get_coord(self, dim: int, direction: np.ndarray = ORIGIN) -> float:
        """
        Meant to generalize get_x, get_y, get_z
        获取物件在 ``dim`` 维度上的坐标

        当direction为ORIGIN的时候
        获取的是中心
        """
        return self.get_bounding_box_point(direction)[dim]

    def get_x(self, direction=ORIGIN) -> float:
        '''获取 x 坐标'''
        return self.get_coord(0, direction)

    def get_y(self, direction=ORIGIN) -> float:
        '''获取 y 坐标'''
        return self.get_coord(1, direction)

    def get_z(self, direction=ORIGIN) -> float:
        '''获取 z 坐标'''
        return self.get_coord(2, direction)

    def get_start(self) -> np.ndarray:
        '''获取起始点'''
        self.throw_error_if_no_points()
        return self.get_points()[0].copy()

    def get_end(self) -> np.ndarray:
        '''获取终止点'''
        self.throw_error_if_no_points()
        return self.get_points()[-1].copy()

    def get_start_and_end(self) -> tuple(np.ndarray, np.ndarray):
        '''获取起始点和终止点'''
        self.throw_error_if_no_points()
        points = self.get_points()
        return (points[0].copy(), points[-1].copy())

    # 这个函数的用处很多
    def point_from_proportion(self, alpha: float) -> np.ndarray:
        '''
        在整条路径上占比为 ``alpha`` 处的点

        在vmobject上重新定义了这个函数
        '''
        # 这里的points并不全是曲线上的点，anchor + handle
        points = self.get_points()
        # 第一次插值
        i, subalpha = integer_interpolate(0, len(points) - 1, alpha)
        # 第二次插值
        return interpolate(points[i], points[i + 1], subalpha)

    def pfp(self, alpha):
        """Abbreviation fo point_from_proportion"""
        return self.point_from_proportion(alpha)

    def get_pieces(self, n_pieces: int) -> Group:
        '''将物体拆成 ``n_pieces`` 个部分，便于部分解决 3D 中透视问题'''
        template = self.copy()
        template.set_submobjects([])
        alphas = np.linspace(0, 1, n_pieces + 1)
        return Group(*[
            template.copy().pointwise_become_partial(
                self, a1, a2
            )
            for a1, a2 in zip(alphas[:-1], alphas[1:])
        ])

    def get_z_index_reference_point(self):
        # TODO, better place to define default z_index_group?
        z_index_group = getattr(self, "z_index_group", self)
        return z_index_group.get_center()

    # Match other mobject properties

    def match_color(self, mobject: Mobject):
        '''将自己的颜色与 ``mobject`` 匹配'''
        return self.set_color(mobject.get_color())

    def match_dim_size(self, mobject: Mobject, dim: int, **kwargs):
        return self.rescale_to_fit(
            mobject.length_over_dim(dim), dim,
            **kwargs
        )

    def match_width(self, mobject: Mobject, **kwargs):
        '''将自己的宽度与 ``mobject`` 匹配'''
        return self.match_dim_size(mobject, 0, **kwargs)

    def match_height(self, mobject: Mobject, **kwargs):
        '''将自己的高度与 ``mobject`` 匹配'''
        return self.match_dim_size(mobject, 1, **kwargs)

    def match_depth(self, mobject: Mobject, **kwargs):
        '''将自己的深度与 ``mobject`` 匹配（这里的深度指 z 轴方向的宽度）'''
        return self.match_dim_size(mobject, 2, **kwargs)

    def match_coord(
        self,
        mobject_or_point: Mobject | np.ndarray,
        dim: int,
        direction: np.ndarray = ORIGIN
    ):
        if isinstance(mobject_or_point, Mobject):
            coord = mobject_or_point.get_coord(dim, direction)
        else:
            coord = mobject_or_point[dim]
        return self.set_coord(coord, dim=dim, direction=direction)

    def match_x(
        self,
        mobject_or_point: Mobject | np.ndarray,
        direction: np.ndarray = ORIGIN
    ):
        '''移动到与 ``mobject`` 相同的 x 轴坐标'''
        return self.match_coord(mobject_or_point, 0, direction)

    def match_y(
        self,
        mobject_or_point: Mobject | np.ndarray,
        direction: np.ndarray = ORIGIN
    ):
        '''移动到与 ``mobject`` 相同的 y 轴坐标'''
        return self.match_coord(mobject_or_point, 1, direction)

    def match_z(
        self,
        mobject_or_point: Mobject | np.ndarray,
        direction: np.ndarray = ORIGIN
    ):
        '''移动到与 ``mobject`` 相同的 z 轴坐标'''
        return self.match_coord(mobject_or_point, 2, direction)

    def align_to(
        self,
        mobject_or_point: Mobject | np.ndarray,
        direction: np.ndarray = ORIGIN
    ):
        """
        Examples:
        mob1.align_to(mob2, UP) moves mob1 vertically so that its
        top edge lines ups with mob2's top edge.

        mob1.align_to(mob2, alignment_vect = RIGHT) moves mob1
        horizontally so that it's center is directly above/below
        the center of mob2
        """
        """
        对齐
        
        例子：
        ``mob1.align_to(mob2, UP)`` 会将 ``mob1`` 垂直移动，顶部与 ``mob2`` 的上边缘对齐
        """
        if isinstance(mobject_or_point, Mobject):
            point = mobject_or_point.get_bounding_box_point(direction)
        else:
            point = mobject_or_point

        for dim in range(self.dim):
            if direction[dim] != 0:
                self.set_coord(point[dim], dim, direction)
        return self

    def get_group_class(self):
        return Group

    # Alignment

    def align_data_and_family(self, mobject: Mobject) -> None:
        self.align_family(mobject)
        self.align_data(mobject)

    def align_data(self, mobject: Mobject) -> None:
        # In case any data arrays get resized when aligned to shader data
        self.refresh_shader_data()
        for mob1, mob2 in zip(self.get_family(), mobject.get_family()):
            # Separate out how points are treated so that subclasses
            # can handle that case differently if they choose
            mob1.align_points(mob2)
            for key in mob1.data.keys() & mob2.data.keys():
                if key == "points":
                    continue
                arr1 = mob1.data[key]
                arr2 = mob2.data[key]
                if len(arr2) > len(arr1):
                    mob1.data[key] = resize_preserving_order(arr1, len(arr2))
                elif len(arr1) > len(arr2):
                    mob2.data[key] = resize_preserving_order(arr2, len(arr1))

    def align_points(self, mobject: Mobject):
        max_len = max(self.get_num_points(), mobject.get_num_points())
        for mob in (self, mobject):
            mob.resize_points(max_len, resize_func=resize_preserving_order)
        return self

    def align_family(self, mobject: Mobject):
        mob1 = self
        mob2 = mobject
        n1 = len(mob1)
        n2 = len(mob2)
        if n1 != n2:
            mob1.add_n_more_submobjects(max(0, n2 - n1))
            mob2.add_n_more_submobjects(max(0, n1 - n2))
        # Recurse
        for sm1, sm2 in zip(mob1.submobjects, mob2.submobjects):
            sm1.align_family(sm2)
        return self

    def push_self_into_submobjects(self):
        copy = self.deepcopy()
        copy.set_submobjects([])
        self.resize_points(0)
        self.add(copy)
        return self

    def add_n_more_submobjects(self, n: int):
        if n == 0:
            return self

        curr = len(self.submobjects)
        if curr == 0:
            # If empty, simply add n point mobjects
            null_mob = self.copy()
            null_mob.set_points([self.get_center()])
            self.set_submobjects([
                null_mob.copy()
                for k in range(n)
            ])
            return self
        target = curr + n
        repeat_indices = (np.arange(target) * curr) // target
        split_factors = [
            (repeat_indices == i).sum()
            for i in range(curr)
        ]
        new_submobs = []
        for submob, sf in zip(self.submobjects, split_factors):
            new_submobs.append(submob)
            for k in range(1, sf):
                new_submob = submob.copy()
                # If the submobject is at all transparent, then
                # make the copy completely transparent
                if submob.get_opacity() < 1:
                    new_submob.set_opacity(0)
                new_submobs.append(new_submob)
        self.set_submobjects(new_submobs)
        return self

    # Interpolate

    def interpolate(
        self,
        mobject1: Mobject,
        mobject2: Mobject,
        alpha: float,
        path_func: Callable[[np.ndarray, np.ndarray, float], np.ndarray] = straight_path
    ):
        """
        需要先对齐两个mob的点集大小

        alpha*arr1 + (1-alpha)*arr2
        arr1和arr2必须是同维度
        """
        for key in self.data:
            if key in self.locked_data_keys:
                continue
            if len(self.data[key]) == 0:
                continue
            if key not in mobject1.data or key not in mobject2.data:
                continue

            if key in ("points", "bounding_box"):
                func = path_func
            else:
                func = interpolate

            self.data[key][:] = func(
                mobject1.data[key],
                mobject2.data[key],
                alpha
            )
        for key in self.uniforms:
            self.uniforms[key] = interpolate(
                mobject1.uniforms[key],
                mobject2.uniforms[key],
                alpha
            )
        return self

    def pointwise_become_partial(self, mobject, a, b):
        """
        Set points in such a way as to become only
        part of mobject.
        Inputs 0 <= a < b <= 1 determine what portion
        of mobject to become.
        """
        """
        生成一个路径百分比从 a 到 b 的物件
        """
        pass  # To implement in subclass

    def become(self, mobject: Mobject):
        """
        Edit all data and submobjects to be idential
        to another mobject
        """
        """
        重构物件数据并将它变成传入的 ``mobject``
        """
        self.align_family(mobject)
        for sm1, sm2 in zip(self.get_family(), mobject.get_family()):
            sm1.set_data(sm2.data)
            sm1.set_uniforms(sm2.uniforms)
        self.refresh_bounding_box(recurse_down=True)
        return self

    # Locking data

    def lock_data(self, keys: Iterable[str]):
        """
        To speed up some animations, particularly transformations,
        it can be handy to acknowledge which pieces of data
        won't change during the animation so that calls to
        interpolate can skip this, and so that it's not
        read into the shader_wrapper objects needlessly
        """
        """
        为了加速一些动画，尤其是 Transform, 它可以很方便地确认哪些数据片段不会在动画期间改变
        以便调用插值可以跳过这一点，这样它就不会被不必要地读入 shader_wrapper 对象
        """
        if self.has_updaters:
            return
        # Be sure shader data has most up to date information
        self.refresh_shader_data()
        self.locked_data_keys = set(keys)

    def lock_matching_data(self, mobject1: Mobject, mobject2: Mobject):
        for sm, sm1, sm2 in zip(self.get_family(), mobject1.get_family(), mobject2.get_family()):
            keys = sm.data.keys() & sm1.data.keys() & sm2.data.keys()
            sm.lock_data(list(filter(
                lambda key: np.all(sm1.data[key] == sm2.data[key]),
                keys,
            )))
        return self

    def unlock_data(self):
        for mob in self.get_family():
            mob.locked_data_keys = set()

    # Operations touching shader uniforms

    def affects_shader_info_id(func):
        @wraps(func)
        def wrapper(self):
            for mob in self.get_family():
                func(mob)
                mob.refresh_shader_wrapper_id()
            return self
        return wrapper

    @affects_shader_info_id
    def fix_in_frame(self):
        '''将物件锁定在屏幕上，常用于 3D 场景需要旋转镜头的情况'''
        self.uniforms["is_fixed_in_frame"] = 1.0
        self.is_fixed_in_frame = True
        return self

    @affects_shader_info_id
    def unfix_from_frame(self):
        '''将锁定在屏幕上的物件解锁'''
        self.uniforms["is_fixed_in_frame"] = 0.0
        self.is_fixed_in_frame = False
        return self

    @affects_shader_info_id
    def apply_depth_test(self):
        self.depth_test = True
        return self

    @affects_shader_info_id
    def deactivate_depth_test(self):
        self.depth_test = False
        return self

    # Shader code manipulation

    def replace_shader_code(self, old: str, new: str):
        # TODO, will this work with VMobject structure, given
        # that it does not simpler return shader_wrappers of
        # family?
        for wrapper in self.get_shader_wrapper_list():
            wrapper.replace_code(old, new)
        return self

    def set_color_by_code(self, glsl_code: str):
        """
        Takes a snippet of code and inserts it into a
        context which has the following variables:
        vec4 color, vec3 point, vec3 unit_normal.
        The code should change the color variable
        """
        """
        传入一段 ``glsl`` 代码，用这段代码来给物件上色

        代码中包含以下变量：

        - ``vec4 color``
        - ``vec3 point``
        - ``vec3 unit_normal``
        - ``vec3 light_coords``
        - ``float gloss``
        - ``float shadow``

        如果想要学习如何用 glsl 上色，推荐去 `<https://thebookofshaders/>`_ 和 `<https://shadertoy.com/>`_ 学习一番`
        """
        self.replace_shader_code(
            "///// INSERT COLOR FUNCTION HERE /////",
            glsl_code
        )
        return self

    def set_color_by_xyz_func(
        self,
        glsl_snippet: str,
        min_value: float = -5.0,
        max_value: float = 5.0,
        colormap: str = "viridis"
    ):
        """
        Pass in a glsl expression in terms of x, y and z which returns
        a float.
        """
        """
        传入一个关于 ``x, y, z`` 的字符串表达式，这个表达式应当返回一个 float 值

        这个方法不是非常智能，因为会把所有匹配到的 ``x, y, z`` 都认为是变量，
        所以如果有特殊必要的话请查看该方法的源码，进行一些更改，取消字符串的匹配和替换
        """
        # TODO, add a version of this which changes the point data instead
        # of the shader code
        for char in "xyz":
            glsl_snippet = glsl_snippet.replace(char, "point." + char)
        rgb_list = get_colormap_list(colormap)
        self.set_color_by_code(
            "color.rgb = float_to_color({}, {}, {}, {});".format(
                glsl_snippet,
                float(min_value),
                float(max_value),
                get_colormap_code(rgb_list)
            )
        )
        return self

    # For shader data

    def init_shader_data(self):
        # TODO, only call this when needed?
        self.shader_data = np.zeros(len(self.get_points()), dtype=self.shader_dtype)
        self.shader_indices = None
        self.shader_wrapper = ShaderWrapper(
            vert_data=self.shader_data,
            shader_folder=self.shader_folder,
            texture_paths=self.texture_paths,
            depth_test=self.depth_test,
            render_primitive=self.render_primitive,
        )

    def refresh_shader_wrapper_id(self):
        self.shader_wrapper.refresh_id()
        return self

    def get_shader_wrapper(self):
        '''获取 shader 包装'''
        self.shader_wrapper.vert_data = self.get_shader_data()
        self.shader_wrapper.vert_indices = self.get_shader_vert_indices()
        self.shader_wrapper.uniforms = self.get_shader_uniforms()
        self.shader_wrapper.depth_test = self.depth_test
        return self.shader_wrapper

    def get_shader_wrapper_list(self) -> list[ShaderWrapper]:
        '''获取 shader 包装列表'''
        shader_wrappers = it.chain(
            [self.get_shader_wrapper()],
            *[sm.get_shader_wrapper_list() for sm in self.submobjects]
        )
        batches = batch_by_property(shader_wrappers, lambda sw: sw.get_id())

        result = []
        for wrapper_group, sid in batches:
            shader_wrapper = wrapper_group[0]
            if not shader_wrapper.is_valid():
                continue
            shader_wrapper.combine_with(*wrapper_group[1:])
            if len(shader_wrapper.vert_data) > 0:
                result.append(shader_wrapper)
        return result

    def check_data_alignment(self, array: Iterable, data_key: str):
        # Makes sure that self.data[key] can be broadcast into
        # the given array, meaning its length has to be either 1
        # or the length of the array
        d_len = len(self.data[data_key])
        if d_len != 1 and d_len != len(array):
            self.data[data_key] = resize_with_interpolation(
                self.data[data_key], len(array)
            )
        return self

    def get_resized_shader_data_array(self, length: int) -> np.ndarray:
        # If possible, try to populate an existing array, rather
        # than recreating it each frame
        if len(self.shader_data) != length:
            self.shader_data = resize_array(self.shader_data, length)
        return self.shader_data

    def read_data_to_shader(
        self,
        shader_data: np.ndarray,
        shader_data_key: str,
        data_key: str
    ):
        if data_key in self.locked_data_keys:
            return
        self.check_data_alignment(shader_data, data_key)
        shader_data[shader_data_key] = self.data[data_key]

    def get_shader_data(self):
        '''获取 shader 数据'''
        shader_data = self.get_resized_shader_data_array(self.get_num_points())
        self.read_data_to_shader(shader_data, "point", "points")
        return shader_data

    def refresh_shader_data(self):
        self.get_shader_data()

    def get_shader_uniforms(self):
        return self.uniforms

    def get_shader_vert_indices(self):
        return self.shader_indices

    # Event Handlers
    """
        Event handling follows the Event Bubbling model of DOM in javascript.
        Return false to stop the event bubbling.
        To learn more visit https://www.quirksmode.org/js/events_order.html

        Event Callback Argument is a callable function taking two arguments:
            1. Mobject
            2. EventData
    """

    def init_event_listners(self):
        self.event_listners: list[EventListner] = []

    def add_event_listner(
        self,
        event_type: EventType,
        event_callback: Callable[[Mobject, dict[str]]]
    ):
        event_listner = EventListner(self, event_type, event_callback)
        self.event_listners.append(event_listner)
        EVENT_DISPATCHER.add_listner(event_listner)
        return self

    def remove_event_listner(
        self,
        event_type: EventType,
        event_callback: Callable[[Mobject, dict[str]]]
    ):
        event_listner = EventListner(self, event_type, event_callback)
        while event_listner in self.event_listners:
            self.event_listners.remove(event_listner)
        EVENT_DISPATCHER.remove_listner(event_listner)
        return self

    def clear_event_listners(self, recurse: bool = True):
        self.event_listners = []
        if recurse:
            for submob in self.submobjects:
                submob.clear_event_listners(recurse=recurse)
        return self

    def get_event_listners(self):
        return self.event_listners

    def get_family_event_listners(self):
        return list(it.chain(*[sm.get_event_listners() for sm in self.get_family()]))

    def get_has_event_listner(self):
        return any(
            mob.get_event_listners()
            for mob in self.get_family()
        )

    def add_mouse_motion_listner(self, callback):
        self.add_event_listner(EventType.MouseMotionEvent, callback)

    def remove_mouse_motion_listner(self, callback):
        self.remove_event_listner(EventType.MouseMotionEvent, callback)

    def add_mouse_press_listner(self, callback):
        self.add_event_listner(EventType.MousePressEvent, callback)

    def remove_mouse_press_listner(self, callback):
        self.remove_event_listner(EventType.MousePressEvent, callback)

    def add_mouse_release_listner(self, callback):
        self.add_event_listner(EventType.MouseReleaseEvent, callback)

    def remove_mouse_release_listner(self, callback):
        self.remove_event_listner(EventType.MouseReleaseEvent, callback)

    def add_mouse_drag_listner(self, callback):
        self.add_event_listner(EventType.MouseDragEvent, callback)

    def remove_mouse_drag_listner(self, callback):
        self.remove_event_listner(EventType.MouseDragEvent, callback)

    def add_mouse_scroll_listner(self, callback):
        self.add_event_listner(EventType.MouseScrollEvent, callback)

    def remove_mouse_scroll_listner(self, callback):
        self.remove_event_listner(EventType.MouseScrollEvent, callback)

    def add_key_press_listner(self, callback):
        self.add_event_listner(EventType.KeyPressEvent, callback)

    def remove_key_press_listner(self, callback):
        self.remove_event_listner(EventType.KeyPressEvent, callback)

    def add_key_release_listner(self, callback):
        self.add_event_listner(EventType.KeyReleaseEvent, callback)

    def remove_key_release_listner(self, callback):
        self.remove_event_listner(EventType.KeyReleaseEvent, callback)

    # Errors

    def throw_error_if_no_points(self):
        if not self.has_points():
            message = "Cannot call Mobject.{} " +\
                      "for a Mobject with no points"
            caller_name = sys._getframe(1).f_code.co_name
            raise Exception(message.format(caller_name))


class Group(Mobject):
    '''数学物件组合'''
    """
    可以组合Mobject对象
    和VGroup相对
    """
    def __init__(self, *mobjects: Mobject, **kwargs):
        '''传入一系列 ``mobjects`` 作为子物件，可以用 ``[]`` 索引'''
        if not all([isinstance(m, Mobject) for m in mobjects]):
            raise Exception("All submobjects must be of type Mobject")
        Mobject.__init__(self, **kwargs)
        self.add(*mobjects)

    def __add__(self, other: Mobject | Group):
        assert(isinstance(other, Mobject))
        return self.add(other)


class Point(Mobject):
    '''点'''
    """
    这个类怎么使用呢?
    如何使用着色器渲染呢?
    还是仅仅用作继承?
    """
    CONFIG = {
        "artificial_width": 1e-6,
        "artificial_height": 1e-6,
    }

    def __init__(self, location: npt.ArrayLike = ORIGIN, **kwargs):
        '''似乎仅用于表示坐标'''
        Mobject.__init__(self, **kwargs)
        self.set_location(location)

    def get_width(self) -> float:
        return self.artificial_width

    def get_height(self) -> float:
        return self.artificial_height

    def get_location(self) -> np.ndarray:
        '''获取坐标位置'''
        return self.get_points()[0].copy()

    def get_bounding_box_point(self, *args, **kwargs) -> np.ndarray:
        return self.get_location()

    def set_location(self, new_loc: npt.ArrayLike):
        '''设置坐标位置'''
        self.set_points(np.array(new_loc, ndmin=2, dtype=float))


class _AnimationBuilder:
    '''动画编译器'''
    def __init__(self, mobject: Mobject):
        '''用于场景类 ``Scene`` 的 ``play`` 中，用法如下：

        .. code:: python

            self.play(mob.animate.shift(UP).scale(2).rotate(PI))

        该示例中，会使 mob 生成一个 **向上移动 2 个单位，放大至 2 倍，旋转 180 度** 的目标，并使用 
        ``MoveToTarget`` 进行转变

        这个方法可以采用 **链式操作**，即像样例中给的那样连续施加 3 个方法。这得益于 Mobject 的这些方法都返回自身，
        也就是 ``return self``，有兴趣的读者可以仔细研究一下源码
        '''
        self.mobject = mobject
        self.overridden_animation = None
        self.mobject.generate_target()
        self.is_chaining = False
        self.methods = []

    """
    In Python, __getattr__ is a special method that you can define in your custom 
    classes to control how attribute access is handled when an attribute is not 
    found through the usual means (i.e., when the attribute is not present as an 
    instance variable or a class variable). 

    @property
    def animate(self):
        return _AnimationBuilder(self)

    
    执行逻辑分析:
    1.当执行到mob.animate的时候, 会返回_AnimationBuilder(mob)对象
    2.当执行到mob.animate.shift(UP)的时候, 即_AnimationBuilder(mob).shift(UP)
    3.因为_AnimationBuilder类没有shift方法, 故会触发__getattr__(self, "shift")方法
    4.执行getattr(self.mobject.target, "shift"), self.methods.append(shift)
    5.
    6. 
    """
    def __getattr__(self, method_name: str):
        method = getattr(self.mobject.target, method_name)
        self.methods.append(method)
        has_overridden_animation = hasattr(method, "_override_animate")

        if (self.is_chaining and has_overridden_animation) or self.overridden_animation:
            raise NotImplementedError(
                "Method chaining is currently not supported for "
                "overridden animations"
            )

        def update_target(*method_args, **method_kwargs):
            if has_overridden_animation:
                self.overridden_animation = method._override_animate(
                    self.mobject, *method_args, **method_kwargs
                )
            else:
                method(*method_args, **method_kwargs)
            return self

        self.is_chaining = True
        # 这里为什么返回了一个函数?
        return update_target

    def build(self):
        '''
        在动画播放之前，:func:`~manimlib.animation.animation.prepare_animation` 
        会先自动调用 ``build()`` 方法，将方法编译为 **动画实例**

        将一系列在 ``.animate`` 之后的方法合并为一个 ``MoveToTarget``，并返回这个 
        ``MoveToTraget`` 的动画实例。也就是说，可以用下面的代码来播放动画，也可以将动画转变为更新

        .. code:: python

            # 直接用 play 方法播放
            self.play(mob.animate.shift(UP).scale(2).rotate(PI/2))
            
            # 播放动画
            anim = mob.animate.shift(UP).scale(2).rotate(PI/2).build() # 此处有无 .build() 均可. why?
            self.play(anim)
    
            # 将动画实例用一个变量保存，并将动画转变为更新
            anim = mob.animate.shift(UP).scale(2).rotate(PI/2).build()
            turn_animation_into_updater(anim)
            self.add(mob)
            self.wait(2)
        '''
        from manimlib.animation.transform import _MethodAnimation

        if self.overridden_animation:
            return self.overridden_animation

        return _MethodAnimation(self.mobject, self.methods)


def override_animate(method):
    def decorator(animation_method):
        method._override_animate = animation_method
        return animation_method

    return decorator
