from __future__ import annotations

import math
from typing import Union, Sequence

import numpy as np

from manimlib.constants import *
from manimlib.animation.animation import Animation
from manimlib.animation.movement import Homotopy
from manimlib.animation.composition import AnimationGroup
from manimlib.animation.composition import Succession
from manimlib.animation.creation import ShowCreation
from manimlib.animation.creation import ShowPartial
from manimlib.animation.fading import FadeOut
from manimlib.animation.fading import FadeIn
from manimlib.animation.transform import Transform
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Dot
from manimlib.mobject.shape_matchers import SurroundingRectangle
from manimlib.mobject.shape_matchers import Underline
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.geometry import Line
from manimlib.utils.bezier import interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import there_and_back
from manimlib.utils.rate_functions import wiggle
from manimlib.utils.rate_functions import smooth
from manimlib.utils.rate_functions import squish_rate_func

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import colour
    from manimlib.mobject.mobject import Mobject
    ManimColor = Union[str, colour.Color, Sequence[float]]

"""
大大低估了这份文件的作用！
"""

class FocusOn(Transform):
    CONFIG = {
        "opacity": 0.2,
        "color": GREY,
        "run_time": 2,
        "remover": True,
    }

    def __init__(self, focus_point: np.ndarray, **kwargs):
        self.focus_point = focus_point
        # Initialize with blank mobject, while create_target
        # and create_starting_mobject handle the meat
        super().__init__(VMobject(), **kwargs)

    def create_target(self) -> Dot:
        little_dot = Dot(radius=0)
        little_dot.set_fill(self.color, opacity=self.opacity)
        little_dot.add_updater(
            lambda d: d.move_to(self.focus_point)
        )
        return little_dot

    def create_starting_mobject(self) -> Dot:
        return Dot(
            radius=FRAME_X_RADIUS + FRAME_Y_RADIUS,
            stroke_width=0,
            fill_color=self.color,
            fill_opacity=0,
        )

"""
self.play(Indicate(self.rings[-1]))

尽管简单, 但是很有用
如果我想强调某一局部, 可以用这个
"""
class Indicate(Transform):
    """
    self.play(Indicate(obj2), Indicate(obj1))
    放大，颜色变黄
    恢复原状
    """
    CONFIG = {
        "rate_func": there_and_back,
        "scale_factor": 1.2,
        "color": YELLOW,
    }

    def create_target(self) -> Mobject:
        target = self.mobject.copy()
        target.scale(self.scale_factor)
        target.set_color(self.color)
        return target


"""
class ShowFlash(Scene):
    def construct(self):
        dot = Dot(ORIGIN, color=YELLOW)
        dot.set_stroke(width=0)
        dot.set_fill(opacity=0)
        self.play(Flash(dot, flash_radius=0.8, line_length=0.6, run_time=2))
        self.wait()
"""
class Flash(AnimationGroup):
    CONFIG = {
        "line_length": 0.2,
        "num_lines": 12,
        "flash_radius": 0.3,
        "line_stroke_width": 3,
        "run_time": 1,
    }

    def __init__(
        self,
        point: np.ndarray,
        color: ManimColor = YELLOW,
        **kwargs
    ):
        self.point = point
        self.color = color
        digest_config(self, kwargs)
        self.lines = self.create_lines()
        animations = self.create_line_anims()
        super().__init__(
            *animations,
            group=self.lines,
            **kwargs,
        )

    def create_lines(self) -> VGroup:
        lines = VGroup()
        for angle in np.arange(0, TAU, TAU / self.num_lines):
            line = Line(ORIGIN, self.line_length * RIGHT)
            line.shift((self.flash_radius - self.line_length) * RIGHT)
            line.rotate(angle, about_point=ORIGIN)
            lines.add(line)
        lines.set_stroke(
            color=self.color,
            width=self.line_stroke_width
        )
        lines.add_updater(lambda l: l.move_to(self.point))
        return lines

    def create_line_anims(self) -> list[Animation]:
        return [
            ShowCreationThenDestruction(line)
            for line in self.lines
        ]


class CircleIndicate(Indicate):
    CONFIG = {
        "rate_func": there_and_back,
        "remover": True,
        "circle_config": {
            "color": YELLOW,
        },
    }

    def __init__(self, mobject: Mobject, **kwargs):
        digest_config(self, kwargs)
        circle = self.get_circle(mobject)
        super().__init__(circle, **kwargs)

    def get_circle(self, mobject: Mobject) -> Circle:
        circle = Circle(**self.circle_config)
        circle.add_updater(lambda c: c.surround(mobject))
        return circle

    def interpolate_mobject(self, alpha: float) -> None:
        super().interpolate_mobject(alpha)
        self.mobject.set_stroke(opacity=alpha)


class ShowPassingFlash(ShowPartial):
    CONFIG = {
        "time_width": 0.1,
        "remover": True,
    }

    def get_bounds(self, alpha: float) -> tuple[float, float]:
        tw = self.time_width
        upper = interpolate(0, 1 + tw, alpha)
        lower = upper - tw
        upper = min(upper, 1)
        lower = max(lower, 0)
        return (lower, upper)

    def finish(self) -> None:
        super().finish()
        for submob, start in self.get_all_families_zipped():
            submob.pointwise_become_partial(start, 0, 1)


"""
plane = NumberPlane()
self.add(plane)

points = [[-1, -1, 0],
            [0, 1, 0],
            [2, 1, 0],
            [3, 4, 0]]
curve = VMobject().set_points_smoothly(points, True).set_stroke(YELLOW, 5)

self.play(VShowPassingFlash(Circle().scale(2), time_width=1, run_time=2))
self.play(VShowPassingFlash(curve, time_width=1, run_time=2))
"""
"""
class test(Scene):
	def construct(self): 
		plane = NumberPlane()
		self.add(plane)

		points = [[-2, -3, 0],
			      [0, 0, 0],
				  [2, 1, 0],
				  [3, 3, 0]]
		line = VMobject().set_points_smoothly(points, True).set_stroke(YELLOW, 5)	
		
		self.add(line)
		for point in points:
			dot = Dot(point)
			self.add(dot)

		rgbas = [
				 [0.95882272, 0.0277352,  0.061623,   1.        ],
                 [0.03781613, 0.96890806, 0.05165273, 1.        ],
                 [0.0795209,  0.03976045, 0.90007538, 1.        ],
				 ]
		line.set_rgba_array(rgbas, "stroke_rgba")
		line.set_stroke(width=[20,10.5,1, 
						       1,9.5,18,
							   18,9.5,1,
							   1,10.5,20, 
						       20,11,2,
							   2,9.5,17])	

		print(len(line.get_points())//3) #6
"""
"""
一个猜想:
整个曲线分为6段, 每一段的stroke渲染的时候都会从rgbas和width数组拿到属于自己的颜色和线宽
每一段的首尾像素都会得到自己的颜色和线宽, 中间部分会插值

困惑:每一段衔接处有些不自然(width变化有点突兀), 需要进一步研究stroke部分的着色器代码
解答:需要为每一段曲线需要3个width值, 且上一段width的末尾和后一段width的开始要相等
"""
"""
self.play(
    Write(circ_label),
    VShowPassingFlash(
        vslices[2].copy().set_stroke(YELLOW, 5).insert_n_curves(20),
        time_width=1.5,
        run_time=1.5,
    ),
    vslices[2].animate.set_color(YELLOW),
)
"""
"""
self.play(*(
    LaggedStart(*(
        VShowPassingFlash(piece, time_width=2)
        for piece in group.copy().set_fill(opacity=0).set_stroke(RED, 5)
    ), lag_ratio=0.02, run_time=4)
    for group in [laid_sectors, sectors]
))
"""
class VShowPassingFlash(Animation):
    """
    这个animation用在了StreamLines上
    
    作用于vmob的时候, 使得vmob部分可见
    """
    CONFIG = {
        "time_width": 0.3,
        "taper_width": 0.02,
        "remover": True,
    }

    def begin(self) -> None:
        # 需要认识到每一条曲线都是由多段拼成, 每一段都可以设置不同的width
        #print(self.mobject.data["stroke_width"])
        self.mobject.align_stroke_width_data_to_points()
        #print(self.mobject.data["stroke_width"])

        # Compute an array of stroke widths for each submobject
        # which tapers out at either end
        self.submob_to_anchor_widths = dict()
        #print(self.mobject.get_family())
        for sm in self.mobject.get_family():
            original_widths = sm.get_stroke_widths()
            anchor_widths = np.array([*original_widths[0::3], original_widths[-1]])

            def taper_kernel(x):
                if x < self.taper_width:
                    return x
                elif x > 1 - self.taper_width:
                    return 1.0 - x
                return 1.0

            taper_array = list(map(taper_kernel, np.linspace(0, 1, len(anchor_widths))))
            self.submob_to_anchor_widths[hash(sm)] = anchor_widths * taper_array
        super().begin()

    def interpolate_submobject(
        self,
        submobject: VMobject,
        starting_sumobject: None,
        alpha: float
    ) -> None:
        anchor_widths = self.submob_to_anchor_widths[hash(submobject)]
        # Create a gaussian such that 3 sigmas out on either side
        # will equals time_width
        tw = self.time_width
        # 正太分布的均值和方差都和tw有关
        sigma = tw / 6
        mu = interpolate(-tw / 2, 1 + tw / 2, alpha)

        # genius
        def gauss_kernel(x):
            if abs(x - mu) > 3 * sigma:
                return 0
            z = (x - mu) / sigma
            return math.exp(-0.5 * z * z)

        """
        这里的命名很好anchor_widths
        genius
        """
        kernel_array = list(map(gauss_kernel, np.linspace(0, 1, len(anchor_widths))))
        scaled_widths = anchor_widths * kernel_array

        new_widths = np.zeros(submobject.get_num_points())
        """
        new_widths是mob的点集的数目, len(new_widths) // 3就是贝塞尔曲线的数目
        """
        new_widths[0::3] = scaled_widths[:-1]
        new_widths[2::3] = scaled_widths[1:]
        new_widths[1::3] = (new_widths[0::3] + new_widths[2::3]) / 2
        """
        当submob的点集大小为18的时候
        len(new_widths) == 18
        len(scaled_widths) == 7 (anchor的width, 重复的anchor算一个)
        """
        """
        动画的效果就是line的部分可见

        通过设置线宽, 使得部分line可见
        """
        submobject.set_stroke(width=new_widths)

    def finish(self) -> None:
        super().finish()
        for submob, start in self.get_all_families_zipped():
            submob.match_style(start)


class FlashAround(VShowPassingFlash):
    """
    mob外围flash
    """
    CONFIG = {
        "stroke_width": 4.0,
        "color": YELLOW,
        "buff": SMALL_BUFF,
        "time_width": 1.0,
        "n_inserted_curves": 20,
    }

    def __init__(self, mobject: Mobject, **kwargs):
        digest_config(self, kwargs)
        path = self.get_path(mobject)
        if mobject.is_fixed_in_frame:
            path.fix_in_frame()
        path.insert_n_curves(self.n_inserted_curves)
        path.set_points(path.get_points_without_null_curves())
        path.set_stroke(self.color, self.stroke_width)
        super().__init__(path, **kwargs)

    def get_path(self, mobject: Mobject) -> SurroundingRectangle:
        return SurroundingRectangle(mobject, buff=self.buff)


class FlashUnder(FlashAround):
    def get_path(self, mobject: Mobject) -> Underline:
        return Underline(mobject, buff=self.buff)


class ShowCreationThenDestruction(ShowPassingFlash):
    CONFIG = {
        "time_width": 2.0,
        "run_time": 1,
    }


class ShowCreationThenFadeOut(Succession):
    CONFIG = {
        "remover": True,
    }

    def __init__(self, mobject: Mobject, **kwargs):
        super().__init__(
            ShowCreation(mobject),
            FadeOut(mobject),
            **kwargs
        )


class AnimationOnSurroundingRectangle(AnimationGroup):
    CONFIG = {
        "surrounding_rectangle_config": {},
        # Function which takes in a rectangle, and spits
        # out some animation.  Could be some animation class,
        # could be something more
        "rect_animation": Animation
    }

    def __init__(self, mobject: Mobject, **kwargs):
        digest_config(self, kwargs)
        if "surrounding_rectangle_config" in kwargs:
            kwargs.pop("surrounding_rectangle_config")
        self.mobject_to_surround = mobject

        rect = self.get_rect()
        rect.add_updater(lambda r: r.move_to(mobject))

        super().__init__(
            self.rect_animation(rect, **kwargs),
        )

    def get_rect(self) -> SurroundingRectangle:
        return SurroundingRectangle(
            self.mobject_to_surround,
            **self.surrounding_rectangle_config
        )


class ShowPassingFlashAround(AnimationOnSurroundingRectangle):
    CONFIG = {
        "rect_animation": ShowPassingFlash
    }


class ShowCreationThenDestructionAround(AnimationOnSurroundingRectangle):
    CONFIG = {
        "rect_animation": ShowCreationThenDestruction
    }


class ShowCreationThenFadeAround(AnimationOnSurroundingRectangle):
    CONFIG = {
        "rect_animation": ShowCreationThenFadeOut
    }

"""genius!
self.play(
    ApplyWave(self.rings, amplitude = 0.1),
    Animation(self.radius_group),
    Animation(alt_side_brace),
    Animation(alt_dr_label),
    run_time = 3,
    lag_ratio = 0.5
)
整个圆环长生了波纹的效果

from manimlib import *
class test(Scene):
    def construct(self):
        square = Square()

        # Apply a wave animation to the square
        self.play(ApplyWave(square, amplitude=0.5, direction=UP))

        self.wait(2)
"""
class ApplyWave(Homotopy):
    CONFIG = {
        "direction": UP,
        "amplitude": 0.2,
        "run_time": 1,
    }

    def __init__(self, mobject: Mobject, **kwargs):
        digest_config(self, kwargs, locals())
        left_x = mobject.get_left()[0]
        right_x = mobject.get_right()[0]
        vect = self.amplitude * self.direction

        def homotopy(x, y, z, t):
            alpha = (x - left_x) / (right_x - left_x)
            power = np.exp(2.0 * (alpha - 0.5))
            nudge = there_and_back(t**power)
            return np.array([x, y, z]) + nudge * vect

        super().__init__(homotopy, mobject, **kwargs)


"""
self.play(
    ShowCreation(edge),
    Write(q_marks),
)
self.play(WiggleOutThenIn(edge, run_time=1))

先出现了一条line
然后line轻微抖动
"""
class WiggleOutThenIn(Animation):
    CONFIG = {
        "scale_value": 1.1,
        "rotation_angle": 0.01 * TAU,
        "n_wiggles": 6,
        "run_time": 2,
        "scale_about_point": None,
        "rotate_about_point": None,
    }

    def get_scale_about_point(self) -> np.ndarray:
        if self.scale_about_point is None:
            return self.mobject.get_center()

    def get_rotate_about_point(self) -> np.ndarray:
        if self.rotate_about_point is None:
            return self.mobject.get_center()

    def interpolate_submobject(
        self,
        submobject: Mobject,
        starting_sumobject: Mobject,
        alpha: float
    ) -> None:
        submobject.match_points(starting_sumobject)
        submobject.scale(
            interpolate(1, self.scale_value, there_and_back(alpha)),
            about_point=self.get_scale_about_point()
        )
        submobject.rotate(
            wiggle(alpha, self.n_wiggles) * self.rotation_angle,
            about_point=self.get_rotate_about_point()
        )


class TurnInsideOut(Transform):
    CONFIG = {
        "path_arc": TAU / 4,
    }

    def create_target(self) -> Mobject:
        return self.mobject.copy().reverse_points()


class FlashyFadeIn(AnimationGroup):
    CONFIG = {
        "fade_lag": 0,
    }

    def __init__(self, vmobject: VMobject, stroke_width: float = 2, **kwargs):
        digest_config(self, kwargs)
        outline = vmobject.copy()
        outline.set_fill(opacity=0)
        outline.set_stroke(width=stroke_width, opacity=1)

        rate_func = kwargs.get("rate_func", smooth)
        super().__init__(
            FadeIn(vmobject, rate_func=squish_rate_func(rate_func, self.fade_lag, 1)),
            VShowPassingFlash(outline, time_width=1),
            **kwargs
        )
