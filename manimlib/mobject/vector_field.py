from __future__ import annotations

import itertools as it
import random
from typing import Sequence, TypeVar, Callable, Iterable

import numpy as np
import numpy.typing as npt

from manimlib.constants import *
from manimlib.animation.composition import AnimationGroup
from manimlib.animation.indication import VShowPassingFlash
from manimlib.mobject.geometry import Arrow
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.utils.bezier import inverse_interpolate
from manimlib.utils.bezier import interpolate
from manimlib.utils.color import get_colormap_list
from manimlib.utils.config_ops import merge_dicts_recursively
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import linear
from manimlib.utils.simple_functions import sigmoid
from manimlib.utils.space_ops import get_norm

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.mobject.mobject import Mobject
    from manimlib.mobject.coordinate_systems import CoordinateSystem
    T = TypeVar("T")


def get_vectorized_rgb_gradient_function(
    min_value: T,
    max_value: T,
    color_map: str
) -> Callable[[npt.ArrayLike], np.ndarray]:
    rgbs = np.array(get_colormap_list(color_map))
    #print(color_map, rgbs)
    """
    3b1b_colormap 

    [[0.10980392 0.45882353 0.54117647]
     [0.26127451 0.57058824 0.48970588]
     [0.4127451  0.68235294 0.43823529]
     [0.5745098  0.7872549  0.35343137]
     [0.75686275 0.87843137 0.20196078]
     [0.93921569 0.96960784 0.0504902 ]
     [0.99705882 0.84607843 0.08333333]
     [0.99264706 0.61519608 0.20833333]
     [0.98823529 0.38431373 0.33333333]]
    """

    def func(values):
        """
        完成模长到颜色的映射

        颜色数组:
        [c1, c2, c3, c4, c5, c6]
        模长范围:
        [min, max]

        假设:
        min --> c1, max --> c2
        当min < value < max时
        value --> ?
        """
        #print(min_value, max_value, values)
        """VectorField (如果是StreamLines输出会不一样)

        0 3 [3.7785946829182113]
        """
        # 模长在min_value和max_value之间的比例
        alphas = inverse_interpolate(
            min_value, max_value, np.array(values)
        )
        alphas = np.clip(alphas, 0, 1)
        # 映射到颜色数组的索引: indices和next_indices
        # 颜色数组的两个索引对应颜色继续插值: inter_alphas 
        scaled_alphas = alphas * (len(rgbs) - 1)
        indices = scaled_alphas.astype(int)
        next_indices = np.clip(indices + 1, 0, len(rgbs) - 1)
        inter_alphas = scaled_alphas % 1
        inter_alphas = inter_alphas.repeat(3).reshape((len(indices), 3))
        result = interpolate(rgbs[indices], rgbs[next_indices], inter_alphas)
        #print(result)
        """
        [[0.98823529 0.38431373 0.33333333]]
        """
        return result
    return func


def get_rgb_gradient_function(
    min_value: T,
    max_value: T,
    color_map: str
) -> Callable[[T], np.ndarray]:
    vectorized_func = get_vectorized_rgb_gradient_function(min_value, max_value, color_map)
    # 这里会取第一个元素
    # 函数的返回值是二维数组
    return lambda value: vectorized_func([value])[0]


def move_along_vector_field(
    mobject: Mobject,
    func: Callable[[np.ndarray], np.ndarray]
) -> Mobject:
    mobject.add_updater(
        lambda m, dt: m.shift(
            func(m.get_center()) * dt
        )
    )
    return mobject


def move_submobjects_along_vector_field(
    mobject: Mobject,
    func: Callable[[np.ndarray], np.ndarray]
) -> Mobject:
    def apply_nudge(mob, dt):
        for submob in mob:
            x, y = submob.get_center()[:2]
            if abs(x) < FRAME_WIDTH and abs(y) < FRAME_HEIGHT:
                submob.shift(func(submob.get_center()) * dt)

    mobject.add_updater(apply_nudge)
    return mobject


def move_points_along_vector_field(
    mobject: Mobject,
    func: Callable[[float, float], Iterable[float]],
    coordinate_system: CoordinateSystem
) -> Mobject:
    cs = coordinate_system
    origin = cs.get_origin()

    def apply_nudge(self, dt):
        mobject.apply_function(
            lambda p: p + (cs.c2p(*func(*cs.p2c(p))) - origin) * dt
        )
    mobject.add_updater(apply_nudge)
    return mobject


def get_sample_points_from_coordinate_system(
    coordinate_system: CoordinateSystem,
    step_multiple: float
) -> it.product[tuple[np.ndarray, ...]]:
    """
    在坐标系上采点
    """
    ranges = []
    for range_args in coordinate_system.get_all_ranges():
        _min, _max, step = range_args
        step *= step_multiple
        ranges.append(np.arange(_min, _max + step, step))
    return it.product(*ranges)


"""
def pendulum_vector_field_func(theta, omega, mu=0.3, g=9.8, L=3):
    return [omega, -np.sqrt(g / L) * np.sin(theta) - mu * omega]

class test(Scene):
	
	def construct(self): 
		
		plane = NumberPlane()
		
		vector_field = VectorField(
			pendulum_vector_field_func,
			plane,
			step_multiple=0.5,
            magnitude_range=(0, 5),
            length_func=lambda norm: 0.35 * sigmoid(norm)
		)
		vector_field.scale(0.5)
		self.play(FadeIn(vector_field))
		self.play(FadeOut(vector_field))

		
		stream_lines = StreamLines(
			pendulum_vector_field_func,
			plane
		)
		stream_lines.scale(0.5)
		self.play(FadeIn(stream_lines))
		self.play(FadeOut(stream_lines))
		
		asl = AnimatedStreamLines(stream_lines)
		self.add(asl)
		self.wait(3)
"""
"""
Callable[[float, float], Sequence[float]] 
means a callable that takes two float arguments and returns a sequence of floats.

Here is an example of a function that matches this type annotation:

```
def average_two_numbers(x: float, y: float) -> Sequence[float]:
    return [x, y, (x + y) / 2]
```
"""
# Mobjects

"""
VectorField和StreamLines
是表达场的两种方式
"""
class VectorField(VGroup):
    """
    The values of this functions is displayed as a grid of vectors.
    By default the color of each vector is determined by it's magnitude.

    func
        The function defining the rate of change at every position of the vector field.
    
    length_func
        The function determining the displayed size of the vectors. The actual size
        of the vector is passed, the returned value will be used as display size for the
        vector. By default this is used to cap the displayed size of vectors to reduce the clutter.
    """
    CONFIG = {
        "step_multiple": 0.5, # 采样点间隔
        "magnitude_range": (0, 2), # 和颜色有关
        "color_map": "3b1b_colormap",
        # Takes in actual norm, spits out displayed norm
        "length_func": lambda norm: 0.45 * sigmoid(norm), # 向量长度归一化。这里用sigmoid真是独具匠心。不得不佩服3b1b对公式的天赋。
        "opacity": 1.0,
        "vector_config": {},
    }

    def __init__(
        self,
        func: Callable[[float, float], Sequence[float]],
        coordinate_system: CoordinateSystem,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.func = func
        self.coordinate_system = coordinate_system
        self.value_to_rgb = get_rgb_gradient_function(
            *self.magnitude_range, self.color_map,
        )

        samples = get_sample_points_from_coordinate_system(
            coordinate_system, self.step_multiple
        )
        self.add(*(
            self.get_vector(coords)
            for coords in samples
        ))

    def get_vector(self, coords: Iterable[float], **kwargs) -> Arrow:
        """Creates a vector in the vector field.

        The created vector is based on the function of the vector field and is
        rooted in the given point. Color and length fit the specifications of
        this vector field.
        """
        vector_config = merge_dicts_recursively(
            self.vector_config,
            kwargs
        )

        """
        self.func是场的函数
        输入空间坐标, 输出场向量

        认知: 任何一个场都有一个函数
        """
        output = np.array(self.func(*coords))
        """
        output是self.func作用后的坐标, 将其当做向量的话, 有方向有模长
        如果按照原本的模长显示, 长短差距难免过大
        所以, 通过合适的数学手段将模长缩放到一个合理的区间
        这里采取的函数是sigmoid(深度学习常用的公式)
        
        模长缩放后, 起模长信息被丢失了
        可以根据模长为向量设置颜色
        这样, 根据颜色, 可以大致明白其模长

        总结:
        场在每一点处的方向不变
        模长被归一化
        模长信息被颜色代替
        """
        # norm被用来设置颜色
        norm = get_norm(output)
        if norm > 0:
            # norm归一化
            output *= self.length_func(norm) / norm

        # 坐标系空间的原点在世界坐标系中的位置
        origin = self.coordinate_system.get_origin()
        """
        如何理解c2p?两个空间的映射
        坐标系空间 ---> 世界空间
        coords: 采样点(坐标系空间)
        _input: 采样点(世界空间)
        output: 向量(坐标系空间)
        _output: 向量(世界空间)

        注意: 向量没有起始点
        为了可视化向量, 需要人为的为向量添加起始点
        """
        _input = self.coordinate_system.c2p(*coords)
        _output = self.coordinate_system.c2p(*output)

        # origin和_output都已经在世界坐标系中
        vect = Arrow(
            origin, _output, buff=0,
            **vector_config
        )
        # 移动到采样点(世界坐标系)
        vect.shift(_input - origin)
        # 模长被归一化后, 长度信息就丢失了。但可以通过颜色显示模长信息
        vect.set_rgba_array([[*self.value_to_rgb(norm), self.opacity]])
        return vect


class StreamLines(VGroup):
    CONFIG = {
        "step_multiple": 0.5,
        "n_repeats": 1,
        "noise_factor": None,
        # Config for drawing lines
        "dt": 0.05,
        "arc_len": 3,
        "max_time_steps": 200,
        "n_samples_per_line": 10,
        "cutoff_norm": 15,
        # Style info
        "stroke_width": 1,
        "stroke_color": WHITE,
        "stroke_opacity": 1,
        "color_by_magnitude": True,
        "magnitude_range": (0, 2.0),
        "taper_stroke_width": False,
        "color_map": "3b1b_colormap",
    }

    def __init__(
        self,
        func: Callable[[float, float], Sequence[float]],
        coordinate_system: CoordinateSystem,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.func = func
        self.coordinate_system = coordinate_system
        # 画场线
        self.draw_lines()
        # 上颜色
        self.init_style()

    def point_func(self, point: np.ndarray) -> np.ndarray:
        """
        输入: 世界空间 点
        输出: 世界空间 点处的向量

        self.func是作用在坐标系空间
        所以需要完成这种转换
        """
        in_coords = self.coordinate_system.p2c(point)
        out_coords = self.func(*in_coords)
        return self.coordinate_system.c2p(*out_coords)

    def draw_lines(self) -> None:
        lines = []
        origin = self.coordinate_system.get_origin()
        #print(origin)
        for point in self.get_start_points():
            points = [point]
            total_arc_len = 0
            # 画每一条线消耗的virtual time
            # 这个属性有什么用么
            time = 0
            for x in range(self.max_time_steps):
                """
                这里设置了最大的迭代步数
                每一步执行消耗virtual time: dt
                """
                time += self.dt
                last_point = points[-1]
                # 计算每一个点的场向量, 得到最新的点
                """
                任何数学公式要想明白其物理意义
                self.point_func(last_point)的几何意义:
                场线在last_point处的切线
                
                个人觉得, 这里并不需要减去origin
                self.point_func(last_point)本身就是向量
                再减去origin, 几何意义反而不够明确 

                new_point = last_point + self.dt * self.point_func(last_point)
                这一步是整个StreamLines的点睛之笔 
                """
                new_point = last_point + self.dt * (self.point_func(last_point) - origin)
                points.append(new_point)
                # 场线长度
                total_arc_len += get_norm(new_point - last_point)
                # 对场线进行截断, 两种情况(逻辑上不统一)
                # 第一种情况, 为何不是对new_point进行判断?
                if get_norm(last_point) > self.cutoff_norm:
                    break
                # 第二种情况, 引入了new_point之后的总弧长
                if total_arc_len > self.arc_len:
                    break
            line = VMobject()
            line.virtual_time = time
            # 每一条线的点集数目可能有不同
            # 隔step采样, 保证每一条线点集数目相同
            step = max(1, int(len(points) / self.n_samples_per_line))
            line.set_points_as_corners(points[::step])
            # 折线变光滑
            line.make_approximately_smooth()
            lines.append(line)
        self.set_submobjects(lines)

    def get_start_points(self) -> np.ndarray:
        cs = self.coordinate_system
        sample_coords = get_sample_points_from_coordinate_system(
            cs, self.step_multiple,
        )

        """
        设置噪声的目的是?
        如果不添加噪声, 每个采样点分布的特别均匀
        对于StreamLines, 每个采样点需要有一点随机性
        """
        noise_factor = self.noise_factor
        if noise_factor is None:
            noise_factor = cs.x_range[2] * self.step_multiple * 0.5

        return np.array([
            cs.c2p(*coords) + noise_factor * np.random.random(3)
            for n in range(self.n_repeats)
            for coords in sample_coords
        ])

    def init_style(self) -> None:
        if self.color_by_magnitude:
            values_to_rgbs = get_vectorized_rgb_gradient_function(
                *self.magnitude_range, self.color_map,
            )
            cs = self.coordinate_system
            for line in self.submobjects:
                norms = [
                    get_norm(self.func(*cs.p2c(point)))
                    for point in line.get_points()
                ]
                rgbs = values_to_rgbs(norms)
                rgbas = np.zeros((len(rgbs), 4))
                rgbas[:, :3] = rgbs
                rgbas[:, 3] = self.stroke_opacity
                #print(rgbas)
                # rgba是二维数组, 为同一条line设置渐变色
                line.set_rgba_array(rgbas, "stroke_rgba")
        else:
            self.set_stroke(self.stroke_color, opacity=self.stroke_opacity)
        """
        可以对比下下面两种写法:
        line.set_rgba_array(rgbas, "stroke_rgba")
        self.set_stroke(self.stroke_color, opacity=self.stroke_opacity) 
        """

        if self.taper_stroke_width:
            # width还能设置为数组
            width = [0, self.stroke_width, 0]
        else:
            width = self.stroke_width
        self.set_stroke(width=width)


class AnimatedStreamLines(VGroup):
    """
    想象力！

    余华: 没有洞见的想象力一文不值
    """
    CONFIG = {
        "lag_range": 4,
        "line_anim_class": VShowPassingFlash,
        "line_anim_config": {
            # "run_time": 4,
            "rate_func": linear,
            "time_width": 0.5,
        },
    }

    def __init__(self, stream_lines: StreamLines, **kwargs):
        super().__init__(**kwargs)
        self.stream_lines = stream_lines
        for line in stream_lines:
            line.anim: VShowPassingFlash = self.line_anim_class(
                line,
                run_time=line.virtual_time,
                **self.line_anim_config,
            )
            # 这一行有什么用
            line.anim.begin()
            line.time = -self.lag_range * random.random()
            self.add(line.anim.mobject)

        self.add_updater(lambda m, dt: m.update(dt))

    def update(self, dt: float) -> None:
        stream_lines = self.stream_lines
        for line in stream_lines:
            line.time += dt
            adjusted_time = max(line.time, 0) % line.anim.run_time
            line.anim.update(adjusted_time / line.anim.run_time)


# TODO: This class should be deleted
class ShowPassingFlashWithThinningStrokeWidth(AnimationGroup):
    CONFIG = {
        "n_segments": 10,
        "time_width": 0.1,
        "remover": True
    }

    def __init__(self, vmobject: VMobject, **kwargs):
        digest_config(self, kwargs)
        max_stroke_width = vmobject.get_stroke_width()
        max_time_width = kwargs.pop("time_width", self.time_width)
        AnimationGroup.__init__(self, *[
            VShowPassingFlash(
                vmobject.deepcopy().set_stroke(width=stroke_width),
                time_width=time_width,
                **kwargs
            )
            for stroke_width, time_width in zip(
                np.linspace(0, max_stroke_width, self.n_segments),
                np.linspace(max_time_width, 0, self.n_segments)
            )
        ])
