from manimlib import *

class NumberedPlane(Scene):
    def construct(self):
        # Create a number plane with numbered axes
        number_plane = NumberPlane(
            axis_config={
                "include_ticks": True,  # Include ticks on the axis
                "include_numbers": True,  # Include numbers on the axis
                "number_scale_val": 0.5,  # Scale for the numbers on the axis
                "tick_frequency": 1,  # Frequency of the ticks
                "number_to_edge_buff": 0.1,  # Buffer space between the numbers and the edges
                "label_direction": DOWN,  # Direction of the numbers on x-axis
                "line_to_number_buff": 0.1  # Buffer space between the line and numbers
            },
        )

        # Add the number plane to the scene
        self.add(number_plane)

        # Additional animations or elements can be added here as needed
