from __future__ import annotations
from collections.abc import Iterable

import random

from manimlib.animation.transform import ReplacementTransform
from manimlib.animation.transform import Transform
from manimlib.animation.transform import ApplyMethod
from manimlib.animation.transform import ApplyPointwiseFunction

from manimlib.animation.composition import LaggedStart
from manimlib.animation.fading import FadeIn
from manimlib.animation.fading import FadeTransform
from manimlib.constants import *
from manimlib.mobject.mobject import Group
from manimlib.mobject.frame import ScreenRectangle
from manimlib.mobject.frame import FullScreenFadeRectangle
from manimlib.mobject.svg.drawings import SpeechBubble
from manimlib.mobject.svg.drawings import ThoughtBubble
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.scene.interactive_scene import InteractiveScene # 潜在风险
from manimlib.scene.scene import Scene
from manimlib.utils.rate_functions import squish_rate_func
from manimlib.utils.rate_functions import there_and_back
from manimlib.utils.space_ops import get_norm

from custom.characters.pi_creature import Mortimer
from custom.characters.pi_creature import PiCreature
from custom.characters.pi_creature import Randolph

from custom.characters.pi_creature_animations import Blink
from custom.characters.pi_creature_animations import PiCreatureBubbleIntroduction
from custom.characters.pi_creature_animations import RemovePiCreatureBubble

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from manimlib.typing import ManimColor, Vect3


"""
InteractiveScene有很多未解决问题, 暂时用Scene代替 

几个有意思的问题:
1.我这个manimgl版本是tag1.6.1, manimlib文件夹下是没有interactive_scene.py文件的
然而3b1b的视频代码(几个pi生物)却需要
2.interactive_scene.py文件主要增加的功能是交互, 可以通过鼠标和键盘控制屏幕中的mob
3.在早期的manimlib版本(cairo), PiCreatureScene直接继承于Scene 
"""
"""
看了PiCreatureScene的源码
发现主要用到了Scene.play方法
和InteractiveScene关系不大
"""
#class PiCreatureScene(InteractiveScene):
"""
对PiCreatureScene的进一步理解
最基本的Scene是一个空白的场景, 什么都没有
提供了self.add()方法, 可以添加mob
提供了self.play()方法, 可以播放动画

对于PiCreatureScene, 主要是默认添加了pi生物
以及一些和pi生物有关的方法
"""
class PiCreatureScene(Scene):
    total_wait_time: float = 0
    seconds_to_blink: float = 3
    pi_creatures_start_on_screen: bool = True
    default_pi_creature_kwargs: dict = dict(
        color=BLUE,
        flip_at_start=False,
    )
    default_pi_creature_start_corner: Vect3 = DL

    def setup(self):
        """
        setup()方法是先于construct()方法执行
        将pi生物创建的代码放在setup()方法
        意味着在construct()方法中已经有了pi生物
        """
        super().setup()
        self.pi_creatures = VGroup(*self.create_pi_creatures())
        self.pi_creature = self.get_primary_pi_creature()
        if self.pi_creatures_start_on_screen:
            self.add(*self.pi_creatures)

    def create_pi_creatures(self) -> VGroup | Iterable[PiCreature]:
        """
        Likely updated for subclasses
        """
        """
        只返回一个pi生物, 这里为何要放入列表?
        因为这个方法会被子类覆盖
        """
        return [self.create_pi_creature()]

    def create_pi_creature(self) -> PiCreature:
        pi_creature = PiCreature(**self.default_pi_creature_kwargs)
        pi_creature.to_corner(self.default_pi_creature_start_corner)
        return pi_creature

    def get_pi_creatures(self) -> VGroup:
        return self.pi_creatures

    def get_primary_pi_creature(self) -> PiCreature:
        return self.pi_creatures[0]

    def any_pi_creatures_on_screen(self):
        return len(self.get_on_screen_pi_creatures()) > 0

    def get_on_screen_pi_creatures(self):
        """
        获取在屏幕上的pi生物
        """
        mobjects = self.get_mobject_family_members()
        return VGroup(*(
            pi for pi in self.get_pi_creatures()
            if pi in mobjects
        ))

    def pi_changes(self, *modes, look_at=None, lag_ratio=0.5, run_time=1):
        """
        class Pi(PiCreatureScene):
            def construct(self):
                modes = ['sassy', 'happy', 'hooray']
                self.play(self.pi_changes(*modes, run_time=3))  

        从实际的执行效果来看, pi生物只会换一种表情
        根源在于:
        for pi, mode in zip(self.pi_creatures, modes)
        self.pi_creatures是只有一个元素的列表
        modes是有三个元素的列表 
        """
        return LaggedStart(
            *(
                pi.change(mode, look_at)
                for pi, mode in zip(self.pi_creatures, modes)
                if mode is not None
            ),
            lag_ratio=lag_ratio,
            run_time=run_time
        )

    def introduce_bubble(
        self,
        pi_creature,
        content,
        bubble_type=SpeechBubble,
        target_mode=None,
        look_at=None,
        bubble_config=dict(),
        bubble_removal_kwargs=dict(),
        added_anims=[],
        **kwargs
    ):
        """
        self.introduce_bubble(pi_creature=self.pi_creature, 
                              content="To be or not to be, that is a question",
                              bubble_type=ThoughtBubble,
                              target_mode="thinking")

        在方法里调用了play方法
        """
        if target_mode is None:
            target_mode = "thinking" if bubble_type is ThoughtBubble else "speaking"

        anims = []
        on_screen_mobjects = self.get_mobject_family_members()

        pi_creatures_with_bubbles = [
            pi for pi in self.get_pi_creatures()
            if pi.bubble in on_screen_mobjects
        ]
        if pi_creature in pi_creatures_with_bubbles:
            pi_creatures_with_bubbles.remove(pi_creature)
            old_bubble = pi_creature.bubble
            bubble = pi_creature.get_bubble(
                content,
                bubble_type=bubble_type,
                **bubble_config
            )
            anims += [
                ReplacementTransform(old_bubble, bubble),
                FadeTransform(old_bubble.content, bubble.content),
                pi_creature.change(target_mode, look_at)
            ]
        else:
            anims.append(PiCreatureBubbleIntroduction(
                pi_creature,
                content,
                target_mode=target_mode,
                bubble_type=bubble_type,
                bubble_config=bubble_config,
                **kwargs
            ))
        anims += [
            RemovePiCreatureBubble(pi, **bubble_removal_kwargs)
            for pi in pi_creatures_with_bubbles
        ]
        anims += added_anims

        self.play(*anims, **kwargs)

    def pi_creature_says(self, pi_creature, content, **kwargs):
        self.introduce_bubble(pi_creature, content, bubble_type=SpeechBubble, **kwargs)

    def pi_creature_thinks(self, pi_creature, content, **kwargs):
        self.introduce_bubble(pi_creature, content, bubble_type=ThoughtBubble, **kwargs)

    def say(self, content, **kwargs):
        self.pi_creature_says(self.get_primary_pi_creature(), content, **kwargs)

    def think(self, content, **kwargs):
        self.pi_creature_thinks(self.get_primary_pi_creature(), content, **kwargs)

    def anims_from_play_args(self, *args, **kwargs):
        """
        Add animations so that all pi creatures look at the
        first mobject being animated with each .play call
        """
        animations = super().anims_from_play_args(*args, **kwargs)
        anim_mobjects = Group(*[a.mobject for a in animations])
        all_movers = anim_mobjects.get_family()
        if not self.any_pi_creatures_on_screen():
            return animations

        pi_creatures = self.get_on_screen_pi_creatures()
        non_pi_creature_anims = [
            anim
            for anim in animations
            if len(set(anim.mobject.get_family()).intersection(pi_creatures)) == 0
        ]
        if len(non_pi_creature_anims) == 0:
            return animations
        # Get pi creatures to look at whatever
        # is being animated
        first_anim = non_pi_creature_anims[0]
        if hasattr(first_anim, "target_mobject") and first_anim.target_mobject is not None:
            main_mobject = first_anim.target_mobject
        else:
            main_mobject = first_anim.mobject
        for pi_creature in pi_creatures:
            if pi_creature not in all_movers:
                animations.append(ApplyMethod(pi_creature.look_at, main_mobject))
        return animations

    def blink(self):
        """
        随机挑选一个pi生物眨眼
        """
        self.play(Blink(random.choice(self.get_on_screen_pi_creatures())))

    def joint_blink(self, pi_creatures=None, shuffle=True, **kwargs):
        if pi_creatures is None:
            pi_creatures = self.get_on_screen_pi_creatures()
        creatures_list = list(pi_creatures)
        if shuffle:
            random.shuffle(creatures_list)

        def get_rate_func(pi):
            index = creatures_list.index(pi)
            proportion = float(index) / len(creatures_list)
            start_time = 0.8 * proportion
            return squish_rate_func(
                there_and_back,
                start_time, start_time + 0.2
            )

        self.play(*[
            Blink(pi, rate_func=get_rate_func(pi), **kwargs)
            for pi in creatures_list
        ])
        return self

    def wait(self, time=1, blink=True, **kwargs):
        if "stop_condition" in kwargs:
            self.non_blink_wait(time, **kwargs)
            return
        while time >= 1:
            time_to_blink = self.total_wait_time % self.seconds_to_blink == 0
            if blink and self.any_pi_creatures_on_screen() and time_to_blink:
                self.blink()
            else:
                self.non_blink_wait(**kwargs)
            time -= 1
            self.total_wait_time += 1
        if time > 0:
            self.non_blink_wait(time, **kwargs)
        return self

    def non_blink_wait(self, time=1, **kwargs):
        Scene.wait(self, time, **kwargs)
        return self

    def change_mode(self, mode):
        """
        play函数的参数不应该是animation吗?
        这里怎么传入了函数和函数参数?

        答: 历史遗留问题。 比较规范的写法如下
        self.play(self.get_primary_pi_creature().animate.change_mode(mode))
        """
        self.play(self.get_primary_pi_creature().change_mode, mode)

    def look_at(self, thing_to_look_at, pi_creatures=None, added_anims=None, **kwargs):
        if pi_creatures is None:
            pi_creatures = self.get_pi_creatures()
        anims = [
            pi.animate.look_at(thing_to_look_at)
            for pi in pi_creatures
        ]
        if added_anims is not None:
            anims.extend(added_anims)
        self.play(*anims, **kwargs)


class MortyPiCreatureScene(PiCreatureScene):
    """
    定义在这个位置的是类属性
    在3b1b的动画中pi生物分为学生和老师
    学生: 蓝色, 不翻转, 左下角
    老师: 棕色, 翻转, 右下角
    """
    default_pi_creature_kwargs: dict = dict(
        color=GREY_BROWN,
        flip_at_start=True,
    )
    default_pi_creature_start_corner: Vect3 = DR


class TeacherStudentsScene(PiCreatureScene):
    student_colors: list[ManimColor] = [BLUE_D, BLUE_E, BLUE_C]
    teacher_color: ManimColor = GREY_BROWN
    background_color: ManimColor = GREY_E
    student_scale_factor: float = 0.8
    seconds_to_blink: float = 2
    screen_height: float = 4

    def setup(self):
        super().setup()
        self.add_background(self.background_color)
        self.screen = ScreenRectangle(
            height=self.screen_height,
            fill_color=BLACK,
            fill_opacity=1.0,
        )
        self.screen.to_corner(UP + LEFT)
        self.hold_up_spot = self.teacher.get_corner(UP + LEFT) + MED_LARGE_BUFF * UP

    def add_background(self, color: ManimColor):
        self.background = FullScreenFadeRectangle(
            fill_color=color,
            fill_opacity=1,
        )
        # linus disable_interaction方法来自于interactive_scene.py 
        # self.disable_interaction(self.background)
        self.add(self.background)
        self.bring_to_back(self.background)

    def create_pi_creatures(self):
        """
        覆写父类的方法
        """
        self.teacher = Mortimer(color=self.teacher_color)
        self.teacher.to_corner(DOWN + RIGHT)
        self.teacher.look(DOWN + LEFT)
        self.students = VGroup(*[
            Randolph(color=c)
            for c in self.student_colors
        ])
        self.students.arrange(RIGHT)
        self.students.scale(self.student_scale_factor)
        self.students.to_corner(DOWN + LEFT)
        self.teacher.look_at(self.students[-1].eyes)
        for student in self.students:
            student.look_at(self.teacher.eyes)

        return [*self.students, self.teacher]

    def get_teacher(self):
        return self.teacher

    def get_students(self):
        return self.students

    """
    class MoveForwardWithApproximation(TeacherStudentsScene):
        def construct(self):
            self.teacher_says(
                "Move forward with \\\\",
                "the", "approximation"
            )
            self.play_student_changes("hesitant", "erm", "sassy")
            self.wait()
            words = TexText(
                "It gets better", 
                "\\\\ for smaller ",
                "$dr$"
            )
            words.set_color_by_tex("dr", BLUE)
            self.teacher_says(words, target_mode = "shruggie")
            self.wait(3)
    
    content参数可以是一个字符串, 也可以是一个mobject
    """
    def teacher_says(self, content, **kwargs):
        return self.pi_creature_says(self.get_teacher(), content, **kwargs)

    def student_says(
        self, content,
        target_mode=None,
        bubble_direction=LEFT,
        index=2,
        **kwargs
    ):
        if target_mode is None:
            target_mode = random.choice([
                "raise_right_hand",
                "raise_left_hand",
            ])
        return self.pi_creature_says(
            self.get_students()[index], content,
            target_mode=target_mode,
            bubble_direction=bubble_direction,
            **kwargs
        )

    def teacher_thinks(self, content, **kwargs):
        return self.pi_creature_thinks(self.get_teacher(), content, **kwargs)

    def student_thinks(self, content, target_mode=None, index=2, **kwargs):
        return self.pi_creature_thinks(
            self.get_students()[index], content,
            target_mode=target_mode,
            **kwargs
        )

    def play_all_student_changes(self, mode, **kwargs):
        self.play_student_changes(*[mode] * len(self.students), **kwargs)

    """
    self.play_student_changes(
            *["hooray"]*3,
            look_at = series[1].get_left(),
            added_anims = [
                ApplyMethod(this_video.restore, run_time = 3),
            ]
        )
    """
    """
    self.play_student_changes(
            "pondering", "sassy", "pondering",
            look_at = self.teacher.eyes,
            added_anims = [
                self.teacher.change_mode, "plain"
            ]
        )
    """
    def play_student_changes(self, *modes, **kwargs):
        added_anims = kwargs.pop("added_anims", [])
        self.play(
            self.change_students(*modes, **kwargs),
            *added_anims
        )

    def change_students(self, *modes, look_at=None, lag_ratio=0.5, run_time=1):
        """
        注意: 学生的数目和mode的数目要匹配
        """
        return LaggedStart(
            *(
                student.change(mode, look_at)
                for student, mode in zip(self.get_students(), modes)
                if mode is not None
            ),
            lag_ratio=lag_ratio,
            run_time=run_time,
        )

    def zoom_in_on_thought_bubble(self, bubble=None, radius=FRAME_Y_RADIUS + FRAME_X_RADIUS):
        if bubble is None:
            for pi in self.get_pi_creatures():
                if isinstance(pi.bubble, ThoughtBubble):
                    bubble = pi.bubble
                    break
            if bubble is None:
                raise Exception("No pi creatures have a thought bubble")
        vect = -bubble.get_bubble_center()

        def func(point):
            centered = point + vect
            return radius * centered / get_norm(centered)
        self.play(*[
            ApplyPointwiseFunction(func, mob)
            for mob in self.get_mobjects()
        ])

    def teacher_holds_up(self, mobject, target_mode="raise_right_hand", added_anims=None, **kwargs):
        mobject.move_to(self.hold_up_spot, DOWN)
        mobject.shift_onto_screen()
        added_anims = added_anims or []
        self.play(
            FadeIn(mobject, shift=UP),
            self.teacher.change(target_mode, mobject),
            *added_anims
        )
