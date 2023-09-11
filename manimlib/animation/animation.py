from __future__ import annotations

from copy import deepcopy
from typing import Callable

from manimlib.mobject.mobject import _AnimationBuilder
from manimlib.mobject.mobject import Mobject
from manimlib.utils.config_ops import digest_config
from manimlib.utils.rate_functions import smooth
from manimlib.utils.simple_functions import clip

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.scene.scene import Scene


DEFAULT_ANIMATION_RUN_TIME = 1.0
DEFAULT_ANIMATION_LAG_RATIO = 0

"""
c = Circle().set_color(RED)
s = Square().set_color(BLUE)
t = Triangle().set_color(GREEN)
c.add(s, t)
self.play(ShowCreation(c, lag_ratio=0, run_time=3))
print("\n", "-"*100)
print(c.submobjects)
print("-"*100)

有关lag_ratio的思考:
1.如果lag_ratio=0, 那么所有的submobject的alpha值都是一样的。如果整个动画的时间固定, 那么每一个submobject的动画时间比较长

2.如果lag_ratio=1, 那么所有的submobject的alpha值都是不一样的。如果整个动画的时间固定, 那么每一个submobject的动画时间比较短
以上面的代码为例
lag_ratio=1时, 每个submobject的动画时间是1
lag_ratio=0时, 每个submobject的动画时间是3

3.当lag_ratio=0时, 每一个submobject看上去是同时完成的, 那么是并行的吗?
其实并不是, 具体执行时是通过for循环, 仍然是串行的
因为是一帧帧渲染的
渲染每一帧的时候, 是按照submobject的顺序来的
播放的时候，是播放渲染完成的帧
所以看上去是同时完成的
"""

"""
alpha --> rate_func(alpha) --> lag_ratio(rate_func(alpha))
"""
class Animation(object):
    CONFIG = {
        "run_time": DEFAULT_ANIMATION_RUN_TIME,
        "rate_func": smooth,
        "name": None,
        # Does this animation add or remove a mobject form the screen
        "remover": False,
        # What to enter into the update function upon completion
        "final_alpha_value": 1,
        # If 0, the animation is applied to all submobjects
        # at the same time
        # If 1, it is applied to each successively.
        # If 0 < lag_ratio < 1, its applied to each
        # with lagged start times
        "lag_ratio": DEFAULT_ANIMATION_LAG_RATIO,
        "suspend_mobject_updating": True,
    }

    def __init__(self, mobject: Mobject, **kwargs):
        assert(isinstance(mobject, Mobject))
        digest_config(self, kwargs)
        self.mobject = mobject

    def __str__(self) -> str:
        if self.name:
            return self.name
        return self.__class__.__name__ + str(self.mobject)

    def begin(self) -> None:
        # This is called right as an animation is being
        # played.  As much initialization as possible,
        # especially any mobject copying, should live in
        # this method
        self.starting_mobject = self.create_starting_mobject()
        # 如果一个mob同时具有updater和animation，那么它的updater会在这里被暂停
        # 相对应的，在fininsh函数中会恢复updater
        if self.suspend_mobject_updating:
            # All calls to self.mobject's internal updaters
            # during the animation, either from this Animation
            # or from the surrounding scene, should do nothing.
            # It is, however, okay and desirable to call
            # the internal updaters of self.starting_mobject,
            # or any others among self.get_all_mobjects()
            self.mobject.suspend_updating()
        self.families = list(self.get_all_families_zipped())
        self.interpolate(0)

    def finish(self) -> None:
        self.interpolate(self.final_alpha_value)
        # 恢复updater
        if self.suspend_mobject_updating:
            self.mobject.resume_updating()

    def clean_up_from_scene(self, scene: Scene) -> None:
        if self.is_remover():
            scene.remove(self.mobject)

    def create_starting_mobject(self) -> Mobject:
        # Keep track of where the mobject starts
        # 一直没有搞明白这里是浅拷贝还是深拷贝
        return self.mobject.copy()

    def get_all_mobjects(self) -> tuple[Mobject, Mobject]:
        """
        Ordering must match the ording of arguments to interpolate_submobject
        """
        return self.mobject, self.starting_mobject

    def get_all_families_zipped(self) -> zip[tuple[Mobject]]:
        return zip(*[
            mob.get_family()
            for mob in self.get_all_mobjects()
        ])

    """
    在manim中, animation和updater是两个不同的概念

    但是都会对mobject的属性进行修改

    animation的修改是通过插值实现的
    updater的修改是通过调用mobject的update方法实现的
    """
    def update_mobjects(self, dt: float) -> None:
        """
        Updates things like starting_mobject, and (for
        Transforms) target_mobject.  Note, since typically
        (always?) self.mobject will have its updating
        suspended during the animation, this will do
        nothing to self.mobject.
        """
        for mob in self.get_all_mobjects_to_update():
            mob.update(dt)

    def get_all_mobjects_to_update(self) -> list[Mobject]:
        # The surrounding scene typically handles
        # updating of self.mobject.  Besides, in
        # most cases its updating is suspended anyway
        return list(filter(
            lambda m: m is not self.mobject,
            self.get_all_mobjects()
        ))

    def copy(self):
        return deepcopy(self)

    def update_config(self, **kwargs):
        digest_config(self, kwargs)
        return self

    # Methods for interpolation, the mean of an Animation
    def interpolate(self, alpha: float) -> None:
        """
        给定alpha值, 就可以渲染对应的帧
        1s可以15帧, 30帧, 60帧等
        """
        alpha = clip(alpha, 0, 1)
        # rate_func作用于alpha
        # 最好的例子是there_and_back这个速率函数
        self.interpolate_mobject(self.rate_func(alpha))

    def update(self, alpha: float) -> None:
        """
        This method shouldn't exist, but it's here to
        keep many old scenes from breaking
        """
        self.interpolate(alpha)

    def interpolate_mobject(self, alpha: float) -> None:
        for i, mobs in enumerate(self.families):
            sub_alpha = self.get_sub_alpha(alpha, i, len(self.families))
            """
            严格来讲, 下面这个函数的名字取得不好
            在manim中, submobjects和family是两个不同的属性
            family比submobjects多一个mob自身
            """
            self.interpolate_submobject(*mobs, sub_alpha)

    def interpolate_submobject(
        self,
        submobject: Mobject,
        starting_submobject: Mobject,
        alpha: float
    ):
        # Typically ipmlemented by subclass
        pass

    def get_sub_alpha(
        self,
        alpha: float,
        index: int,
        num_submobjects: int
    ) -> float:
        # TODO, make this more understanable, and/or combine
        # its functionality with AnimationGroup's method
        # build_animations_with_timings
        """
        计算每个submobject的alpha值

        一个mob的animation是由多个submobject的animation组成的
        由于一些参数设置(比如lag_ratio), 每个submobject的animation的alpha值是不同的
        """
        lag_ratio = self.lag_ratio
        full_length = (num_submobjects - 1) * lag_ratio + 1
        value = alpha * full_length
        lower = index * lag_ratio
        return clip((value - lower), 0, 1)

    # Getters and setters
    def set_run_time(self, run_time: float):
        self.run_time = run_time
        return self

    def get_run_time(self) -> float:
        return self.run_time

    def set_rate_func(self, rate_func: Callable[[float], float]):
        self.rate_func = rate_func
        return self

    def get_rate_func(self) -> Callable[[float], float]:
        return self.rate_func

    def set_name(self, name: str):
        self.name = name
        return self

    def is_remover(self) -> bool:
        return self.remover


def prepare_animation(anim: Animation | _AnimationBuilder):
    if isinstance(anim, _AnimationBuilder):
        return anim.build()

    if isinstance(anim, Animation):
        return anim

    raise TypeError(f"Object {anim} cannot be converted to an animation")
