from __future__ import annotations

import inspect
from typing import Callable

from manimlib.constants import DEGREES
from manimlib.constants import RIGHT
from manimlib.mobject.mobject import Mobject
from manimlib.utils.simple_functions import clip

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from manimlib.animation.animation import Animation


def assert_is_mobject_method(method):
    """判断 ``method`` 是否是 Mobject 的方法"""
    assert(inspect.ismethod(method))
    mobject = method.__self__
    assert(isinstance(mobject, Mobject))


def always(method, *args, **kwargs):
    """一直调用 ``method``，传入 ``*args, **kwargs``"""
    assert_is_mobject_method(method)
    mobject = method.__self__
    func = method.__func__
    mobject.add_updater(lambda m: func(m, *args, **kwargs))
    return mobject


def f_always(method, *arg_generators, **kwargs):
    """
    More functional version of always, where instead
    of taking in args, it takes in functions which output
    the relevant arguments.
    """
    """与 ``always`` 类似，但是传入的多个 ``arg_generators`` 是可调用对象，用于生成参数"""
    assert_is_mobject_method(method)
    mobject = method.__self__
    func = method.__func__

    def updater(mob):
        args = [
            arg_generator()
            for arg_generator in arg_generators
        ]
        func(mob, *args, **kwargs)

    mobject.add_updater(updater)
    return mobject


"""
arc = always_redraw(lambda: Arc(
            start_angle=PI / 2,
            angle=-get_theta(),
            radius=0.5,
            stroke_width=2,
        ).rotate(PI / 2, RIGHT, about_point=ORIGIN).shift(get_fc()))
"""
def always_redraw(func: Callable[..., Mobject], *args, **kwargs) -> Mobject:
    """始终重复调用 ``func`` 生成新物体"""
    """
    mob = Mobject()
    似乎也未尝不可
    """
    mob = func(*args, **kwargs)
    mob.add_updater(lambda m: mob.become(func(*args, **kwargs)))
    return mob


def always_shift(
    mobject: Mobject,
    direction: np.ndarray = RIGHT,
    rate: float = 0.1
) -> Mobject:
    """将 ``mobject`` 始终向 ``direction`` 方向移动，速度为 ``rate``"""
    mobject.add_updater(
        lambda m, dt: m.shift(dt * rate * direction)
    )
    return mobject


def always_rotate(
    mobject: Mobject,
    rate: float = 20 * DEGREES,
    **kwargs
) -> Mobject:
    """将 ``mobject`` 始终旋转"""
    mobject.add_updater(
        lambda m, dt: m.rotate(dt * rate, **kwargs)
    )
    return mobject


def turn_animation_into_updater(
    animation: Animation,
    cycle: bool = False,
    **kwargs
) -> Mobject:
    """
    Add an updater to the animation's mobject which applies
    the interpolation and update functions of the animation

    If cycle is True, this repeats over and over.  Otherwise,
    the updater will be popped uplon completion
    """
    """将 ``animation`` 转化为对执行动画对象的 updater
    
    - ``cycle`` 为 True 时循环执行，否则只执行一次
    """
    mobject = animation.mobject
    animation.update_config(**kwargs)
    # 当一个mob有animation的时候, 可能同时有一个updater
    # 默认情况下，执行animation的时候, updater会被暂停
    # 但是这里要将animation转成updater, 就没有必要暂停既有的updater了
    animation.suspend_mobject_updating = False
    animation.begin()
    # animation已执行的时间
    animation.total_time = 0

    def update(m, dt):
        # animation的总时长
        run_time = animation.get_run_time()
        # animation已执行比例
        time_ratio = animation.total_time / run_time
        if cycle:
            alpha = time_ratio % 1
        else:
            alpha = clip(time_ratio, 0, 1)
            if alpha >= 1:
                animation.finish()
                m.remove_updater(update)
                return
        animation.interpolate(alpha)
        animation.update_mobjects(dt)
        animation.total_time += dt

    mobject.add_updater(update)
    return mobject


def cycle_animation(animation: Animation, **kwargs) -> Mobject:
    '''默认保持循环的 ``turn_animation_into_updater``'''
    return turn_animation_into_updater(
        animation, cycle=True, **kwargs
    )
