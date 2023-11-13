from manimlib import *

class test(Scene):
    CONFIG = {
        "num_vectors": 16,
        "start_color" : PINK,
        "end_color" : BLUE_E,
    }   

    def construct(self):
        vectors = self.get_vectors()
        colors = Color(self.start_color).range_to(
            self.end_color, len(vectors)
        )
        for vect, color in zip(vectors, colors):
            vect.set_color(color)
        
        vector_group = VGroup(*vectors)
        self.add(vector_group)
    
    def get_vectors(self):
        return [
            Vector(a*np.array([1.5, 1]))
            for a in np.linspace(
                -FRAME_Y_RADIUS, FRAME_Y_RADIUS, self.num_vectors
            )
        ]
