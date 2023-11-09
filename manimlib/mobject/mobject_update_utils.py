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


# /Users/linus/Desktop/less-is-more/3b1b_anaconda_install/manim/udemy/Bag_of_Tracks/51geodater.py
# 上面的示例是最好的

# 特别需要注意，这里的method方法的格式：mob.func
# 不是method
def assert_is_mobject_method(method):
    """判断 ``method`` 是否是 Mobject 的方法"""
    assert(inspect.ismethod(method))
    mobject = method.__self__
    assert(isinstance(mobject, Mobject))


"""
always(label.next_to, brace, dir)
always(stuff[0].next_to, stuff[1], LEFT, buff=MED_SMALL_BUFF)
"""
def always(method, *args, **kwargs):
    """一直调用 ``method``，传入 ``*args, **kwargs``"""
    assert_is_mobject_method(method)
    # 因为method的格式是mob.func
    # 所以可以从method中提取mob和func
    mobject = method.__self__
    func = method.__func__
    # 困惑：不应该是
    # lambda m: m.func(*args, **kwargs)
    # 难道等价？
    mobject.add_updater(lambda m: func(m, *args, **kwargs))
    return mobject


"""
x = ValueTracker(-3)
f_always(stuff[0].set_x, x.get_value)
"""
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
"""
brace = always_redraw(Brace, square, UP)
"""
def always_redraw(func: Callable[..., Mobject], *args, **kwargs) -> Mobject:
    """始终重复调用 ``func`` 生成新物体"""
    """
    Callable[..., Mobject]
    This means that the type annotation is for a callable object, which 
    is something that can be called like a function. A callable object 
    can be a function, a method, a class, or an instance with a __call__ 
    method. 

    输入：The ... in the brackets means that the callable object can take 
    any number and type of arguments. 
    
    输出：The Mobject after the arrow means that the callable object returns 
    a Mobject object
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


"""
turn_animation_into_updater(Write(stuff[0]), cycle=True)
turn_animation_into_updater(ShowCreation(stuff[1]), cycle=True)
turn_animation_into_updater(FadeIn(stuff[2]), cycle=True)
cycle_animation(FadeOut(stuff[3]))
"""
# 不得不赞叹！只有对animation和updater理解的足够深，才能完成两者之间的转换
# 佩服不已

# 可以进一步思考这个函数
# 如果将cycle设置为False，那么这个函数就是一个普通的animation
# 本质上，就将play(animation)的内部过程展现了出来
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
        # 执行animation
        animation.interpolate(alpha)
        # 假设mob同时有updater. 没有这样做也无妨
        animation.update_mobjects(dt)
        animation.total_time += dt

    mobject.add_updater(update)
    return mobject


def cycle_animation(animation: Animation, **kwargs) -> Mobject:
    '''默认保持循环的 ``turn_animation_into_updater``'''
    return turn_animation_into_updater(
        animation, cycle=True, **kwargs
    )
