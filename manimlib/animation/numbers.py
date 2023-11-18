from __future__ import annotations

from typing import Callable

from manimlib.animation.animation import Animation
from manimlib.mobject.numbers import DecimalNumber
from manimlib.utils.bezier import interpolate


class ChangingDecimal(Animation):
    """
    专门针对DecimalNumber对象的animation
    """
    CONFIG = {
        "suspend_mobject_updating": False,
    }

    def __init__(
        self,
        decimal_mob: DecimalNumber,
        number_update_func: Callable[[float], float],
        **kwargs
    ):
        assert(isinstance(decimal_mob, DecimalNumber))
        self.number_update_func = number_update_func
        super().__init__(decimal_mob, **kwargs)

    """
    有一个疑问：
    当继承Animation类时
    需要实现interpolate_mobject方法
    但有的时候是实现interpolate_submobject方法
    这是为何？

    如果动画作用的对象是一个不包含子对象的Mobject，使用interpolate_mobject
    如果动画作用的对象是一个包含子对象的Mobject，使用interpolate_submobject，
    可以针对不同的子对象进行不同的动画
    但是，如果所有子对象都是同一个动画，那么使用interpolate_mobject也是可以的

    这里动画的对象是DecimalNumber，它是一个Mobject，没有子对象，所以使用interpolate_mobject
    """
    def interpolate_mobject(self, alpha: float) -> None:
        self.mobject.set_value(
            self.number_update_func(alpha)
        )


class ChangeDecimalToValue(ChangingDecimal):
    def __init__(
        self,
        decimal_mob: DecimalNumber,
        target_number: float | complex,
        **kwargs
    ):
        start_number = decimal_mob.number
        super().__init__(
            decimal_mob,
            lambda a: interpolate(start_number, target_number, a), # 用插值函数来实现动画
            **kwargs
        )


class CountInFrom(ChangingDecimal):
    def __init__(
        self,
        decimal_mob: DecimalNumber,
        source_number: float | complex = 0,
        **kwargs
    ):
        start_number = decimal_mob.number
        super().__init__(
            decimal_mob,
            lambda a: interpolate(source_number, start_number, a),
            **kwargs
        )
