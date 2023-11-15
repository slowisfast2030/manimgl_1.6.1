from manimlib import *

class RingMerge(Scene):
    def construct(self):
        ring = self.get_ring(1, 0.2).move_to(LEFT)
        self.add(ring)
        print(ring.get_all_points())
    
    def get_ring(self, radius, dR, color = GREEN):
        ring = Circle(radius = radius + dR).center()
        inner_ring = Circle(radius = radius)
        inner_ring.rotate(np.pi, RIGHT)
        ring.append_vectorized_mobject(inner_ring)
        ring.set_stroke(width = 0)
        ring.set_fill(color)
        return ring