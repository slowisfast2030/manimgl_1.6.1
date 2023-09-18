
from manimlib.constants import *
from manimlib.mobject.svg.tex_mobject import SingleStringTex
from manimlib.utils.config_ops import digest_config
from manimlib.mobject.types.vectorized_mobject import VGroup
from manimlib.mobject.types.vectorized_mobject import VMobject
from manimlib.mobject.geometry import Circle

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from manimlib.typing import ManimColor, Vect3

class AlphabetCreature(SingleStringTex):
    pupil_to_eye_width_ratio: float = 0.4
    pupil_dot_to_pupil_width_ratio: float = 0.3

    CONFIG = {
        "color": BLUE_E,
        "height": 3,
        "start_corner": ORIGIN
    }

    def __init__(self, 
                 letter: str = "A",
                 **kwargs
                 ):
        digest_config(self, kwargs)
        self.letter = letter
        super().__init__(self.letter, **kwargs)
        self.init_structure()
        
        
    def init_structure(self):
        self.body:VMobject = self.submobjects[0]
        self.eyes = self.draw_eyes()
        self.set_submobjects([self.body, self.eyes]) 


    def draw_eyes(self):
        eyes = VGroup()

        
        # 眼白
        iris = Circle().scale(0.2).\
                    shift(0.25*LEFT+1.6*UP).\
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

        return eyes
        
