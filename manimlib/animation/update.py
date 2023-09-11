from __future__ import annotations

import operator as op
from typing import Callable

from manimlib.animation.animation import Animation

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.mobject.mobject import Mobject


"""
rect = Rectangle().set_color(BLUE)
ball_1 = Dot().set_color(RED)
ball_2 = Dot().set_color(YELLOW)
self.play(
    ShowCreation(rect, run_time=2),
    UpdateFromFunc(ball_1, lambda m: m.move_to(rect.get_end())),
    ball_2.animate.move_to(rect.get_end())              
)

ball_1的动画符合预期
ball_2的动画不符合预期
这里需要对animate函数的本质有着进一步的理解
animate后面可以跟着很多的属性设置, 本质上会产生一个target_mobject
整个animate动画等价于MoveToTarget(ball_2)
"""

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
