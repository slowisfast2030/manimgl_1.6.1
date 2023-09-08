from __future__ import annotations

from typing import Callable

import numpy as np

from manimlib.constants import BLUE_D
from manimlib.constants import BLUE_B
from manimlib.constants import BLUE_E
from manimlib.constants import GREY_BROWN
from manimlib.constants import WHITE
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.utils.rate_functions import smooth


"""
screen_rect = ScreenRectangle()
self.add(AnimatedBoundary(screen_rect, colors=[RED, YELLOW, GREEN]))
self.add(20)

效果: screen_rect的边界从红色到黄色到绿色, 然后再从绿色到红色, 循环往复
"""
class AnimatedBoundary(VGroup):
    '''
    动态变化的边界
    '''
    CONFIG = {
        "colors": [BLUE_D, BLUE_B, BLUE_E, GREY_BROWN],
        "max_stroke_width": 3,
        "cycle_rate": 0.5,
        "back_and_forth": True,
        "draw_rate_func": smooth,
        "fade_rate_func": smooth,
    }

    def __init__(self, vmobject: VMobject, **kwargs):
        '''
        传入需要显示动态边界的物体 ``vmobject``
    
        - ``colors`` 表示变化中出现的颜色
        - ``max_stroke_width`` 表示边界最大的粗细
        - ``cycle_rate`` 表示循环率
        '''
        super().__init__(**kwargs)
        self.vmobject: VMobject = vmobject
        self.boundary_copies: list[VMobject] = [
            vmobject.copy().set_style(
                stroke_width=0,
                fill_opacity=0
            )
            for x in range(2)
        ]
        self.add(*self.boundary_copies)
        self.total_time: float = 0
        self.add_updater(
            lambda m, dt: self.update_boundary_copies(dt)
        )

    def update_boundary_copies(self, dt: float) -> None:
        # Not actual time, but something which passes at
        # an altered rate to make the implementation below
        # cleaner
        time = self.total_time * self.cycle_rate
        growing, fading = self.boundary_copies
        colors = self.colors
        msw = self.max_stroke_width
        vmobject = self.vmobject

        index = int(time % len(colors))
        alpha = time % 1
        draw_alpha = self.draw_rate_func(alpha)
        fade_alpha = self.fade_rate_func(alpha)

        if self.back_and_forth and int(time) % 2 == 1:
            bounds = (1 - draw_alpha, 1)
        else:
            bounds = (0, draw_alpha)
        self.full_family_become_partial(growing, vmobject, *bounds)
        growing.set_stroke(colors[index], width=msw)

        if time >= 1:
            self.full_family_become_partial(fading, vmobject, 0, 1)
            fading.set_stroke(
                color=colors[index - 1],
                width=(1 - fade_alpha) * msw
            )

        self.total_time += dt

    def full_family_become_partial(
        self,
        mob1: VMobject,
        mob2: VMobject,
        a: float,
        b: float
    ):
        family1 = mob1.family_members_with_points()
        family2 = mob2.family_members_with_points()
        for sm1, sm2 in zip(family1, family2):
            sm1.pointwise_become_partial(sm2, a, b)
        return self


"""
c = Dot()
p = TracedPath(c.get_center, stroke_color=TEAL, time_traced=1)
self.add(c, p)
self.play(c.animate.shift(200 * RIGHT), run_time=20)
"""
class TracedPath(VMobject):
    '''
    记录路径的 VMobject
    '''
    CONFIG = {
        "stroke_width": 2,
        "stroke_color": WHITE,
        "time_traced": np.inf,
        "fill_opacity": 0,
        "time_per_anchor": 1 / 15,
    }

    def __init__(self, traced_point_func: Callable[[], np.ndarray], **kwargs):
        '''
        传入一个可调用的对象 ``traced_point_func`` (一般为 ``mob.get_center`` )

        - ``min_distance_to_new_point`` : 两点之间的最小距离，若小于此距离则不增加点
        - ``time_traced`` : 追踪时间
        - ``time_per_anchor`` : 采样时间间隔
        '''
        super().__init__(**kwargs)
        self.traced_point_func = traced_point_func # 一般为 ``mob.get_center``
        self.time: float = 0
        self.traced_points: list[np.ndarray] = []
        self.add_updater(lambda m, dt: m.update_path(dt))

    def update_path(self, dt: float):
        if dt == 0:
            return self
        # traced_point_func一般为mob.get_center，所以这里是mob.get_center().copy()
        point = self.traced_point_func().copy()
        self.traced_points.append(point)

        if self.time_traced < np.inf:
            n_relevant_points = int(self.time_traced / dt + 0.5)
            # n_anchors = int(self.time_traced / self.time_per_anchor)
            n_tps = len(self.traced_points)
            if n_tps < n_relevant_points:
                points = self.traced_points + [point] * (n_relevant_points - n_tps)
            else:
                points = self.traced_points[n_tps - n_relevant_points:]
            # points = [
            #     self.traced_points[max(n_tps - int(alpha * n_relevant_points) - 1, 0)]
            #     for alpha in np.linspace(1, 0, n_anchors)
            # ]
            # Every now and then refresh the list
            if n_tps > 10 * n_relevant_points:
                self.traced_points = self.traced_points[-n_relevant_points:]
        else:
            # sparseness = max(int(self.time_per_anchor / dt), 1)
            # points = self.traced_points[::sparseness]
            # points[-1] = self.traced_points[-1]
            points = self.traced_points

        if points:
            self.set_points_smoothly(points)

        self.time += dt
        return self


class TracingTail(TracedPath):
    '''
    自动减淡的轨迹
    
    需要注意：
    stroke_width和stroke_opacity的默认参数是tuple
    执行会报错
    '''
    CONFIG = {
        "stroke_width": (0, 3),
        "stroke_opacity": (0, 1),
        "stroke_color": WHITE,
        "time_traced": 1.0,
    }

    def __init__(
        self,
        mobject_or_func: Mobject | Callable[[], np.ndarray],
        **kwargs
    ):
        """传入一个 ``Mobject`` 或者一个可调用的对象 ``func``（如 ``line.get_end``），追踪其运动轨迹"""
        if isinstance(mobject_or_func, Mobject):
            func = mobject_or_func.get_center
        else:
            func = mobject_or_func
        super().__init__(func, **kwargs)
