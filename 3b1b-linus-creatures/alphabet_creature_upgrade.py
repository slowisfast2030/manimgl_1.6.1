from manimlib.constants import *
from manimlib.mobject.mobject import _AnimationBuilder
from manimlib.mobject.svg.tex_mobject import SingleStringTex
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.geometry import Circle
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import normalize

from manimlib.animation.transform import Transform
from manimlib.animation.animation import Animation
from manimlib.mobject.svg.drawings import SpeechBubble
from manimlib.mobject.svg.drawings import ThoughtBubble
from manimlib.mobject.svg.text_mobject import Text
from manimlib.utils.rate_functions import there_and_back


class AlphabetCreature(SingleStringTex):
    """
    eye = iris + pupil + dot
    """
    pupil_to_eye_width_ratio: float = 0.4
    pupil_dot_to_pupil_width_ratio: float = 0.3

    """
    在CONFIG类中定义了2种属性:
    1.父类中出现过, 比如color, height
    2.父类中没有出现过, 比如start_corner

    这里涉及到如何理解继承
    当前类的继承链如下:
    AlphabetCreature --> SingleStringTex --> SVGMobject --> VMobject --> Mobject
    每一个类都会有自己的CONFIG字典
    在当前类中, 我们可以想象
    当前类拥有所有类的方法, 也会拥有所有类的CONFIG中定义的属性
    当前类的同名方法会覆盖父类的同名方法(所有父类的方法会合并到当前类)
    当前类的同名属性会覆盖父类的同名属性(所有的父类的CONFIG字典会合并成一个字典)

    """
    """
    https://zavden.github.io/char-creature-docs/html/CHP_1.html
    想自己实现这里的字符生物
    发现里面的示例”A“是竖直的, 而我这里渲染的是倾斜的
    经过对比发现, 是因为这里自己默认是math_mode: True
    将其改为False就可以了
    """
    CONFIG = {
        "math_mode": False,
        "color": BLUE_E,
        "height": 3,
        "start_corner": ORIGIN,
        "flip_at_start": False,
    }
    """
    __init__方法中的属性和CONFIG字典中的属性是什么关系?
    一般而言, CONFIG中的属性都是类的一般属性
    __init__方法中上属性都是更加私人化的
    
    而且, __init__方法的属性优先级更高, 可以覆盖CONFIG字典的属性
    """
    def __init__(self, 
                 letter: str = "A",
                 eye_scale = 0.25,
                 eye_buffer = 0.5,
                 eye_prop = [0.5, 0.05],
                 **kwargs
                 ):
        
        # 在父类Mobject中会调用这个函数, 这里可以省去
        #digest_config(self, kwargs)
        
        self.letter = letter
        self.eye_scale = eye_scale
        self.eye_buffer = eye_buffer
        self.eye_prop = eye_prop
        self.bubble = None
        
        super().__init__(self.letter, **kwargs)

        self.init_structure()

        self.set_color(self.color)

        if self.start_corner is not None:
            self.move_to(self.start_corner)
        
        if self.flip_at_start:
            self.flip()
        
        self.refresh_triangulation()
        
    def init_structure(self):
        """
        初始化卡通生物的body和eyes
        """
        self.body:VMobject = self.draw_body()
        self.eyes:VGroup = self.draw_eyes()
        self.set_submobjects([self.body, self.eyes]) 

    def draw_body(self):
        submobjects = self.submobjects
        """
        输入的letter只能是一个字符
        """
        assert len(submobjects) == 1, "the length of the submobjects must be 1"
        body = submobjects[0]
        self.body = body
        return body

    def draw_eyes(self):
        # 眼白
        iris = Circle().scale(self.eye_scale).\
                    set_stroke(BLACK, 5).\
                    set_fill(WHITE, 1)
        
        # 瞳孔和瞳孔中的点
        pupil_r = iris.get_width() / 2
        pupil_r *= self.pupil_to_eye_width_ratio
        dot_r = pupil_r
        dot_r *= self.pupil_dot_to_pupil_width_ratio

        # 瞳孔
        black = Circle(radius=pupil_r, color=BLACK)
        dot = Circle(radius=dot_r, color=WHITE)
        dot.shift(black.pfp(3 / 8) - dot.pfp(3 / 8))
        pupil = VGroup(black, dot)
        pupil.set_style(fill_opacity=1, stroke_width=0)
        # 默认情况下，pupil的中心位于iris的中心
        pupil.move_to(iris.get_center())

        # 左眼
        iris_left = iris.copy()
        pupil_left = pupil.copy()
        eye_left = VGroup(iris_left, pupil_left)
        eye_left.iris = iris
        eye_left.pupil = pupil

        # 右眼
        iris_right = iris.copy()
        pupil_right = pupil.copy()
        eye_right = VGroup(iris_right, pupil_right)
        eye_right.iris = iris_right
        eye_right.pupil = pupil_right
        
        eyes = VGroup(eye_left, eye_right).arrange(RIGHT, buff=self.eye_buffer)
        # body左上角
        body_UL = self.body.get_corner(UL)
        # body右上角
        body_UR = self.body.get_corner(UR)
        # body左下角
        body_DL = self.body.get_corner(DL)

        x_vector = (body_UR - body_UL) * self.eye_prop[0]
        y_vector = (body_DL - body_UL) * self.eye_prop[1]

        eyes.move_to(body_UL + x_vector + y_vector)
        return eyes
    
    def align_data_and_family(self, mobject):
        # This ensures that after a transform into a different letter,
        # the alphabet creatures letter will be updated appropriately
        SVGMobject.align_data_and_family(self, mobject)
        if isinstance(mobject, AlphabetCreature):
            self.letter = mobject.get_letter()

    def set_color(self, color, recurse=True):
        """
        为body部分设置颜色
        """
        self.body.set_fill(color, recurse=recurse)
        return self

    def get_color(self):
        return self.body.get_color()
    
    def change_letter(self, new_letter):
        """
        用new_letter实例化一个新对象
        然后become
        """
        new_self = self.__class__(letter=new_letter)
        new_self.match_style(self)
        new_self.match_height(self)
        if self.is_flipped() != new_self.is_flipped():
            new_self.flip()
        new_self.shift(self.eyes.get_center() - new_self.eyes.get_center())
        if hasattr(self, "purposeful_looking_direction"):
            new_self.look(self.purposeful_looking_direction)
        self.become(new_self)
        self.letter = new_letter 
        return self

    def get_letter(self):
        return self.letter

    """
    look应该是一个动画
    """
    def look(self, direction):
        """
        iris不变, 移动pupil
        """
        direction = normalize(direction)
        self.purposeful_looking_direction = direction

        eyes = self.eyes.copy()
        for eye in eyes:
            iris, pupil = eye
            iris_center = iris.get_center()
            right = iris.get_right() - iris_center
            up = iris.get_top() - iris_center
            vect = direction[0] * right + direction[1] * up
            v_norm = get_norm(vect)
            pupil_radius = 0.5 * pupil.get_width()
            vect *= (v_norm - 0.75 * pupil_radius) / v_norm
            pupil.move_to(iris_center + vect)
        
        # 这一行注释掉就正常了
        #self.eyes[1].pupil.align_to(self.eyes[0].pupil, DOWN)
        ani = Transform(self.eyes, eyes, rate_func=there_and_back)    
        return ani

    def look_at(self, point_or_mobject):
        if isinstance(point_or_mobject, Mobject):
            point = point_or_mobject.get_center()
        else:
            point = point_or_mobject
        self.look(point - self.eyes.get_center())
        return self

    def get_looking_direction(self):
        vect = self.eyes[0].pupil.get_center() - self.eyes[0].get_center()
        return normalize(vect)
    
    def get_look_at_spot(self):
        return self.eyes.get_center() + self.get_looking_direction()

    def is_flipped(self):
        return self.eyes.submobjects[0].get_center()[0] > \
            self.eyes.submobjects[1].get_center()[0]

    """
    blink应该是一个动画
    """
    def blink(self):
        """
        将眼睛部分的点的y坐标设置为eye_bottom_y
        从而实现闭眼的效果
        """
        """
        blink的效果需要改进
        眼睛会闭起来
        但不再睁开
        """
        eyes = self.eyes.copy()
        #eye_bottom_y = eyes.get_y(DOWN)
        eye_bottom_y = eyes.get_y(ORIGIN)

        for eye_part in eyes.family_members_with_points():
            new_points = eye_part.get_points()
            new_points[:, 1] = eye_bottom_y
            eye_part.set_points(new_points)

        #ani = self.eyes.animate.become(eyes)
        ani = Transform(self.eyes, eyes, rate_func=there_and_back)
        return ani
    
    # Overrides

    def become(self, mobject):
        super().become(mobject)
        if isinstance(mobject, AlphabetCreature):
            self.bubble = mobject.bubble
        return self
    
     # Animations

    def change(self, new_letter, look_at=None) -> _AnimationBuilder:
        """
        通过animate创建了动画
        """
        animation = self.animate.change_letter(new_letter)
        if look_at is not None:
            animation = animation.look_at(look_at)
        return animation

    def get_bubble(self, content, bubble_type=ThoughtBubble, **bubble_config):
        """
        单独调用这个函数不能正常显示content

        在replace_bubble方法中可以被正常调用

        疑惑
        """
        bubble = bubble_type(**bubble_config)
        if len(content) > 0:
            if isinstance(content[0], str):
                content_mob = Text(content)
            else:
                content_mob = content
            bubble.add_content(content_mob)
            bubble.resize_to_content()
        # 多了一个auto_flip参数
        #bubble.pin_to(self, auto_flip=["direction" not in bubble_config])
        bubble.pin_to(self)
        self.bubble = bubble
        return bubble

    """
    需要修复下
    这里压根不需要mode参数
    """
    def says(self, content, mode="A", look_at=None, **kwargs) -> Animation:
        from alphabet_creature_animations import PiCreatureBubbleIntroduction
        return PiCreatureBubbleIntroduction(
            self, content,
            target_mode=self.letter,
            look_at=look_at,
            bubble_type=SpeechBubble,
            **kwargs,
        )

    def thinks(self, content, mode="A", look_at=None, **kwargs) -> Animation:
        from alphabet_creature_animations import PiCreatureBubbleIntroduction
        return PiCreatureBubbleIntroduction(
            self, content,
            target_mode=self.letter,
            look_at=look_at,
            bubble_type=ThoughtBubble,
            **kwargs,
        )

    """
    需要修复下
    这里压根不需要mode参数
    """ 
    def debubble(self, mode="plain", look_at=None, **kwargs):
        """
        从有bubble的状态回到没有bubble的状态

        注意: 一开始要有bubble
        """
        
        from alphabet_creature_animations import RemovePiCreatureBubble
        result = RemovePiCreatureBubble(
            self, target_mode=self.letter, look_at=look_at, **kwargs
        )
        self.bubble = None
        return result