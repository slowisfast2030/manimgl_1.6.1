from __future__ import annotations

import operator as op
import itertools as it
from functools import reduce, wraps
from typing import Iterable, Sequence, Callable, Union

import colour
import moderngl
import numpy.typing as npt

from manimlib.constants import *
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.mobject import Point
from manimlib.utils.bezier import bezier
from manimlib.utils.bezier import get_smooth_quadratic_bezier_handle_points
from manimlib.utils.bezier import get_smooth_cubic_bezier_handle_points
from manimlib.utils.bezier import get_quadratic_approximation_of_cubic
from manimlib.utils.bezier import interpolate
from manimlib.utils.bezier import inverse_interpolate
from manimlib.utils.bezier import integer_interpolate
from manimlib.utils.bezier import partial_quadratic_bezier_points
from manimlib.utils.color import rgb_to_hex
from manimlib.utils.iterables import make_even
from manimlib.utils.iterables import resize_array
from manimlib.utils.iterables import resize_with_interpolation
from manimlib.utils.iterables import listify
from manimlib.utils.space_ops import angle_between_vectors
from manimlib.utils.space_ops import cross2d
from manimlib.utils.space_ops import earclip_triangulation
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import get_unit_normal
from manimlib.utils.space_ops import z_to_vector
from manimlib.shader_wrapper import ShaderWrapper


ManimColor = Union[str, colour.Color, Sequence[float]]


class VMobject(Mobject):
    CONFIG = {
        "fill_color": None,
        "fill_opacity": 0.0,
        "stroke_color": None,
        "stroke_opacity": 1.0,
        "stroke_width": DEFAULT_STROKE_WIDTH,
        "draw_stroke_behind_fill": False,
        # Indicates that it will not be displayed, but
        # that it should count in parent mobject's path
        "pre_function_handle_to_anchor_scale_factor": 0.01,
        "make_smooth_after_applying_functions": False,
        "background_image_file": None,
        # This is within a pixel
        # TODO, do we care about accounting for
        # varying zoom levels?
        "tolerance_for_point_equality": 1e-8,
        "n_points_per_curve": 3,
        "long_lines": False,
        # For shaders
        "stroke_shader_folder": "quadratic_bezier_stroke", # 原来在这里
        "fill_shader_folder": "quadratic_bezier_fill",     # 原来在这里
        # Could also be "bevel", "miter", "round"
        "joint_type": "auto",
        "flat_stroke": False,
        "render_primitive": moderngl.TRIANGLES,
        "fill_dtype": [
            ('point', np.float32, (3,)),
            ('unit_normal', np.float32, (3,)),
            ('color', np.float32, (4,)),
            ('vert_index', np.float32, (1,)),
        ],
        "stroke_dtype": [
            ("point", np.float32, (3,)),
            ("prev_point", np.float32, (3,)),
            ("next_point", np.float32, (3,)),
            ('unit_normal', np.float32, (3,)),
            ("stroke_width", np.float32, (1,)),
            ("color", np.float32, (4,)),
        ]
    }

    def __init__(self, **kwargs):
        """
        三角剖分
        Triangulation in computer graphics is the process of dividing a complex polygonal area 
        into simpler triangles, which can be rendered more efficiently by the graphics card.

        Graphics hardware and software commonly use triangles as the basic rendering primitive. 
        Triangles are straightforward to rasterize (convert to pixels) because they are always 
        planar and convex. By breaking down complex shapes into triangles, rendering engines can 
        efficiently display 3D models and scenes on 2D screens.

        mobject类并不需要实现三角剖分, 比如Surface类
        三角剖分的主要目的是在既有顶点下, 将顶点组合成一个个三角形, 作为基元, 方便着色器渲染
        对于Surface类, 因为是对nv空间的采样, 直接设置了triangle index(可以算作另类的三角剖分)
        """
        self.needs_new_triangulation = True
        self.triangulation = np.zeros(0, dtype='i4')
        super().__init__(**kwargs)

    def get_group_class(self):
        return VGroup

    """
    'fill_rgba': array([[0.98823529, 0.38431373, 0.33333333, 0.        ]])
    'stroke_rgba': array([[0.98823529, 0.38431373, 0.33333333, 1.        ]])
    """
    def init_data(self):
        super().init_data()
        self.data.pop("rgbas")
        self.data.update({
            "fill_rgba": np.zeros((1, 4)),
            "stroke_rgba": np.zeros((1, 4)),
            "stroke_width": np.zeros((1, 1)),
            "unit_normal": np.zeros((1, 3))
        })

    # Colors
    def init_colors(self):
        self.set_fill(
            color=self.fill_color or self.color,
            opacity=self.fill_opacity,
        )
        self.set_stroke(
            color=self.stroke_color or self.color,
            width=self.stroke_width,
            opacity=self.stroke_opacity,
            background=self.draw_stroke_behind_fill,
        )
        self.set_gloss(self.gloss)
        self.set_flat_stroke(self.flat_stroke)
        return self

    def set_rgba_array(
        self,
        rgba_array: npt.ArrayLike,
        name: str = None,
        recurse: bool = False
    ):
        if name is None:
            names = ["fill_rgba", "stroke_rgba"]
        else:
            names = [name]

        for name in names:
            super().set_rgba_array(rgba_array, name, recurse)
        return self

    def set_fill(
        self,
        color: ManimColor | None = None,
        opacity: float | None = None,
        recurse: bool = True
    ):
        self.set_rgba_array_by_color(color, opacity, 'fill_rgba', recurse)
        return self

    def set_stroke(
        self,
        color: ManimColor | None = None,
        width: float | npt.ArrayLike | None = None,
        opacity: float | None = None,
        background: bool | None = None,
        recurse: bool = True
    ):
        '''设置轮廓线（轮廓线浮于填充色上方）'''
        self.set_rgba_array_by_color(color, opacity, 'stroke_rgba', recurse)

        if width is not None:
            for mob in self.get_family(recurse):
                if isinstance(width, np.ndarray):
                    arr = width.reshape((len(width), 1))
                else:
                    arr = np.array([[w] for w in listify(width)], dtype=float)
                mob.data['stroke_width'] = arr

        if background is not None:
            for mob in self.get_family(recurse):
                mob.draw_stroke_behind_fill = background
        return self

    def set_backstroke(
        self,
        color: ManimColor = BLACK,
        width: float | npt.ArrayLike = 3,
        background: bool = True
    ):
        """设置背景轮廓线（轮廓线衬于填充色下方）"""
        self.set_stroke(color, width, background=background)
        return self

    def align_stroke_width_data_to_points(self, recurse: bool = True) -> None:
        for mob in self.get_family(recurse):
            mob.data["stroke_width"] = resize_with_interpolation(
                mob.data["stroke_width"], len(mob.get_points())
            )

    def set_style(
        self,
        fill_color: ManimColor | None = None,
        fill_opacity: float | None = None,
        fill_rgba: npt.ArrayLike | None = None,
        stroke_color: ManimColor | None = None,
        stroke_opacity: float | None = None,
        stroke_rgba: npt.ArrayLike | None = None,
        stroke_width: float | npt.ArrayLike | None = None,
        stroke_background: bool = True,
        reflectiveness: float | None = None,
        gloss: float | None = None,
        shadow: float | None = None,
        recurse: bool = True
    ):
        '''整体设置样式'''
        if fill_rgba is not None:
            self.data['fill_rgba'] = resize_with_interpolation(fill_rgba, len(fill_rgba))
        else:
            self.set_fill(
                color=fill_color,
                opacity=fill_opacity,
                recurse=recurse
            )

        if stroke_rgba is not None:
            self.data['stroke_rgba'] = resize_with_interpolation(stroke_rgba, len(fill_rgba))
            self.set_stroke(
                width=stroke_width,
                background=stroke_background,
            )
        else:
            self.set_stroke(
                color=stroke_color,
                width=stroke_width,
                opacity=stroke_opacity,
                recurse=recurse,
                background=stroke_background,
            )

        if reflectiveness is not None:
            self.set_reflectiveness(reflectiveness, recurse=recurse)
        if gloss is not None:
            self.set_gloss(gloss, recurse=recurse)
        if shadow is not None:
            self.set_shadow(shadow, recurse=recurse)
        return self

    def get_style(self):
        '''获取样式字典'''
        return {
            "fill_rgba": self.data['fill_rgba'].copy(),
            "stroke_rgba": self.data['stroke_rgba'].copy(),
            "stroke_width": self.data['stroke_width'].copy(),
            "stroke_background": self.draw_stroke_behind_fill,
            "reflectiveness": self.get_reflectiveness(),
            "gloss": self.get_gloss(),
            "shadow": self.get_shadow(),
        }

    def match_style(self, vmobject: VMobject, recurse: bool = True):
        '''将自身样式与传入的 ``vmobject`` 匹配'''
        self.set_style(**vmobject.get_style(), recurse=False)
        if recurse:
            # Does its best to match up submobject lists, and
            # match styles accordingly
            submobs1, submobs2 = self.submobjects, vmobject.submobjects
            if len(submobs1) == 0:
                return self
            elif len(submobs2) == 0:
                submobs2 = [vmobject]
            for sm1, sm2 in zip(*make_even(submobs1, submobs2)):
                sm1.match_style(sm2)
        return self

    def set_color(self, color: ManimColor, recurse: bool = True):
        self.set_fill(color, recurse=recurse)
        self.set_stroke(color, recurse=recurse)
        return self

    def set_opacity(self, opacity: float, recurse: bool = True):
        self.set_fill(opacity=opacity, recurse=recurse)
        self.set_stroke(opacity=opacity, recurse=recurse)
        return self

    def fade(self, darkness: float = 0.5, recurse: bool = True):
        mobs = self.get_family() if recurse else [self]
        for mob in mobs:
            factor = 1.0 - darkness
            mob.set_fill(
                opacity=factor * mob.get_fill_opacity(),
                recurse=False,
            )
            mob.set_stroke(
                opacity=factor * mob.get_stroke_opacity(),
                recurse=False,
            )
        return self

    def get_fill_colors(self) -> list[str]:
        return [
            rgb_to_hex(rgba[:3])
            for rgba in self.data['fill_rgba']
        ]

    def get_fill_opacities(self) -> np.ndarray:
        return self.data['fill_rgba'][:, 3]

    def get_stroke_colors(self) -> list[str]:
        return [
            rgb_to_hex(rgba[:3])
            for rgba in self.data['stroke_rgba']
        ]

    def get_stroke_opacities(self) -> np.ndarray:
        return self.data['stroke_rgba'][:, 3]

    def get_stroke_widths(self) -> np.ndarray:
        return self.data['stroke_width'][:, 0]

    # TODO, it's weird for these to return the first of various lists
    # rather than the full information
    def get_fill_color(self) -> str:
        """
        If there are multiple colors (for gradient)
        this returns the first one
        """
        return self.get_fill_colors()[0]

    def get_fill_opacity(self) -> float:
        """
        If there are multiple opacities, this returns the
        first
        """
        return self.get_fill_opacities()[0]

    def get_stroke_color(self) -> str:
        return self.get_stroke_colors()[0]

    def get_stroke_width(self) -> float | np.ndarray:
        return self.get_stroke_widths()[0]

    def get_stroke_opacity(self) -> float:
        return self.get_stroke_opacities()[0]

    def get_color(self) -> str:
        if self.has_fill():
            return self.get_fill_color()
        return self.get_stroke_color()

    def has_stroke(self) -> bool:
        return self.get_stroke_widths().any() and self.get_stroke_opacities().any()

    def has_fill(self) -> bool:
        return any(self.get_fill_opacities())

    def get_opacity(self) -> float:
        if self.has_fill():
            return self.get_fill_opacity()
        return self.get_stroke_opacity()

    def set_flat_stroke(self, flat_stroke: bool = True, recurse: bool = True):
        for mob in self.get_family(recurse):
            mob.flat_stroke = flat_stroke
        return self

    def get_flat_stroke(self) -> bool:
        return self.flat_stroke

    def set_joint_type(self, joint_type: str, recurse: bool = True):
        for mob in self.get_family(recurse):
            mob.joint_type = joint_type
        return self

    def get_joint_type(self) -> str:
        return self.joint_type

    # Points
    def set_anchors_and_handles(
        self,
        anchors1: np.ndarray,
        handles: np.ndarray,
        anchors2: np.ndarray
    ):
        '''设置二阶贝塞尔曲线的锚点和手柄'''
        assert(len(anchors1) == len(handles) == len(anchors2))
        # CONFIG字典中给出的是3，二阶贝塞尔曲线有两个anchor和一个handle
        nppc = self.n_points_per_curve
        new_points = np.zeros((nppc * len(anchors1), self.dim))
        arrays = [anchors1, handles, anchors2]
        for index, array in enumerate(arrays):
            # new_points中重复存储了部分anchor
            new_points[index::nppc] = array
        self.set_points(new_points)
        return self

    def start_new_path(self, point: np.ndarray):
        '''开启一个新的路径'''
        assert(self.get_num_points() % self.n_points_per_curve == 0)
        self.append_points([point])
        return self

    def add_cubic_bezier_curve(
        self,
        anchor1: npt.ArrayLike,
        handle1: npt.ArrayLike,
        handle2: npt.ArrayLike,
        anchor2: npt.ArrayLike
    ):
        """
        三阶贝塞尔曲线需要两个anchor和两个handle
        """
        # 这里做一个猜想，这里返回的new_points是6个点，即两条二阶贝塞尔曲线的锚点和手柄
        new_points = get_quadratic_approximation_of_cubic(anchor1, handle1, handle2, anchor2)
        self.append_points(new_points)

    def add_cubic_bezier_curve_to(
        self,
        handle1: npt.ArrayLike,
        handle2: npt.ArrayLike,
        anchor: npt.ArrayLike
    ):
        """
        Add cubic bezier curve to the path.
        """
        """
        添加一条三阶贝塞尔曲线（可能不准）
        """
        """
        这里将第一个anchor省略了
        默认为当前曲线的最后一个点
        """
        self.throw_error_if_no_points()
        quadratic_approx = get_quadratic_approximation_of_cubic(
            self.get_last_point(), handle1, handle2, anchor
        )
        if self.has_new_path_started():
            self.append_points(quadratic_approx[1:])
        else:
            self.append_points(quadratic_approx)

    def add_quadratic_bezier_curve_to(self, handle: np.ndarray, anchor: np.ndarray):
        '''添加一条二阶贝塞尔曲线'''
        self.throw_error_if_no_points()
        if self.has_new_path_started():
            self.append_points([handle, anchor])
        else:
            self.append_points([self.get_last_point(), handle, anchor])

    def add_line_to(self, point: np.ndarray):
        '''添加一条直线'''
        # 添加一条直线，本质上在于添加一些点
        end = self.get_points()[-1]
        # 在0和1之间等间隔插3个值，包含首尾
        alphas = np.linspace(0, 1, self.n_points_per_curve)
        if self.long_lines:
            halfway = interpolate(end, point, 0.5)
            points = [
                interpolate(end, halfway, a)
                for a in alphas
            ] + [
                interpolate(halfway, point, a)
                for a in alphas
            ]
        else:
            points = [
                interpolate(end, point, a)
                for a in alphas
            ]
        if self.has_new_path_started():
            points = points[1:]
        self.append_points(points)
        return self

    def add_smooth_curve_to(self, point: np.ndarray):
        '''添加一条平滑的曲线'''
        if self.has_new_path_started():
            self.add_line_to(point)
        else:
            self.throw_error_if_no_points()
            # 这里用二阶贝塞尔曲线来生成曲线
            # 需要首先计算出handle
            new_handle = self.get_reflection_of_last_handle()
            self.add_quadratic_bezier_curve_to(new_handle, point)
        return self

    def add_smooth_cubic_curve_to(self, handle: np.ndarray, point: np.ndarray):
        """
        这里用三阶贝塞尔曲线生成曲线
        三阶曲线需要两个handle
        这里只给出了一个
        需要计算出另一个
        """
        self.throw_error_if_no_points()
        if self.get_num_points() == 1:
            new_handle = self.get_points()[-1]
        else:
            new_handle = self.get_reflection_of_last_handle()
        self.add_cubic_bezier_curve_to(new_handle, handle, point)

    def has_new_path_started(self) -> bool:
        return self.get_num_points() % self.n_points_per_curve == 1

    def get_last_point(self) -> np.ndarray:
        '''获取路径最后一个锚点'''
        return self.get_points()[-1]

    def get_reflection_of_last_handle(self) -> np.ndarray:
        points = self.get_points()
        return 2 * points[-1] - points[-2]

    def close_path(self):
        '''用直线闭合该曲线'''
        if not self.is_closed():
            self.add_line_to(self.get_subpaths()[-1][0])

    def is_closed(self) -> bool:
        '''判断曲线是否闭合'''
        # 这里就凸显了工程的特点了
        # 第一个点和最后一个点的距离是否小于阈值
        # 并不需要完全重合
        return self.consider_points_equals(
            self.get_points()[0], self.get_points()[-1]
        )

    def subdivide_sharp_curves(
        self,
        angle_threshold: float = 30 * DEGREES,
        recurse: bool = True
    ):
        vmobs = [vm for vm in self.get_family(recurse) if vm.has_points()]
        for vmob in vmobs:
            new_points = []
            for tup in vmob.get_bezier_tuples():
                angle = angle_between_vectors(tup[1] - tup[0], tup[2] - tup[1])
                if angle > angle_threshold:
                    n = int(np.ceil(angle / angle_threshold))
                    alphas = np.linspace(0, 1, n + 1)
                    new_points.extend([
                        partial_quadratic_bezier_points(tup, a1, a2)
                        for a1, a2 in zip(alphas, alphas[1:])
                    ])
                else:
                    new_points.append(tup)
            vmob.set_points(np.vstack(new_points))
        return self

    def add_points_as_corners(self, points: Iterable[np.ndarray]):
        for point in points:
            self.add_line_to(point)
        return points

    def set_points_as_corners(self, points: Iterable[np.ndarray]):
        '''传入一个 Nx3 的数组，绘制顺序连接的折线'''
        nppc = self.n_points_per_curve
        points = np.array(points)
        self.set_anchors_and_handles(*[
            interpolate(points[:-1], points[1:], a)
            for a in np.linspace(0, 1, nppc)
        ])
        return self

    def set_points_smoothly(
        self,
        points: Iterable[np.ndarray],
        true_smooth: bool = False
    ):
        '''用平滑的曲线连接传入的系列点'''
        self.set_points_as_corners(points)
        if true_smooth:
            self.make_smooth()
        else:
            self.make_approximately_smooth()
        return self

    def change_anchor_mode(self, mode: str):
        '''改变曲线连接模式

         - ``jagged`` : 折线
         - ``approx_smooth`` : 大致平滑
         - ``true_smooth`` : 真正平滑
        '''
        assert(mode in ("jagged", "approx_smooth", "true_smooth"))
        nppc = self.n_points_per_curve
        for submob in self.family_members_with_points():
            subpaths = submob.get_subpaths()
            submob.clear_points()
            for subpath in subpaths:
                anchors = np.vstack([subpath[::nppc], subpath[-1:]])
                new_subpath = np.array(subpath)
                if mode == "approx_smooth":
                    new_subpath[1::nppc] = get_smooth_quadratic_bezier_handle_points(anchors)
                elif mode == "true_smooth":
                    h1, h2 = get_smooth_cubic_bezier_handle_points(anchors)
                    new_subpath = get_quadratic_approximation_of_cubic(anchors[:-1], h1, h2, anchors[1:])
                elif mode == "jagged":
                    new_subpath[1::nppc] = 0.5 * (anchors[:-1] + anchors[1:])
                submob.append_points(new_subpath)
            submob.refresh_triangulation()
        return self

    def make_smooth(self):
        """
        This will double the number of points in the mobject,
        so should not be called repeatedly.  It also means
        transforming between states before and after calling
        this might have strange artifacts
        """
        """
        使曲线变平滑

        这个方法会使得锚点数量加倍，所以 **不要重复使用**，否则锚点数量会 **指数爆炸**

        同时，应用 Transform 时有可能会出现奇怪的曲线
        """
        self.change_anchor_mode("true_smooth")
        return self

    def make_approximately_smooth(self):
        """
        Unlike make_smooth, this will not change the number of
        points, but it also does not result in a perfectly smooth
        curve.  It's most useful when the points have been
        sampled at a not-too-low rate from a continuous function,
        as in the case of ParametricCurve
        """
        """
        使曲线变得大致平滑

        这个方法不像 ``make_smooth``，本方法不会使锚点数量加倍，与此同时带来了无法达到完美平滑的问题

        但是这个方法在锚点采样间隔较小时会有比较好的效果，所以有时会更实用
        """
        self.change_anchor_mode("approx_smooth")
        return self

    def make_jagged(self):
        '''使曲线模式变为折线'''
        self.change_anchor_mode("jagged")
        return self

    def add_subpath(self, points: Iterable[np.ndarray]):
        # 这里传入的points就是二阶贝塞尔曲线的点了
        # 需要判断点数是否是3的倍数
        assert(len(points) % self.n_points_per_curve == 0)
        self.append_points(points)
        return self

    def append_vectorized_mobject(self, vectorized_mobject: VMobject):
        new_points = list(vectorized_mobject.get_points())

        if self.has_new_path_started():
            # Remove last point, which is starting
            # a new path
            self.resize_data(len(self.get_points() - 1))
        self.append_points(new_points)
        return self

    #
    def consider_points_equals(self, p0: np.ndarray, p1: np.ndarray) -> bool:
        '''判断两点是否大致重合'''
        return get_norm(p1 - p0) < self.tolerance_for_point_equality

    # Information about the curve
    def get_bezier_tuples_from_points(self, points: Sequence[np.ndarray]):
        # 二阶贝塞尔曲线，每一段由3个点组成
        # 给定的points数目可能不是3的倍数
        nppc = self.n_points_per_curve
        # 保证points的长度是nppc的整数倍
        remainder = len(points) % nppc
        points = points[:len(points) - remainder]
        return (
            points[i:i + nppc]
            for i in range(0, len(points), nppc)
        )

    def get_bezier_tuples(self):
        """
        三个一组, 返回贝塞尔控制点
        """
        return self.get_bezier_tuples_from_points(self.get_points())

    def get_subpaths_from_points(
        self,
        points: Sequence[np.ndarray]
    ) -> list[Sequence[np.ndarray]]:
        """
        两个vmob的布尔操作会用到
        """
        nppc = self.n_points_per_curve
        diffs = points[nppc - 1:-1:nppc] - points[nppc::nppc]
        splits = (diffs * diffs).sum(1) > self.tolerance_for_point_equality
        split_indices = np.arange(nppc, len(points), nppc, dtype=int)[splits]

        # split_indices = filter(
        #     lambda n: not self.consider_points_equals(points[n - 1], points[n]),
        #     range(nppc, len(points), nppc)
        # )
        split_indices = [0, *split_indices, len(points)]
        return [
            points[i1:i2]
            for i1, i2 in zip(split_indices, split_indices[1:])
            if (i2 - i1) >= nppc
        ]

    def get_subpaths(self) -> list[Sequence[np.ndarray]]:
        return self.get_subpaths_from_points(self.get_points())

    def get_nth_curve_points(self, n: int) -> np.ndarray:
        '''获取组成曲线的第 n 条贝塞尔曲线的控制点'''
        assert(n < self.get_num_curves())
        nppc = self.n_points_per_curve
        return self.get_points()[nppc * n:nppc * (n + 1)]

    def get_nth_curve_function(self, n: int) -> Callable[[float], np.ndarray]:
        '''获取组成曲线的第 n 条贝塞尔曲线函数'''
        return bezier(self.get_nth_curve_points(n))

    def get_num_curves(self) -> int:
        '''获取组成曲线的贝塞尔曲线数量'''
        return self.get_num_points() // self.n_points_per_curve

    def quick_point_from_proportion(self, alpha: float) -> np.ndarray:
        """
        在整条路径上占比为 alpha 处的点

        这个方法建立在假设每一段弧线长度相同的条件下，因此可能有一些误差，但是性能更好

        整体思想:
        整个vmob是由多段二阶贝塞尔曲线拼接而成
        需要通过alpha获取两个关键信息: 
        待求的点在第几段曲线
        在曲线的百分比位置
        """
        # Assumes all curves have the same length, so is inaccurate
        num_curves = self.get_num_curves()
        n, residue = integer_interpolate(0, num_curves, alpha)
        # 返回第n段贝塞尔曲线的公式
        curve_func = self.get_nth_curve_function(n)
        return curve_func(residue)

    def point_from_proportion(self, alpha: float) -> np.ndarray:
        """
        在整条路径上占比为 alpha 处的点

        不得不说, 这个函数的实现比mobject中的函数实现的要更加准确
        直接获取了第i段贝塞尔曲线的表达式, 然后计算出曲线上的点

        整体思想:
        整个vmob是由多段二阶贝塞尔曲线拼接而成
        需要通过alpha获取两个关键信息: 
        待求的点在第几段曲线
        在曲线的百分比位置
        """
        if alpha <= 0:
            return self.get_start()
        elif alpha >= 1:
            return self.get_end()

        partials = [0]
        # 遍历每一小段贝塞尔曲线
        for tup in self.get_bezier_tuples():
            # Approximate length with straight line from start to end
            """
            这里是点睛之笔
            每一段贝塞尔曲线的长度是没有公式可以计算的
            这里采取的是近似法
            这也给与我们很大启发:
            在图形学中, 如果不能拿到准确的数学公式, 可以用近似方法解决
            理论 vs 工程
            这是一个优秀的工程师的素养
            """
            arclen = get_norm(tup[0] - tup[-1])
            partials.append(partials[-1] + arclen)
        full = partials[-1]
        if full == 0:
            return self.get_start()
        # First index where the partial lenth is more alpha times the full length
        """
        next(iterator, default)

        其中, iterator是要传入的迭代器, default是可选的第二个参数, 它表示当迭代器耗尽时返回的默认值。
        如果不指定default, 那么当迭代器耗尽时, next函数会抛出一个StopIteration异常, 表示迭代结束。
        """
        i = next(
            (i for i, x in enumerate(partials) if x >= full * alpha),
            len(partials)  # Default
        )
        """
        partials[i - 1] / full < alpha < partials[i] / full
        计算出 alpha 在第 i - 1 条贝塞尔曲线上的占比
        """
        residue = inverse_interpolate(partials[i - 1] / full, partials[i] / full, alpha)
        return self.get_nth_curve_function(i - 1)(residue)

    def get_anchors_and_handles(self) -> list[np.ndarray]:
        """
        returns anchors1, handles, anchors2,
        where (anchors1[i], handles[i], anchors2[i])
        will be three points defining a quadratic bezier curve
        for any i in range(0, len(anchors1))
        """
        """
        获取二阶贝塞尔曲线的anchor和handle
        [anchor1_list, handle_list, anchor2_list]
        """
        nppc = self.n_points_per_curve
        points = self.get_points()
        return [
            points[i::nppc]
            for i in range(nppc)
        ]

    def get_start_anchors(self) -> np.ndarray:
        """
        所有贝塞尔曲线的第一个锚点的集合
        """
        return self.get_points()[0::self.n_points_per_curve]

    def get_end_anchors(self) -> np.ndarray:
        """
        所有贝塞尔曲线的最后一个锚点的集合
        """
        nppc = self.n_points_per_curve
        return self.get_points()[nppc - 1::nppc]

    def get_anchors(self) -> np.ndarray:
        """
        获取所有的锚点
        """
        points = self.get_points()
        if len(points) == 1:
            return points
        return np.array(list(it.chain(*zip(
            self.get_start_anchors(),
            self.get_end_anchors(),
        ))))

    def get_points_without_null_curves(self, atol: float=1e-9) -> np.ndarray:
        nppc = self.n_points_per_curve
        points = self.get_points()
        distinct_curves = reduce(op.or_, [
            (abs(points[i::nppc] - points[0::nppc]) > atol).any(1)
            for i in range(1, nppc)
        ])
        return points[distinct_curves.repeat(nppc)]

    def get_arc_length(self, n_sample_points: int | None = None) -> float:
        if n_sample_points is None:
            n_sample_points = 4 * self.get_num_curves() + 1
        points = np.array([
            self.point_from_proportion(a)
            for a in np.linspace(0, 1, n_sample_points)
        ])
        diffs = points[1:] - points[:-1]
        norms = np.array([get_norm(d) for d in diffs])
        return norms.sum()

    def get_area_vector(self) -> np.ndarray:
        '''
        返回一个向量，其长度为锚点(没有handle)形成的多边形所围成的面积，根据右手定则指向垂直于该多边形的方向

        这里只是近似的面积
        '''
        # Returns a vector whose length is the area bound by
        # the polygon formed by the anchor points, pointing
        # in a direction perpendicular to the polygon according
        # to the right hand rule.
        if not self.has_points():
            return np.zeros(3)

        nppc = self.n_points_per_curve
        points = self.get_points()
        # 第一个锚点的集合
        p0 = points[0::nppc]
        # 最后一个锚点的集合
        p1 = points[nppc - 1::nppc]
        # 并没有handle的参与，所以这里的面积是由anchor点形成的多边形的面积

        # Each term goes through all edges [(x1, y1, z1), (x2, y2, z2)]
        return 0.5 * np.array([
            sum((p0[:, 1] + p1[:, 1]) * (p1[:, 2] - p0[:, 2])),  # Add up (y1 + y2)*(z2 - z1)
            sum((p0[:, 2] + p1[:, 2]) * (p1[:, 0] - p0[:, 0])),  # Add up (z1 + z2)*(x2 - x1)
            sum((p0[:, 0] + p1[:, 0]) * (p1[:, 1] - p0[:, 1])),  # Add up (x1 + x2)*(y2 - y1)
        ])

    def get_unit_normal(self, recompute: bool = False) -> np.ndarray:
        '''
        获取单位法向量
        '''
        if not recompute:
            return self.data["unit_normal"][0]

        if self.get_num_points() < 3:
            return OUT

        # 这里的area_vect是多边形的面积向量，不是原始图形的面积向量
        # 然而，这里计算的是法向量，所以不影响结果
        area_vect = self.get_area_vector()
        area = get_norm(area_vect)
        if area > 0:
            normal = area_vect / area
        else:
            points = self.get_points()
            normal = get_unit_normal(
                points[1] - points[0],
                points[2] - points[1],
            )
        self.data["unit_normal"][:] = normal
        return normal

    def refresh_unit_normal(self):
        for mob in self.get_family():
            mob.get_unit_normal(recompute=True)
        return self

    # Alignment
    def align_points(self, vmobject: VMobject):
        '''对齐锚点，主要用于 Transform 的内部实现'''
        if self.get_num_points() == len(vmobject.get_points()):
            """
            这里不应该是return self吗?
            """
            return

        for mob in self, vmobject:
            # If there are no points, add one to
            # where the "center" is
            if not mob.has_points():
                mob.start_new_path(mob.get_center())
            # If there's only one point, turn it into
            # a null curve
            if mob.has_new_path_started():
                mob.add_line_to(mob.get_points()[0])

        # Figure out what the subpaths are, and align
        subpaths1 = self.get_subpaths()
        subpaths2 = vmobject.get_subpaths()
        n_subpaths = max(len(subpaths1), len(subpaths2))
        # Start building new ones
        new_subpaths1 = []
        new_subpaths2 = []

        nppc = self.n_points_per_curve

        def get_nth_subpath(path_list, n):
            if n >= len(path_list):
                # Create a null path at the very end
                return [path_list[-1][-1]] * nppc
            return path_list[n]

        for n in range(n_subpaths):
            sp1 = get_nth_subpath(subpaths1, n)
            sp2 = get_nth_subpath(subpaths2, n)
            diff1 = max(0, (len(sp2) - len(sp1)) // nppc)
            diff2 = max(0, (len(sp1) - len(sp2)) // nppc)
            sp1 = self.insert_n_curves_to_point_list(diff1, sp1)
            sp2 = self.insert_n_curves_to_point_list(diff2, sp2)
            new_subpaths1.append(sp1)
            new_subpaths2.append(sp2)
        self.set_points(np.vstack(new_subpaths1))
        vmobject.set_points(np.vstack(new_subpaths2))
        return self

    def insert_n_curves(self, n: int, recurse: bool = True):
        for mob in self.get_family(recurse):
            if mob.get_num_curves() > 0:
                new_points = mob.insert_n_curves_to_point_list(n, mob.get_points())
                # TODO, this should happen in insert_n_curves_to_point_list
                if mob.has_new_path_started():
                    new_points = np.vstack([new_points, mob.get_last_point()])
                mob.set_points(new_points)
        return self

    def insert_n_curves_to_point_list(self, n: int, points: np.ndarray):
        nppc = self.n_points_per_curve
        if len(points) == 1:
            return np.repeat(points, nppc * n, 0)

        bezier_groups = list(self.get_bezier_tuples_from_points(points))
        norms = np.array([
            get_norm(bg[nppc - 1] - bg[0])
            for bg in bezier_groups
        ])
        total_norm = sum(norms)
        # Calculate insertions per curve (ipc)
        if total_norm < 1e-6:
            ipc = [n] + [0] * (len(bezier_groups) - 1)
        else:
            ipc = np.round(n * norms / sum(norms)).astype(int)

        diff = n - sum(ipc)
        for x in range(diff):
            ipc[np.argmin(ipc)] += 1
        for x in range(-diff):
            ipc[np.argmax(ipc)] -= 1

        new_points = []
        for group, n_inserts in zip(bezier_groups, ipc):
            # What was once a single quadratic curve defined
            # by "group" will now be broken into n_inserts + 1
            # smaller quadratic curves
            alphas = np.linspace(0, 1, n_inserts + 2)
            for a1, a2 in zip(alphas, alphas[1:]):
                new_points += partial_quadratic_bezier_points(group, a1, a2)
        return np.vstack(new_points)

    """
    c = Circle().set_color(RED)
    s = Square().set_color(TEAL)
    c.align_points(s)

    vm = c.copy()
    vm.interpolate(c, s, 0.2)
    vm.shift(UP*2)
    self.add(c, s, vm)
    self.wait(1)
    """
    def interpolate(
        self,
        mobject1: VMobject,
        mobject2: VMobject,
        alpha: float,
        *args, **kwargs
    ):
        '''mobject1 到 mobject2 百分比为 alpha 的补间'''
        """
        这个函数接口的定义和实现都不好
        接口: 这个函数返回的是对两个vmob的补间。按功能讲, 应该是一个单独的函数, 而不是vmob的方法
        实现: 插值之前要先对齐points。但代码中没有。可以先比较一下两个vmob的顶点数目的多少, 让数目少的对齐数目多的

        之所以需要对齐points, 本质是因为后面会执行 alpha*arr1 + (1-alpha)*arr2
        arr1是mob1的点集, arr2是mob2的点集
        当点集维度不同的时候, 无法执行加法
        """
        super().interpolate(mobject1, mobject2, alpha, *args, **kwargs)
        if self.has_fill():
            tri1 = mobject1.get_triangulation()
            tri2 = mobject2.get_triangulation()
            if len(tri1) != len(tri1) or not np.all(tri1 == tri2):
                # 重新计算三角剖分
                self.refresh_triangulation()
        return self

    def pointwise_become_partial(self, vmobject: VMobject, a: float, b: float):
        '''返回 vmobject 上百分比从 a 到 b 的部分曲线的拷贝'''
        assert(isinstance(vmobject, VMobject))
        if a <= 0 and b >= 1:
            self.become(vmobject)
            return self
        num_curves = vmobject.get_num_curves()
        nppc = self.n_points_per_curve

        # Partial curve includes three portions:
        # - A middle section, which matches the curve exactly
        # - A start, which is some ending portion of an inner quadratic
        # - An end, which is the starting portion of a later inner quadratic

        lower_index, lower_residue = integer_interpolate(0, num_curves, a)
        upper_index, upper_residue = integer_interpolate(0, num_curves, b)
        i1 = nppc * lower_index
        i2 = nppc * (lower_index + 1)
        i3 = nppc * upper_index
        i4 = nppc * (upper_index + 1)

        vm_points = vmobject.get_points()
        new_points = vm_points.copy()
        if num_curves == 0:
            new_points[:] = 0
            return self
        if lower_index == upper_index:
            tup = partial_quadratic_bezier_points(vm_points[i1:i2], lower_residue, upper_residue)
            new_points[:i1] = tup[0]
            new_points[i1:i4] = tup
            new_points[i4:] = tup[2]
            new_points[nppc:] = new_points[nppc - 1]
        else:
            low_tup = partial_quadratic_bezier_points(vm_points[i1:i2], lower_residue, 1)
            high_tup = partial_quadratic_bezier_points(vm_points[i3:i4], 0, upper_residue)
            new_points[0:i1] = low_tup[0]
            new_points[i1:i2] = low_tup
            # Keep new_points i2:i3 as they are
            new_points[i3:i4] = high_tup
            new_points[i4:] = high_tup[2]
        self.set_points(new_points)
        return self

    def get_subcurve(self, a: float, b: float) -> VMobject:
        '''获取路径上百分比为 a 到 b 的部分'''
        vmob = self.copy()
        vmob.pointwise_become_partial(self, a, b)
        return vmob

    # Related to triangulation

    def refresh_triangulation(self):
        '''重置三角剖分'''
        for mob in self.get_family():
            mob.needs_new_triangulation = True
        return self

    def get_triangulation(self, normal_vector: np.ndarray | None = None):
        # Figure out how to triangulate the interior to know
        # how to send the points as to the vertex shader.
        # First triangles come directly from the points
        """
        经过三角形剖分后的结果是啥？

        t = Circle().set_stroke(RED, width=3)
        self.add(t)
        t.needs_new_triangulation = True
        print(t.get_triangulation())

        [ 0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20 21 22 23
         21 23  0  0  3  6  6  9 12 12 15 18 18 21  0  0  6 12 12 18  0]

         3个一组确定一个三角形(似乎多了一组(21,23,0))
         可以发现, 一个圆的三角剖分的结果和 
         https://docs.manim.org.cn/documentation/shaders/quadratic_bezier_fill.html
         图示的结果一样         
        """
        """
        三角剖分算法: earclip triangulation
        Earclip triangulation is a method used in computational geometry to divide 
        a simple polygon into a set of triangles. It is called "earclip" because it 
        involves identifying and "clipping" or removing "ears" from the polygon until 
        it is fully triangulated. An "ear" in this context refers to a convex vertex 
        of the polygon that can be safely removed along with its connecting edges to 
        form a triangle.
        """
        if normal_vector is None:
            normal_vector = self.get_unit_normal(recompute=True)

        if not self.needs_new_triangulation:
            return self.triangulation

        points = self.get_points()

        if len(points) <= 1:
            self.triangulation = np.zeros(0, dtype='i4')
            self.needs_new_triangulation = False
            return self.triangulation

        if not np.isclose(normal_vector, OUT).all():
            # Rotate points such that unit normal vector is OUT
            points = np.dot(points, z_to_vector(normal_vector))
        indices = np.arange(len(points), dtype=int)

        b0s = points[0::3]
        b1s = points[1::3]
        b2s = points[2::3]
        v01s = b1s - b0s
        v12s = b2s - b1s

        crosses = cross2d(v01s, v12s)
        convexities = np.sign(crosses)

        atol = self.tolerance_for_point_equality
        end_of_loop = np.zeros(len(b0s), dtype=bool)
        end_of_loop[:-1] = (np.abs(b2s[:-1] - b0s[1:]) > atol).any(1)
        end_of_loop[-1] = True

        concave_parts = convexities < 0

        # These are the vertices to which we'll apply a polygon triangulation
        inner_vert_indices = np.hstack([
            indices[0::3],
            indices[1::3][concave_parts],
            indices[2::3][end_of_loop],
        ])
        inner_vert_indices.sort()
        rings = np.arange(1, len(inner_vert_indices) + 1)[inner_vert_indices % 3 == 2]

        # Triangulate
        inner_verts = points[inner_vert_indices]
        inner_tri_indices = inner_vert_indices[
            earclip_triangulation(inner_verts, rings)
        ]

        tri_indices = np.hstack([indices, inner_tri_indices])
        self.triangulation = tri_indices
        self.needs_new_triangulation = False
        return tri_indices

    def triggers_refreshed_triangulation(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            old_points = self.get_points().copy()
            func(self, *args, **kwargs)
            if not np.all(self.get_points() == old_points):
                self.refresh_unit_normal()
                self.refresh_triangulation()
        return wrapper

    @triggers_refreshed_triangulation
    def set_points(self, points: npt.ArrayLike):
        '''设置物件的锚点，传入的数组必须为 Nx3'''
        super().set_points(points)
        return self

    @triggers_refreshed_triangulation
    def set_data(self, data: dict):
        super().set_data(data)
        return self

    # TODO, how to be smart about tangents here?
    @triggers_refreshed_triangulation
    def apply_function(
        self,
        function: Callable[[np.ndarray], np.ndarray],
        make_smooth: bool = False,
        **kwargs
    ):
        '''把 ``function`` 作用到所有锚点上'''
        super().apply_function(function, **kwargs)
        if self.make_smooth_after_applying_functions or make_smooth:
            self.make_approximately_smooth()
        return self

    def flip(self, axis: np.ndarray = UP, **kwargs):
        '''绕 axis 轴翻转'''
        super().flip(axis, **kwargs)
        self.refresh_unit_normal()
        self.refresh_triangulation()
        return self

    # For shaders
    def init_shader_data(self):
        self.fill_data = np.zeros(0, dtype=self.fill_dtype)
        self.stroke_data = np.zeros(0, dtype=self.stroke_dtype)
        self.fill_shader_wrapper = ShaderWrapper(
            vert_data=self.fill_data,
            vert_indices=np.zeros(0, dtype='i4'),
            shader_folder=self.fill_shader_folder,
            render_primitive=self.render_primitive,
        )
        self.stroke_shader_wrapper = ShaderWrapper(
            vert_data=self.stroke_data,
            shader_folder=self.stroke_shader_folder,
            render_primitive=self.render_primitive,
        )

    def refresh_shader_wrapper_id(self):
        for wrapper in [self.fill_shader_wrapper, self.stroke_shader_wrapper]:
            wrapper.refresh_id()
        return self

    def get_fill_shader_wrapper(self) -> ShaderWrapper:
        # 顶点数据
        self.fill_shader_wrapper.vert_data = self.get_fill_shader_data()
        # 顶点索引，三角形剖分
        self.fill_shader_wrapper.vert_indices = self.get_fill_shader_vert_indices()
        self.fill_shader_wrapper.uniforms = self.get_shader_uniforms()
        self.fill_shader_wrapper.depth_test = self.depth_test
        return self.fill_shader_wrapper

    def get_stroke_shader_wrapper(self) -> ShaderWrapper:
        self.stroke_shader_wrapper.vert_data = self.get_stroke_shader_data()
        self.stroke_shader_wrapper.uniforms = self.get_stroke_uniforms()
        self.stroke_shader_wrapper.depth_test = self.depth_test
        return self.stroke_shader_wrapper

    def get_shader_wrapper_list(self) -> list[ShaderWrapper]:
        # Build up data lists
        fill_shader_wrappers = []
        stroke_shader_wrappers = []
        back_stroke_shader_wrappers = []
        for submob in self.family_members_with_points():
            if submob.has_fill():
                fill_shader_wrappers.append(submob.get_fill_shader_wrapper())
            if submob.has_stroke():
                ssw = submob.get_stroke_shader_wrapper()
                if submob.draw_stroke_behind_fill:
                    back_stroke_shader_wrappers.append(ssw)
                else:
                    stroke_shader_wrappers.append(ssw)

        # Combine data lists
        wrapper_lists = [
            back_stroke_shader_wrappers,
            fill_shader_wrappers,
            stroke_shader_wrappers
        ]
        result = []
        for wlist in wrapper_lists:
            if wlist:
                wrapper = wlist[0]
                wrapper.combine_with(*wlist[1:])
                result.append(wrapper)
        return result

    def get_stroke_uniforms(self) -> dict[str, float]:
        result = dict(super().get_shader_uniforms())
        result["joint_type"] = JOINT_TYPE_MAP[self.joint_type]
        result["flat_stroke"] = float(self.flat_stroke)
        return result

    def get_stroke_shader_data(self) -> np.ndarray:
        points = self.get_points()
        if len(self.stroke_data) != len(points):
            self.stroke_data = resize_array(self.stroke_data, len(points))

        if "points" not in self.locked_data_keys:
            nppc = self.n_points_per_curve
            self.stroke_data["point"] = points
            self.stroke_data["prev_point"][:nppc] = points[-nppc:]
            self.stroke_data["prev_point"][nppc:] = points[:-nppc]
            self.stroke_data["next_point"][:-nppc] = points[nppc:]
            self.stroke_data["next_point"][-nppc:] = points[:nppc]

        self.read_data_to_shader(self.stroke_data, "color", "stroke_rgba")
        self.read_data_to_shader(self.stroke_data, "stroke_width", "stroke_width")
        self.read_data_to_shader(self.stroke_data, "unit_normal", "unit_normal")

        return self.stroke_data

    def get_fill_shader_data(self) -> np.ndarray:
        points = self.get_points()
        if len(self.fill_data) != len(points):
            self.fill_data = resize_array(self.fill_data, len(points))
            self.fill_data["vert_index"][:, 0] = range(len(points))

        self.read_data_to_shader(self.fill_data, "point", "points")
        self.read_data_to_shader(self.fill_data, "color", "fill_rgba")
        self.read_data_to_shader(self.fill_data, "unit_normal", "unit_normal")

        return self.fill_data

    def refresh_shader_data(self):
        self.get_fill_shader_data()
        self.get_stroke_shader_data()

    def get_fill_shader_vert_indices(self) -> np.ndarray:
        """
        需要进一步解释一下这里的顶点索引
        一个VMobject对象, 当执行set_data函数的时候, 每个顶点按照列表的顺序已经有了列表索引
        但是这里需要计算的是这些顶点组成三角形后的索引
        比如:
        按照列表索引: 0, 1, 2, 3
        经过三角剖分后
        得到新的索引:0, 1, 2, 1, 2, 3
        每3个订单组成一个三角形
        """
        return self.get_triangulation()


class VGroup(VMobject):
    """
    和 ``VMobject`` 相同，主要用作包含一些子物体（必须都是 VMobject)
    """
    def __init__(self, *vmobjects: VMobject, **kwargs):
        if not all([isinstance(m, VMobject) for m in vmobjects]):
            raise Exception("All submobjects must be of type VMobject")
        super().__init__(**kwargs)
        self.add(*vmobjects)

    def __add__(self, other: VMobject | VGroup):
        assert(isinstance(other, VMobject))
        return self.add(other)


class VectorizedPoint(Point, VMobject):
    """
    以 VMobject 形式存在的单个点
    """
    CONFIG = {
        "color": BLACK,
        "fill_opacity": 0,
        "stroke_width": 0,
        "artificial_width": 0.01,
        "artificial_height": 0.01,
    }

    def __init__(self, location: np.ndarray = ORIGIN, **kwargs):
        Point.__init__(self, **kwargs)
        VMobject.__init__(self, **kwargs)
        self.set_points(np.array([location]))


class CurvesAsSubmobjects(VGroup):
    """
    传入一个 VMobject 实例（物体），将其所有段曲线作为子物体（一个子物体为一条曲线）
    """
    def __init__(self, vmobject: VMobject, **kwargs):
        super().__init__(**kwargs)
        for tup in vmobject.get_bezier_tuples():
            part = VMobject()
            part.set_points(tup)
            part.match_style(vmobject)
            self.add(part)


class DashedVMobject(VMobject):
    """ 
    传入一个 VMobject 实例（物体），将其所有曲线全部设为虚线
    
    - 传入 ``num_dashed`` 表示分为多少段虚线
    - 传入 ``positive_space_ratio`` 表示虚实比例
    """
    CONFIG = {
        "num_dashes": 15,
        "positive_space_ratio": 0.5,
        "color": WHITE
    }

    def __init__(self, vmobject: VMobject, **kwargs):
        super().__init__(**kwargs)
        num_dashes = self.num_dashes
        ps_ratio = self.positive_space_ratio
        if num_dashes > 0:
            # End points of the unit interval for division
            alphas = np.linspace(0, 1, num_dashes + 1)

            # This determines the length of each "dash"
            full_d_alpha = (1.0 / num_dashes)
            partial_d_alpha = full_d_alpha * ps_ratio

            # Rescale so that the last point of vmobject will
            # be the end of the last dash
            alphas /= (1 - full_d_alpha + partial_d_alpha)

            self.add(*[
                vmobject.get_subcurve(alpha, alpha + partial_d_alpha)
                for alpha in alphas[:-1]
            ])
        # Family is already taken care of by get_subcurve
        # implementation
        self.match_style(vmobject, recurse=False)
