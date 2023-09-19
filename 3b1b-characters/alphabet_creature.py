
from manimlib.constants import *
from manimlib.mobject.mobject import _AnimationBuilder
from manimlib.mobject.svg.tex_mobject import SingleStringTex
from manimlib.mobject.svg.svg_mobject import SVGMobject
from manimlib.utils.config_ops import digest_config
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.mobject import Mobject
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Rectangle
from manimlib.utils.space_ops import get_norm
from manimlib.utils.space_ops import normalize

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from manimlib.typing import ManimColor, Vect3

class AlphabetCreature(SingleStringTex):
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
    CONFIG = {
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
                 **kwargs
                 ):
        
        # 在父类Mobject中会调用这个函数, 这里可以省去
        #digest_config(self, kwargs)
        
        self.letter = letter
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
        初始化卡通生物的body,eyes和mouth
        """
        self.body:VMobject = self.draw_body()
        self.eyes:VGroup = self.draw_eyes()
        self.mouth:VMobject = self.draw_mouth()
        self.set_submobjects([self.body, self.eyes, self.mouth]) 

    def draw_body(self):
        submobjects = self.submobjects
        assert len(submobjects) == 1, "the length of the submobjects must be 1"
        body = submobjects[0]
        return body

    def draw_eyes(self):
        eyes = VGroup()

        # 眼白
        iris = Circle().scale(0.22).\
                    shift(0.15*LEFT+1.6*UP).\
                    set_stroke(BLACK, 1).\
                    set_fill(WHITE, 1)
        
        pupil_r = iris.get_width() / 2
        pupil_r *= self.pupil_to_eye_width_ratio
        dot_r = pupil_r
        dot_r *= self.pupil_dot_to_pupil_width_ratio

        # 眼睛
        black = Circle(radius=pupil_r, color=BLACK)
        dot = Circle(radius=dot_r, color=WHITE)
        dot.shift(black.pfp(3 / 8) - dot.pfp(3 / 8))
        pupil = VGroup(black, dot)
        pupil.set_style(fill_opacity=1, stroke_width=0)
        pupil.move_to(iris.get_center()+UR*0.08)

        # 左眼
        iris_left = iris.copy()
        pupil_left = pupil.copy()
        eye_left = VGroup(iris_left, pupil_left)
        eye_left.iris = iris
        eye_left.pupil = pupil
        eyes.add(eye_left)

        # 右眼
        iris_right = iris.copy().shift(RIGHT*0.8)
        pupil_right = pupil.copy().shift(RIGHT*0.8)
        eye_right = VGroup(iris_right, pupil_right)
        eye_right.iris = iris_right
        eye_right.pupil = pupil_right
        eyes.add(eye_right)

        return eyes

    def draw_mouth(self):
        mouth = Rectangle(color=BLACK,
                          height=0.01,
                          width=0.3)
        mouth.shift(UP*1.22 + RIGHT*0.2)
        return mouth
    
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

    def look(self, direction):
        """
        iris不变, 移动pupil
        """
        direction = normalize(direction)
        self.purposeful_looking_direction = direction
        for eye in self.eyes:
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
        return self

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
        eyes = self.eyes
        eye_bottom_y = eyes.get_y(DOWN)

        for eye_part in eyes.family_members_with_points():
            new_points = eye_part.get_points()
            new_points[:, 1] = eye_bottom_y
            eye_part.set_points(new_points)

        return self
    
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
