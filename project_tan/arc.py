from manimlib import *

class DrawTriangleAndAngles(Scene):
    def construct(self):
        # Define the vertices of the triangle
        vertex1 = LEFT
        vertex2 = RIGHT
        vertex3 = UP

        # Create the triangle
        triangle = Polygon(vertex1, vertex2, vertex3, color=WHITE)
        self.play(ShowCreation(triangle))

        plane = NumberPlane()
        self.add(plane)

        # Function to calculate the angle between two vectors
        def angle_of_points(p1, p2, p3):
            v1 = p2 - p1
            v2 = p3 - p1
            angle = np.arccos(np.dot(v1, v2)/(np.linalg.norm(v1)*np.linalg.norm(v2)))
            return angle

        # Calculate angles
        angle3 = angle_of_points(vertex1, vertex3, vertex2)

        # Draw angles
        arc3 = Arc(start_angle=Line(vertex1, vertex3).get_angle(), angle=-angle3, radius=0.3, color=BLUE)

        arc3.shift(vertex1)

        # Add the angles to the scene
        self.play(
                  ShowCreation(arc3))
