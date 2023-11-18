from manimlib import *

class test(Scene):
    def construct(self):
        # Create a Mobject, for example, a circle
        circle = Circle()

        # Define a translation function
        # This example translates the object rightwards by 0.5 units per unit of virtual time
        def translation_function(p):
            return np.array([1, 0, 0])  # Translation vector (rightwards)

        # Create a PhaseFlow animation
        translation_animation = PhaseFlow(
            function=translation_function,
            mobject=circle,
            virtual_time=3,  # Adjust as needed for timing
            rate_func=linear
        )

        # Play the animation
        self.play(translation_animation)


class RotationAnimation(Scene):
    def construct(self):
        # Create a Mobject, e.g., a square
        square = Square()

        # Define the rotation function
        # This function rotates the object around the origin
        def rotation_function(p):
            # Define the rotation angle per unit time (in radians)
            angle = 1  # Adjust this for different rotation speeds
            rotation_matrix = np.array([
                [np.cos(angle), -np.sin(angle), 0],
                [np.sin(angle), np.cos(angle), 0],
                [0, 0, 1]
            ])
            return np.dot(rotation_matrix, p) - p

        # Create a PhaseFlow animation
        rotation_animation = PhaseFlow(
            function=rotation_function,
            mobject=square,
            virtual_time=1,  # Adjust as needed
            rate_func=linear
        )

        # Play the animation
        self.play(rotation_animation)

        # Keep the scene displayed after the animation
        self.wait()
