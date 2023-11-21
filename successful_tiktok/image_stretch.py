from manimlib import *

class test(Scene):
    def construct(self):
        image_path = ImageMobject("dall-path.png").scale(2).shift(IN*4)
        image_path_blocker = SurroundingRectangle(image_path)
        image_path_blocker.set_fill(BLACK, 1)
        image_path_blocker.set_stroke(width=0)
        
        self.add(image_path, image_path_blocker)

        self.play(ApplyMethod(
                image_path_blocker.stretch, 0, 1, {"about_edge": DOWN},
                run_time=3,
                #rate_func=bezier([0, 0, 1, 1]),
                rate_func = rush_into
            ))



class DivideImage(Scene):
    def construct(self):
        # Load the full image
        full_image = ImageMobject("dall-path.png").scale(2)

        # Dimensions for slicing (4x4 grid)
        num_rows, num_cols = 20, 10
        segments = []

        # Calculate the size of each segment
        img_height, img_width = full_image.get_height(), full_image.get_width()
        segment_height, segment_width = img_height / num_rows, img_width / num_cols

        for i in range(num_rows):
            for j in range(num_cols):
                # Calculate the position for each segment
                x = segment_width * (j - num_cols / 2 + 0.5)
                y = segment_height * (num_rows / 2 - i - 0.5)

                # Create a new ImageMobject for the segment
                segment = ImageMobject("dall-path.png")
                segment.set_width(segment_width)
                segment.set_height(segment_height)
                segment.move_to(np.array([x, y, 0]))

                # Calculate and set im_coords
                left, right = j / num_cols, (j + 1) / num_cols
                top, bottom = i / num_rows, (i + 1) / num_rows
                segment.data["im_coords"] = np.array([(left, top), (left, bottom), (right, top), (right, bottom)])

                segments.append(segment)

        # Display all the segments
        segments = Group(*segments).space_out_submobjects(1.1)
        self.add(*segments)
        # for seg in segments:
        #     self.play(FadeIn(seg, rate_func=linear), run_time=0.01)
        #     self.wait(0.1)


        # Iterate over each segment and apply a rotation animation
        for segment in segments:
            # Randomly choose the axis for rotation
            #rotation_axis = np.random.choice([RIGHT, UP])
            # Apply the rotation animation
            #self.play(segment.animate.rotate(TAU/2, UP), run_time=0.5)
            #self.play(ApplyMethod(segment.rotate, TAU/2, UP), run_time=0.5)
            self.play(ApplyMethod(segment.rotate, TAU/2, UP), run_time=0.5)

        self.wait()