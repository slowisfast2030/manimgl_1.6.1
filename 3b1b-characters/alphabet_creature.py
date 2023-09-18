
from manimlib.constants import *
from manimlib.mobject.svg.tex_mobject import SingleStringTex


from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from manimlib.typing import ManimColor, Vect3

class AlphabetCreature():

    def __init__(self, 
                 letter: str = "A",
                 color: ManimColor = BLUE_E,
                 stroke_width: float = 0.0, 
                 stroke_color: ManimColor = BLACK,
                 fill_opacity: float = 1.0,
                 height: float = 3,
                 start_corner: Union[Vect3, None] = None,
                 ):
        self.letter = letter
        self.color = color
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color
        self.fill_opacity = fill_opacity
        self.height = height
        self.start_corner = start_corner

        
