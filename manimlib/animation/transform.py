from __future__ import annotations

import inspect
from typing import Callable, Union, Sequence

import numpy as np
import numpy.typing as npt

from manimlib.animation.animation import Animation
from manimlib.constants import DEFAULT_POINTWISE_FUNCTION_RUN_TIME
from manimlib.constants import OUT
from manimlib.constants import DEGREES
from manimlib.mobject.mobject import Group
from manimlib.mobject.mobject import Mobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.paths import path_along_arc
from manimlib.utils.paths import straight_path
from manimlib.utils.rate_functions import smooth
from manimlib.utils.rate_functions import squish_rate_func

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import colour
    from manimlib.scene.scene import Scene
    ManimColor = Union[str, colour.Color, Sequence[float]]

"""
title = titles[0]
        
for next_title in titles[1:]:
    self.play(Transform(title, next_title))
    self.wait(3)

Transform这个类的作用是将mobject的属性变成target的属性
所以,一开始的时候, title是titles[0]
执行了一次动画后, title就变成了titles[1]
"""
"""
area = Tex("\\text{Area}", "=", "\\pi", "R", "^2")
area.next_to(self.pi_creature.get_corner(UP+RIGHT), UP+RIGHT)

self.play(
        self.pi_creature.change_mode, "raise_right_hand",
        self.pi_creature.look_at, area,
        Transform(R_copy, area.get_part_by_tex("R"))
        )
self.play(Write(area))
self.remove(R_copy)

应该将这种用法抽象成一个固有的模式
当场景中有图和公式的时候
图上有一些符号也会出现在公式中
我们可以执行一次Transform
将图上的符号变成公式中的符号
然后再执行一次Write
"""
class Transform(Animation):
    CONFIG = {
        "path_arc": 0,
        "path_arc_axis": OUT,
        "path_func": None,
        "replace_mobject_with_target_in_scene": False,
    }

    def __init__(
        self,
        mobject: Mobject,
        target_mobject: Mobject | None = None,
        **kwargs
    ):
        super().__init__(mobject, **kwargs)
        self.target_mobject = target_mobject
        self.init_path_func()

    def init_path_func(self) -> None:
        if self.path_func is not None:
            return
        elif self.path_arc == 0:
            self.path_func = straight_path
        else:
            self.path_func = path_along_arc(
                self.path_arc,
                self.path_arc_axis,
            )

    def begin(self) -> None:
        self.target_mobject = self.create_target()
        self.check_target_mobject_validity()
        # Use a copy of target_mobject for the align_data_and_family
        # call so that the actual target_mobject stays
        # preserved, since calling allign_data will potentially
        # change the structure of both arguments
        self.target_copy = self.target_mobject.copy()
        """
        以前有一个很大的疑问: 如何对circle和square进行插值?
        它们的点集的数目是不一样的
        现在看来, 这个问题的关键在于, 如何对两个mobject进行对齐
        """
        """
        下面的对齐也可以注释掉, 然后在场景代码中添加
        circle.align_data_and_family(square)
        """
        self.mobject.align_data_and_family(self.target_copy)
        
        super().begin()
        self.mobject.lock_matching_data(
            self.starting_mobject,
            self.target_copy,
        )

    def finish(self) -> None:
        super().finish()
        self.mobject.unlock_data()

    def create_target(self) -> Mobject:
        # Has no meaningful effect here, but may be useful
        # in subclasses
        return self.target_mobject

    def check_target_mobject_validity(self) -> None:
        if self.target_mobject is None:
            raise Exception(
                f"{self.__class__.__name__}.create_target not properly implemented"
            )

    """
    def finish_animations(self, animations: Iterable[Animation]) -> None:
        for animation in animations:
            animation.finish()
            animation.clean_up_from_scene(self)
        if self.skip_animations:
            self.update_mobjects(self.get_run_time(animations))
        else:
            self.update_mobjects(0)
    
    clean_up_from_scene方法是在动画结束的时候执行
    不论是Transfrom还是ReplacementTransform
    动画过程中, 都是mobject逐渐变为target
    当动画结束的时候, mobject就变成了target
    此时, 在屏幕上可以显示mobect
    也可以显示target
    作为观察者, 是看不出区别的
    """
    def clean_up_from_scene(self, scene: Scene) -> None:
        super().clean_up_from_scene(scene)
        if self.replace_mobject_with_target_in_scene:
            # 并没有删除mobject
            # add和remove只是让mob可见或者不可见
            scene.remove(self.mobject)
            scene.add(self.target_mobject)

    def update_config(self, **kwargs) -> None:
        Animation.update_config(self, **kwargs)
        if "path_arc" in kwargs:
            self.path_func = path_along_arc(
                kwargs["path_arc"],
                kwargs.get("path_arc_axis", OUT)
            )

    def get_all_mobjects(self) -> list[Mobject]:
        return [
            self.mobject,
            self.starting_mobject,
            self.target_mobject,
            self.target_copy,
        ]

    def get_all_families_zipped(self) -> zip[tuple[Mobject]]:
        return zip(*[
            mob.get_family()
            for mob in [
                self.mobject,
                self.starting_mobject,
                self.target_copy,
            ]
        ])

    # 特别注意，这个函数和父类的同名函数，参数个数不一致
    def interpolate_submobject(
        self,
        submob: Mobject,
        start: Mobject,
        target_copy: Mobject,
        alpha: float
    ):
        submob.interpolate(start, target_copy, alpha, self.path_func)
        return self

"""
for d_rect, corner_pair in zip(d_rects, corner_pairs):
    line = Line(*[
        rect.get_corner(corner)
        for corner in corner_pair
    ])
    d_rect.line = d_rect.copy().replace(line, stretch = True)
    d_rect.line.set_color(d_rect.get_color())

ReplacementTransform(d_rect.line, d_rect)
"""
"""
self.play(
    Write(width_label.get_part_by_tex("pi")),
    ReplacementTransform(
        self.ring_radius_group[1].copy(),
        width_label.get_part_by_tex("r")
    )
)
将ring_radius_group中的r变成width_label中的r
动画结束后
移除ring_radius_group中的r
保留width_label中的r

使用ReplacementTransform的完美场景
"""
class ReplacementTransform(Transform):
    CONFIG = {
        "replace_mobject_with_target_in_scene": True,
    }


"""
self.play(TransformFromCopy(sectors, laid_sectors, run_time=2))

In simple terms, Transform directly changes the original object into the target, 
while TransformFromCopy leaves the original object unchanged and uses a copy of 
it for the transformation. This difference is crucial depending on whether you 
want to maintain the original object post-animation or not.
"""
"""
self.play(ShowCreation(width_line))
self.play(TransformFromCopy(width_line, semi_circ, path_arc=-PI / 2, run_time=2))
"""
class TransformFromCopy(Transform):
    """
    Performs a reversed Transform
    """

    def __init__(self, mobject: Mobject, target_mobject: Mobject, **kwargs):
        super().__init__(target_mobject, mobject, **kwargs)

    def interpolate(self, alpha: float) -> None:
        super().interpolate(1 - alpha)


class ClockwiseTransform(Transform):
    CONFIG = {
        "path_arc": -np.pi
    }


class CounterclockwiseTransform(Transform):
    CONFIG = {
        "path_arc": np.pi
    }


"""
frame = self.frame
frame.target = frame.generate_target()
frame.target.scale(1.75, about_edge=LEFT)
self.play(
    LaggedStartMap(
        FadeIn, VGroup(*blocks[10:30]),
        lag_ratio=0.9, # 将lag_ratio设置为0, 所有的block同时出现
    ),
    MoveToTarget(frame, rate_func=rush_into),
    run_time=12,
    )
"""
"""
MoveToTarget这个类名字起得不好, 容易让人误解
直观的印象就是将mobect移动到target的位置
但实际上, 这个类的作用是将mobject的属性变成target的属性
包括点集，颜色，透明度等等

MoveToTarget这个类初始化需要一个mobject
给人的感觉是这个transform只需要一个对象
但实际上, 这个类还需要一个target
只是这个target是通过拷贝mobject得到的
"""
"""
MoveToTarget这个类的作用是将mobject的属性变成target的属性
是现在的自己和过去的自己之间的一次变化
"""
"""
self.play(
    MoveToTarget(
        example_ring,
        path_arc = -np.pi/2,
        run_time = 2
    ),
    Animation(self.x_axis),
)
self.wait(2)

self.play(*[
    MoveToTarget(
        ring,
        path_arc = -np.pi/2,
        run_time = 4,
        rate_func = squish_rate_func(smooth, alpha, alpha+0.25)
    )
    for ring, alpha in zip(
        transformed_rings, 
        np.linspace(0, 0.75, len(transformed_rings))
    )
] + foreground_animations)
self.wait()

简简单单的MoveToTarget
竟然用到如此水平！！！
"""
class MoveToTarget(Transform):
    def __init__(self, mobject: Mobject, **kwargs):
        self.check_validity_of_input(mobject)
        super().__init__(mobject, mobject.target, **kwargs)

    def check_validity_of_input(self, mobject: Mobject) -> None:
        if not hasattr(mobject, "target"):
            raise Exception(
                "MoveToTarget called on mobject"
                "without attribute 'target'"
            )


class _MethodAnimation(MoveToTarget):
    def __init__(self, mobject: Mobject, methods: Callable):
        self.methods = methods
        super().__init__(mobject)


"""
x = ValueTracker(0)
self.play(ApplyMethod(x.increment_value, 3, run_time=5))

self.play(ApplyMethod(sine.shift, 4*LEFT, **kwargs))

self.play(*[
            ApplyMethod(mob.scale, 0.5*random.random(), **kwargs)
            for mob in self.intervals
        ])

通过method, 获得一个target
"""
class ApplyMethod(Transform):
    def __init__(self, method: Callable, *args, **kwargs):
        """
        method is a method of Mobject, *args are arguments for
        that method.  Key word arguments should be passed in
        as the last arg, as a dict, since **kwargs is for
        configuration of the transform itself

        Relies on the fact that mobject methods return the mobject
        """
        """
        将vmob的一个方法封装成animation
        本质上和animate一样
        """
        self.check_validity_of_input(method)
        self.method = method
        self.method_args = args
        super().__init__(method.__self__, **kwargs)

    def check_validity_of_input(self, method: Callable) -> None:
        if not inspect.ismethod(method):
            raise Exception(
                "Whoops, looks like you accidentally invoked "
                "the method you want to animate"
            )
        assert(isinstance(method.__self__, Mobject))

    def create_target(self) -> Mobject:
        method = self.method
        # Make sure it's a list so that args.pop() works
        args = list(self.method_args)

        if len(args) > 0 and isinstance(args[-1], dict):
            method_kwargs = args.pop()
        else:
            method_kwargs = {}
        target = method.__self__.copy()
        method.__func__(target, *args, **method_kwargs)
        return target


class ApplyPointwiseFunction(ApplyMethod):
    CONFIG = {
        "run_time": DEFAULT_POINTWISE_FUNCTION_RUN_TIME
    }

    def __init__(
        self,
        function: Callable[[np.ndarray], np.ndarray],
        mobject: Mobject,
        **kwargs
    ):
        super().__init__(mobject.apply_function, function, **kwargs)


class ApplyPointwiseFunctionToCenter(ApplyPointwiseFunction):
    def __init__(
        self,
        function: Callable[[np.ndarray], np.ndarray],
        mobject: Mobject,
        **kwargs
    ):
        self.function = function
        super().__init__(mobject.move_to, **kwargs)

    def begin(self) -> None:
        self.method_args = [
            self.function(self.mobject.get_center())
        ]
        super().begin()


class FadeToColor(ApplyMethod):
    def __init__(
        self,
        mobject: Mobject,
        color: ManimColor,
        **kwargs
    ):
        super().__init__(mobject.set_color, color, **kwargs)


class ScaleInPlace(ApplyMethod):
    def __init__(
        self,
        mobject: Mobject,
        scale_factor: npt.ArrayLike,
        **kwargs
    ):
        super().__init__(mobject.scale, scale_factor, **kwargs)


class ShrinkToCenter(ScaleInPlace):
    def __init__(self, mobject: Mobject, **kwargs):
        super().__init__(mobject, 0, **kwargs)


class Restore(ApplyMethod):
    def __init__(self, mobject: Mobject, **kwargs):
        super().__init__(mobject.restore, **kwargs)


class ApplyFunction(Transform):
    """
    和ApplyMethod类进行对比

    通过function对mobject进行变换, 得到target
    然后执行插值操作
    """
    def __init__(
        self,
        function: Callable[[Mobject], Mobject],
        mobject: Mobject,
        **kwargs
    ):
        self.function = function
        super().__init__(mobject, **kwargs)

    def create_target(self) -> Mobject:
        target = self.function(self.mobject.copy())
        if not isinstance(target, Mobject):
            raise Exception("Functions passed to ApplyFunction must return object of type Mobject")
        return target


class ApplyMatrix(ApplyPointwiseFunction):
    def __init__(
        self,
        matrix: npt.ArrayLike,
        mobject: Mobject,
        **kwargs
    ):
        matrix = self.initialize_matrix(matrix)

        def func(p):
            return np.dot(p, matrix.T)

        super().__init__(func, mobject, **kwargs)

    def initialize_matrix(self, matrix: npt.ArrayLike) -> np.ndarray:
        matrix = np.array(matrix)
        if matrix.shape == (2, 2):
            new_matrix = np.identity(3)
            new_matrix[:2, :2] = matrix
            matrix = new_matrix
        elif matrix.shape != (3, 3):
            raise Exception("Matrix has bad dimensions")
        return matrix


class ApplyComplexFunction(ApplyMethod):
    def __init__(
        self,
        function: Callable[[complex], complex],
        mobject: Mobject,
        **kwargs
    ):
        self.function = function
        method = mobject.apply_complex_function
        super().__init__(method, function, **kwargs)

    def init_path_func(self) -> None:
        func1 = self.function(complex(1))
        self.path_arc = np.log(func1).imag
        super().init_path_func()

###


class CyclicReplace(Transform):
    CONFIG = {
        "path_arc": 90 * DEGREES,
    }

    def __init__(self, *mobjects: Mobject, **kwargs):
        self.group = Group(*mobjects)
        super().__init__(self.group, **kwargs)

    def create_target(self) -> Mobject:
        target = self.group.copy()
        cycled_targets = [target[-1], *target[:-1]]
        for m1, m2 in zip(cycled_targets, self.group):
            m1.move_to(m2)
        return target


class Swap(CyclicReplace):
    pass  # Renaming, more understandable for two entries


# TODO, this may be deprecated...worth reimplementing?
class TransformAnimations(Transform):
    CONFIG = {
        "rate_func": squish_rate_func(smooth)
    }

    def __init__(self, start_anim: Animation, end_anim: Animation, **kwargs):
        digest_config(self, kwargs, locals())
        if "run_time" in kwargs:
            self.run_time = kwargs.pop("run_time")
        else:
            self.run_time = max(start_anim.run_time, end_anim.run_time)
        for anim in start_anim, end_anim:
            anim.set_run_time(self.run_time)

        if start_anim.starting_mobject.get_num_points() != end_anim.starting_mobject.get_num_points():
            start_anim.starting_mobject.align_data_and_family(end_anim.starting_mobject)
            for anim in start_anim, end_anim:
                if hasattr(anim, "target_mobject"):
                    anim.starting_mobject.align_data_and_family(anim.target_mobject)

        Transform.__init__(self, start_anim.mobject,
                           end_anim.mobject, **kwargs)
        # Rewire starting and ending mobjects
        start_anim.mobject = self.starting_mobject
        end_anim.mobject = self.target_mobject

    def interpolate(self, alpha: float) -> None:
        self.start_anim.interpolate(alpha)
        self.end_anim.interpolate(alpha)
        Transform.interpolate(self, alpha)
