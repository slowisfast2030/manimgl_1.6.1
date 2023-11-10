from manimlib import *

class test(Scene):
    def construct(self):
        # Parameters for the animation
        R = 3  # Radius of the circle
        num_rings = 20  # Number of rings and strips
        
        # Create the initial circle
        circle = Circle(radius=R, color=BLUE)
        self.play(FadeIn(circle))
        
        # Create rings by slicing the circle
        rings = VGroup(*[
            AnnularSector(inner_radius=R*(i-1)/num_rings, 
                          outer_radius=R*i/num_rings, 
                          angle=TAU, 
                          color=BLUE).move_to(circle.get_center())
            for i in range(1, num_rings + 1)
        ])
        
        # Animate the transformation from the circle to the rings
        self.play(Transform(circle, rings))
        
        # Create the triangular shape to guide the placement of strips
        triangle = Polygon(
            np.array([-R, -np.sqrt(3)/2*R, 0]), 
            np.array([R, -np.sqrt(3)/2*R, 0]), 
            np.array([0, np.sqrt(3)/2*R, 0]), 
            color=WHITE
        )
        
        # Calculate the total length of all strips
        total_length = sum(2 * PI * R * (i / num_rings) for i in range(1, num_rings + 1))
        
        # Scale the triangle to match the total length of the strips
        triangle.scale(total_length / triangle.get_width())

        # Animate the transformation of the rings into the triangular shape
        for i, annulus in enumerate(rings):
            # Determine the length and width of the strip
            strip_length = annulus.get_width()
            strip_height = annulus.get_height() / num_rings
            
            # Create the strip
            strip = Rectangle(width=strip_length, height=strip_height, color=BLUE)
            strip.move_to(triangle.get_bottom() + UP * strip_height / 2 + UP * i * (strip_height))
            
            # Align the strip's left side to the left side of the triangle
            strip.align_to(triangle, LEFT)
            
            # Animate the annulus transforming into the strip
            self.play(Transform(annulus, strip))
        
        # Fade out the triangle guide
        self.play(FadeOut(triangle))
        
        # Show the final result
        self.wait(2)

# To run this scene, use the following command in your terminal:
# manimgl script_name.py CircleToTriangle
