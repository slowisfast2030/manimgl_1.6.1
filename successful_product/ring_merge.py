from manimlib import *

class test(Scene):
    def construct(self):
        ring = self.get_ring(1, 0.2)
        self.add(ring)
        print(ring.get_all_points())
        
        c = Circle(radius = 1.2).set_stroke(width = 0.5).set_fill(RED)
        c.shift(LEFT*3)
        self.add(c)
    
    def get_ring(self, radius, dR, color = RED):
        ring = Circle(radius = radius + dR).center()
        inner_ring = Circle(radius = radius).center()
        inner_ring.rotate(np.pi, RIGHT)
        ring.append_vectorized_mobject(inner_ring)
        ring.set_stroke(width = 0.5)
        ring.set_fill(color)
        return ring