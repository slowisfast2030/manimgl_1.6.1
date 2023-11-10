from manimlib import *

class test(Scene):
    def construct(self):
        # Define the radius of the circle and the number of rings/stripes
        R = 3
        num_rings = 20
        
        # Create the initial circle
        circle = Circle(radius=R, color=BLUE).shift(LEFT * 3+UP*2)
        self.add(circle)
        
        # Create the rings from the circle
        rings = VGroup()
        for i in range(1, num_rings + 1):
            ring = Annulus(
                inner_radius=R * (i - 1) / num_rings, 
                outer_radius=R * i / num_rings, 
                color=BLUE, 
                fill_opacity=1
            )
            rings.add(ring)
        
        # Animate the circle transforming into the rings
        self.play(Transform(circle, rings.shift(LEFT * 3+DOWN*2)))
        
        # Turn each ring into a strip
        strips = VGroup()
        for i, ring in enumerate(rings):
            # Calculate the length of the strip based on the circumference of the ring
            strip_length = TAU * (R * i / num_rings)
            strip = Rectangle(
                width=strip_length, 
                height=(R/num_rings), 
                color=BLUE, 
                fill_opacity=1
            )
            # Position the strip
            strip.move_to(ORIGIN, aligned_edge=LEFT)
            strips.add(strip)
            # Animate the ring transforming into a strip
            self.play(Transform(ring, strip), run_time=0.5)
        
        # Animate the stacking of strips into a triangular shape
        triangle_height = R
        triangle_base = 2 * math.sqrt(R**2 - (triangle_height/2)**2)
        
        for i, strip in enumerate(strips):
            # Calculate the scale factor for the width of the strip
            scale_factor = (triangle_base - (i * (triangle_base / num_rings))) / strip.width
            strip.scale(scale_factor, about_point=ORIGIN)
            # Calculate the y-position for the strip
            y_position = -triangle_height / 2 + (i * (triangle_height / num_rings)) + (triangle_height / num_rings) / 2
            # Animate the movement of the strip to its position in the triangle
            self.play(strip.animate.move_to([0, y_position, 0]), run_time=0.5)
        
        # Pause to admire the work!
        self.wait(2)

# To run this scene, use the following command in your terminal:
# manimgl script_name.py CircleToTriangle
