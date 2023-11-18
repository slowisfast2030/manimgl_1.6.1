from __future__ import annotations

from typing import Callable, Sequence

from manimlib.animation.animation import Animation
from manimlib.utils.rate_functions import linear

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np
    from manimlib.mobject.mobject import Mobject


"""
test_homotopy1 = lambda x, y, z, t: (
			x + interpolate(-3, 3, 2*t if t<=0.5 else 1),     # First 5 Seconds
			y + interpolate(0, 3, 2*(t-0.5) if t>0.5 else 0), # Next 5 Seconds
			z)

test_homotopy2 = lambda x, y, z, t: (
			x + interpolate(-3, 3, 4*t if t<=0.25 else 1) 
				+ interpolate(3, -3, 4*(t-0.5) if (t>=0.5 and t<=0.75) else (0 if t<=0.5 else 1)), 
			y + interpolate(-3, 3, 4*(t-0.25) if (t>0.25 and t<0.5) else (0 if t<=0.25 else 1)) 
				+ interpolate(3, -3, 4*(t-0.75) if (t>0.75) else (0 if t<=0.75 else 1)), 
			z)

self.play(Homotopy(test_homotopy1, obj2, run_time=10, rate_func=linear))
"""

"""
pi_creature = PiCreature(color = PINK).scale(0.5)
pi_creature.shift(-pi_creature.get_corner(DOWN+LEFT))
self.plane.prepare_for_nonlinear_transform()

self.play(ShowCreation(
    self.plane,
    run_time = 2
))
self.play(FadeIn(pi_creature))
self.play(Blink(pi_creature))
self.plane.add(pi_creature)
self.play(Homotopy(plane_wave_homotopy, self.plane, run_time = 3))
self.wait(2)
self.apply_matrix([[2, 1], [1, 2]])
self.wait()
"""
class Homotopy(Animation):
    CONFIG = {
        "run_time": 3,
        "apply_function_kwargs": {},
    }

    def __init__(
        self,
        homotopy: Callable[[float, float, float, float], Sequence[float]],
        mobject: Mobject,
        **kwargs
    ):
        """
        Homotopy is a function from
        (x, y, z, t) to (x', y', z')
        """
        """
        homotopy 是一个从 (x, y, z, t) 到 (x', y', z') 的函数
        t 的取值范围是 [0, 1]
        让 mobject 根据 homotopy 计算的每个点坐标进行变换
        例子中 t = 0 时 mob 是边长为 0 的正方形
        t = 1 时是边长为 2 的正方形
        与 Transform 类似，区别在于 Transform 锚点运动轨迹是直线
        Homotopy 锚点运动轨迹是根据传入的 homotopy 计算的
        """
        self.homotopy = homotopy
        super().__init__(mobject, **kwargs)

    def function_at_time_t(
        self,
        t: float
    ) -> Callable[[np.ndarray], Sequence[float]]:
        return lambda p: self.homotopy(*p, t)

    def interpolate_submobject(
        self,
        submob: Mobject,
        start: Mobject,
        alpha: float
    ) -> None:
        """
        alpha是时间进程，不是动画进程
        两者之间的纽带：rate_func
        """
        submob.match_points(start)
        submob.apply_function(
            self.function_at_time_t(alpha),
            **self.apply_function_kwargs
        )


class SmoothedVectorizedHomotopy(Homotopy):
    CONFIG = {
        "apply_function_kwargs": {"make_smooth": True}, # mob.apply_function(**kwargs)似乎没有make_smooth参数
    }


class ComplexHomotopy(Homotopy):
    def __init__(
        self,
        complex_homotopy: Callable[[complex, float], Sequence[float]],
        mobject: Mobject,
        **kwargs
    ):
        """
        Given a function form (z, t) -> w, where z and w
        are complex numbers and t is time, this animates
        the state over time
        """
        def homotopy(x, y, z, t):
            c = complex_homotopy(complex(x, y), t)
            return (c.real, c.imag, z)
        super().__init__(homotopy, mobject, **kwargs)


class PhaseFlow(Animation):
    CONFIG = {
        "virtual_time": 1,
        "rate_func": linear,
        "suspend_mobject_updating": False,
    }

    def __init__(
        self,
        function: Callable[[np.ndarray], np.ndarray],
        mobject: Mobject,
        **kwargs
    ):
        self.function = function
        super().__init__(mobject, **kwargs)

    """
    updater的参数是dt，即帧之间的时间间隔
    见过将dt改为alpha的
    这里是将alpha改为dt
    """
    def interpolate_mobject(self, alpha: float) -> None:
        #print(self.virtual_time)
        if hasattr(self, "last_alpha"):
            dt = self.virtual_time * (alpha - self.last_alpha)
            self.mobject.apply_function(
                lambda p: p + dt * self.function(p)
            )
        self.last_alpha = alpha


class MoveAlongPath(Animation):
    CONFIG = {
        "suspend_mobject_updating": False,
    }

    def __init__(self, mobject: Mobject, path: Mobject, **kwargs):
        self.path = path
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        point = self.path.point_from_proportion(alpha)
        self.mobject.move_to(point)
