from __future__ import annotations

import numpy as np
from typing import Callable

from manimlib.animation.animation import Animation, prepare_animation
from manimlib.mobject.mobject import Group
from manimlib.utils.bezier import integer_interpolate
from manimlib.utils.bezier import interpolate
from manimlib.utils.config_ops import digest_config
from manimlib.utils.iterables import remove_list_redundancies
from manimlib.utils.rate_functions import linear
from manimlib.utils.simple_functions import clip

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.scene.scene import Scene
    from manimlib.mobject.mobject import Mobject


DEFAULT_LAGGED_START_LAG_RATIO = 0.05


"""
c = Circle().set_color(RED)
s = Square().set_color(BLUE)
t = Triangle().set_color(GREEN)
d = Dot().set_color(YELLOW)
animations = [Write(c),
              Write(s),
              Write(t),
              d.animate.shift(LEFT*2)]   

self.play(AnimationGroup(*animations, lag_ratio=1, run_time=4))

ag = AnimationGroup(*animations, lag_ratio=1, run_time=4)
print(ag.group, ag.group.submobjects)

VGroup 
[
<manimlib.mobject.geometry.Circle object at 0x142e17a90>, 
<manimlib.mobject.geometry.Square object at 0x14300f730>, 
<manimlib.mobject.geometry.Triangle object at 0x14300f790>, 
<manimlib.mobject.geometry.Dot object at 0x14300f8e0>
]
"""
class AnimationGroup(Animation):
    '''动画组，可以传入一系列动画，统一播放'''
    CONFIG = {
        # If None, this defaults to the sum of all
        # internal animations
        "run_time": None,
        "rate_func": linear,
        # If 0, all animations are played at once.
        # If 1, all are played successively.
        # If >0 and <1, they start at lagged times
        # from one and other.
        "lag_ratio": 0,
        "group": None,
    }

    def __init__(self, *animations: Animation, **kwargs):
        digest_config(self, kwargs)
        # 动画列表
        self.animations = [prepare_animation(anim) for anim in animations]
        if self.group is None:
            self.group = Group(*remove_list_redundancies(
                [anim.mobject for anim in animations]
            ))
        self.init_run_time()
        Animation.__init__(self, self.group, **kwargs)

    def get_all_mobjects(self) -> Group:
        return self.group

    def begin(self) -> None:
        for anim in self.animations:
            anim.begin()
        # self.init_run_time()

    def finish(self) -> None:
        for anim in self.animations:
            anim.finish()

    def clean_up_from_scene(self, scene: Scene) -> None:
        for anim in self.animations:
            anim.clean_up_from_scene(scene)

    def update_mobjects(self, dt: float) -> None:
        for anim in self.animations:
            anim.update_mobjects(dt)

    def init_run_time(self) -> None:
        """
        动画组的最大执行时间
        """
        self.build_animations_with_timings()
        if self.anims_with_timings:
            self.max_end_time = np.max([
                awt[2] for awt in self.anims_with_timings
            ])
        else:
            self.max_end_time = 0
        if self.run_time is None:
            self.run_time = self.max_end_time

    def build_animations_with_timings(self) -> None:
        """
        Creates a list of triplets of the form
        (anim, start_time, end_time)
        """
        self.anims_with_timings = []
        curr_time = 0
        for anim in self.animations:
            start_time = curr_time
            end_time = start_time + anim.get_run_time()
            self.anims_with_timings.append(
                (anim, start_time, end_time)
            )
            # Start time of next animation is based on
            # the lag_ratio
            """
            秀的头皮发麻
            通过这个函数可以明确lag_ratio的具体含义:
            
            |<------>|:a
            ----------
                  ---------
            |<--->|:b

            lag_ratio = b/a 
            也就是说, 当上一个动画执行了lag_ratio比例的时候
            下一个动画开始执行
            """
            curr_time = interpolate(
                start_time, end_time, self.lag_ratio
            )

    def interpolate(self, alpha: float) -> None:
        # Note, if the run_time of AnimationGroup has been
        # set to something other than its default, these
        # times might not correspond to actual times,
        # e.g. of the surrounding scene.  Instead they'd
        # be a rescaled version.  But that's okay!
        """
        alpha: 整个动画的进度
        sub_alpha: 每一个动画的进度
        可以通过alpha计算出sub_alpha

        alpha * self.max_end_time
               |
               |
        ----------
               -----------
                     -----------    
        |<--------------------->|
              max_end_time
        """
        time = alpha * self.max_end_time
        for anim, start_time, end_time in self.anims_with_timings:
            anim_time = end_time - start_time
            if anim_time == 0:
                sub_alpha = 0
            else:
                sub_alpha = clip(
                    (time - start_time) / anim_time,
                    0, 1
                )
            anim.interpolate(sub_alpha)


"""
c = Circle().set_color(RED)
s = Square().set_color(BLUE)
t = Triangle().set_color(GREEN)
d = Dot().set_color(YELLOW)

animations = [Write(c),
              Write(s),
              Write(t),
              d.animate.shift(LEFT*2)]   

self.play(Succession(*animations))

基本功能是实现了, 但是不明白为什么在动画开始前, 屏幕上已经显示了部分mob
"""
class Succession(AnimationGroup):
    '''使子动画逐一播放'''
    CONFIG = {
        "lag_ratio": 1, #这里即使改成0，各个动画也是依次执行
    }

    def begin(self) -> None:
        assert(len(self.animations) > 0)
        self.init_run_time()
        self.active_animation = self.animations[0]
        self.active_animation.begin()

    def finish(self) -> None:
        self.active_animation.finish()

    def update_mobjects(self, dt: float) -> None:
        self.active_animation.update_mobjects(dt)

    def interpolate(self, alpha: float) -> None:
        index, subalpha = integer_interpolate(
            0, len(self.animations), alpha
        )
        animation = self.animations[index]
        if animation is not self.active_animation:
            self.active_animation.finish()
            animation.begin()
            self.active_animation = animation
        animation.interpolate(subalpha)


"""
c = Circle().set_color(RED)
s = Square().set_color(BLUE)
t = Triangle().set_color(GREEN)
d = Dot().set_color(YELLOW)

animations = [c.animate.shift(DOWN*2),
                s.animate.shift(UP*2),
                t.animate.shift(RIGHT*2),
                d.animate.shift(LEFT*2)]   

self.play(LaggedStart(*animations, lag_ratio=0))
"""
class LaggedStart(AnimationGroup):
    '''可以统一控制 ``lag_ratio`` 的动画组'''
    CONFIG = {
        "lag_ratio": DEFAULT_LAGGED_START_LAG_RATIO, # lag_ratio = 0时，所有动画同时开始
    }


"""
self.play(
        LaggedStart(*(
            dot.animate.set_radius(0.1).set_opacity(self.dot_fade_factor)
            for dot in dots
        ), **kw),
        LaggedStartMap(FadeOut, labels, **kw),
        LaggedStartMap(FadeOut, lines[:2], **kw),
)
"""
"""
self.play(
        LaggedStartMap(
            FadeIn, VGroup(*blocks[10:30]),
            lag_ratio=0.9,
        ),
        run_time=12,
)
"""
class LaggedStartMap(LaggedStart):
    '''统一控制 **动画类**、 ``mobjects``、 ``lag_ratio`` 的动画组'''
    CONFIG = {
        "run_time": 2,
    }

    def __init__(
        self,
        AnimationClass: type,
        mobject: Mobject,
        arg_creator: Callable[[Mobject], tuple] | None = None,
        **kwargs
    ):
        args_list = []
        for submob in mobject:
            if arg_creator:
                args_list.append(arg_creator(submob))
            else:
                args_list.append((submob,))
        anim_kwargs = dict(kwargs)
        if "lag_ratio" in anim_kwargs:
            anim_kwargs.pop("lag_ratio")
        animations = [
            AnimationClass(*args, **anim_kwargs)
            for args in args_list
        ]
        super().__init__(*animations, group=mobject, **kwargs)
