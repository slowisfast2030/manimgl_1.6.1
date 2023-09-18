
from manimlib.constants import *
from manimlib.mobject.svg.tex_mobject import SingleStringTex
from manimlib.utils.config_ops import digest_config

from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from manimlib.typing import ManimColor, Vect3

class AlphabetCreature(SingleStringTex):
    CONFIG = {
        "color": RED_E,
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
        
        

