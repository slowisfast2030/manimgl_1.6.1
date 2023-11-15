from manimlib import *

class test(Scene):
    def construct(self):
        ring = self.get_ring(1, 0.2)
        self.add(ring)
    
    def get_ring(self, radius, dR, color = RED):
        ring = Circle(radius = radius + dR).center()
        inner_ring = Circle(radius = radius).center()
        inner_ring.rotate(PI, RIGHT)
        ring.append_vectorized_mobject(inner_ring)
        ring.set_stroke(width = 0.5)
        ring.set_fill(color,1)
        return ring