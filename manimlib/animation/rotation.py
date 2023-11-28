from __future__ import annotations

from manimlib.animation.animation import Animation
from manimlib.constants import OUT
from manimlib.constants import PI
from manimlib.constants import TAU
from manimlib.constants import ORIGIN
from manimlib.utils.rate_functions import linear
from manimlib.utils.rate_functions import smooth

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from manimlib.mobject.mobject import Mobject


class Rotating(Animation):
    CONFIG = {
        # "axis": OUT,
        # "radians": TAU,
        "run_time": 5,
        "rate_func": linear,
        "about_point": None,
        "about_edge": None,
        "suspend_mobject_updating": False,
    }

    def __init__(
        self,
        mobject: Mobject,
        angle: float = TAU,
        axis: np.ndarray = OUT,
        **kwargs
    ):
        self.angle = angle
        self.axis = axis
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        for sm1, sm2 in self.get_all_families_zipped():
            sm1.set_points(sm2.get_points())
        self.mobject.rotate(
            alpha * self.angle,
            axis=self.axis,
            about_point=self.about_point,
            about_edge=self.about_edge,
        )


"""
对于旋转来说，一个重要的参数是旋转轴所过的点
about_point和about_edge就是为了确定这个点
当about_point为None, about_edge为ORIGIN的时候
这个固定点就是mob的中心

self.play(
        Rotate(face, 50 * DEGREES, UP),
        rate_func=there_and_back,
        run_time=8,
        )
"""
"""
self.play(
        Rotate(
            mobject = self.radius_line, 
            angle = 2*np.pi-0.001,
            axis = OUT, 
            about_point = self.circle.get_center(),
        ),
        ShowCreation(self.circle),
        *added_anims,
        run_time = 2
        )
"""
"""
rotation_animation = Rotate(
                        mobject=square, 
                        angle=PI/2,
                        axis=OUT,
                        #about_point=ORIGIN+RIGHT+UP
                        about_edge = RIGHT+UP
                        )
"""
class Rotate(Rotating):
    CONFIG = {
        "run_time": 1,
        "rate_func": smooth,
        "about_edge": ORIGIN,
    }

    def __init__(
        self,
        mobject: Mobject,
        angle: float = PI,
        axis: np.ndarray = OUT,
        **kwargs
    ):
        super().__init__(mobject, angle, axis, **kwargs)
