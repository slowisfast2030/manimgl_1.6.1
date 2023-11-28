from __future__ import annotations

from manimlib.constants import PI
from manimlib.animation.transform import Transform

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from manimlib.mobject.mobject import Mobject
    from manimlib.mobject.geometry import Arrow


class GrowFromPoint(Transform):
    """
    start: self.mobject.copy().scale(0).move_to(self.point)
    target: self.mobject

    从一个点变成mobject

    注意: 这里的一个点本质上是mobject缩小到点的大小
    因为Transfrom的动画需要插值
    不可能真的是一个点
    不过, 只要点集大小一致的mob缩小到一个点似乎都可以
    """
    CONFIG = {
        "point_color": None,
    }

    def __init__(self, mobject: Mobject, point: np.ndarray, **kwargs):
        self.point = point
        super().__init__(mobject, **kwargs)

    def create_target(self) -> Mobject:
        return self.mobject

    def create_starting_mobject(self) -> Mobject:
        start = super().create_starting_mobject()
        """
        下面这两行真是天才！！！
        """
        start.scale(0)
        start.move_to(self.point)
        if self.point_color:
            start.set_color(self.point_color)
        return start


class GrowFromCenter(GrowFromPoint):
    def __init__(self, mobject: Mobject, **kwargs):
        point = mobject.get_center()
        super().__init__(mobject, point, **kwargs)


class GrowFromEdge(GrowFromPoint):
    def __init__(self, mobject: Mobject, edge: np.ndarray, **kwargs):
        point = mobject.get_bounding_box_point(edge)
        super().__init__(mobject, point, **kwargs)


class GrowArrow(GrowFromPoint):
    def __init__(self, arrow: Arrow, **kwargs):
        point = arrow.get_start()
        super().__init__(arrow, point, **kwargs)


class SpinInFromNothing(GrowFromCenter):
    CONFIG = {
        "path_arc": PI,
    }
