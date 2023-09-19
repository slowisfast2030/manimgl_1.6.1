
from manimlib.constants import *
from manimlib.mobject.svg.tex_mobject import SingleStringTex
from manimlib.utils.config_ops import digest_config
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.geometry import Circle
from manimlib.mobject.geometry import Rectangle


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
        "height": 4,
        "start_corner": ORIGIN+RIGHT*2,
    }

    def __init__(self, 
                 letter: str = "A",
                 **kwargs
                 ):
        """
        __init__方法中的属性和CONFIG字典中的属性是什么关系?
        

        """
        # 在父类Mobject中会调用这个函数, 这里可以省去
        #digest_config(self, kwargs)
        self.letter = letter
        
        super().__init__(self.letter, **kwargs)

        self.init_structure()

        if self.start_corner is not None:
            self.move_to(self.start_corner)
        
        
    def init_structure(self):
        self.body:VMobject = self.submobjects[0]
        self.eyes = self.draw_eyes()
        self.mouth = self.draw_mouth()
        self.set_submobjects([self.body, self.eyes, self.mouth]) 



    def draw_eyes(self):
        eyes = VGroup()

        iris = Circle().scale(0.22).\
                    shift(0.15*LEFT+1.6*UP).\
                    set_stroke(BLACK, 1).\
                    set_fill(WHITE, 1)
        
        pupil_r = iris.get_width() / 2
        pupil_r *= self.pupil_to_eye_width_ratio
        dot_r = pupil_r
        dot_r *= self.pupil_dot_to_pupil_width_ratio

        black = Circle(radius=pupil_r, color=BLACK)
        dot = Circle(radius=dot_r, color=WHITE)
        dot.shift(black.pfp(3 / 8) - dot.pfp(3 / 8))
        pupil = VGroup(black, dot)
        pupil.set_style(fill_opacity=1, stroke_width=0)
        pupil.move_to(iris.get_center()+UR*0.08)

        eye = VGroup(iris, pupil)
        eye.pupil = pupil
        eye.iris = iris
        eyes.add(eye)

        eyes_right = eyes.copy().shift(RIGHT*0.8)
        eyes.add(eyes_right)

        return eyes

    def draw_mouth(self):
        mouth = Rectangle(color=BLACK,
                          height=0.01,
                          width=0.3)
        mouth.shift(UP*1.22 + RIGHT*0.2)
        return mouth
