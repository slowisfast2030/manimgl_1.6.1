from __future__ import annotations

import operator as op
from typing import Callable

from manimlib.animation.animation import Animation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.mobject.mobject import Mobject


"""
这个动画类和其他的动画类不是并列关系, 更像是总分关系
任何其他的动画类都可以用此类实现
只要给出合适的update_function
"""
class UpdateFromFunc(Animation):
    """
    update_function of the form func(mobject), presumably
    to be used when the state of one mobject is dependent
    on another simultaneously animated mobject
    """
    CONFIG = {
        "suspend_mobject_updating": False,
    }

    def __init__(
        self,
        mobject: Mobject,
        update_function: Callable[[Mobject]],
        **kwargs
    ):
        self.update_function = update_function
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        self.update_function(self.mobject)


"""
lambda的第二个参数是动画的完成比例: alpha

self.play(
        Rotate(face, -PI / 3, UP),
        UpdateFromAlphaFunc(light_lines, lambda m, a: m.set_opacity(0.5 * (1 - a)), remover=True),
        run_time=2,
        )
"""
class UpdateFromAlphaFunc(UpdateFromFunc):
    def interpolate_mobject(self, alpha: float) -> None:
        self.update_function(self.mobject, alpha)


class MaintainPositionRelativeTo(Animation):
    def __init__(
        self,
        mobject: Mobject,
        tracked_mobject: Mobject,
        **kwargs
    ):
        self.tracked_mobject = tracked_mobject
        self.diff = op.sub(
            mobject.get_center(),
            tracked_mobject.get_center(),
        )
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        target = self.tracked_mobject.get_center()
        location = self.mobject.get_center()
        self.mobject.shift(target - location + self.diff)
