from manimlib import *

class DivideImage(Scene):
    def construct(self):
        # Load the full image
        image_path = "dall-path.png"
        full_image = ImageMobject(image_path).scale(2)

        # Dimensions for slicing (4x4 grid)
        num_rows, num_cols = 10, 10
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
                segment = ImageMobject(image_path)
                segment.set_width(segment_width)
                segment.set_height(segment_height)
                segment.move_to(np.array([x, y, 0]))

                # Calculate and set im_coords
                left, right = j / num_cols, (j + 1) / num_cols
                top, bottom = i / num_rows, (i + 1) / num_rows
                segment.data["im_coords"] = np.array([(left, top), (left, bottom), (right, top), (right, bottom)])

                segments.append(segment)

        # Display all the segments
        segments = Group(*segments).space_out_submobjects(1.02)
        self.add(*segments)

        # Iterate over each segment and apply a rotation animation
        segments = random.sample(list(segments), num_rows*num_cols)
        # 在翻转之前，先执行一次翻转
        for i in range(len(segments)):
            if i % 4 == 0:
                segments[i]= segments[i].rotate(TAU/2, UP).copy()
            elif i % 4 == 1:
                segments[i].rotate(TAU/4, OUT)
            elif i % 4 == 2:
                segments[i].rotate(TAU/4, IN)
            else:
                segments[i].rotate(TAU/2, OUT)

        # for i in range(len(segments)):
        #     if i % 2 == 1:
        #         self.play(ApplyMethod(segments[i].rotate, TAU/2, UP), run_time=0.5)
        #     else:
        #         self.play(ApplyMethod(segments[i].rotate, TAU/4, -OUT), run_time=0.5)
    
        anims = []
        for i in range(len(segments)):
            if i % 4 == 0:
                anims.append(ApplyMethod(segments[i].rotate, TAU/2, UP))
            elif i % 4 == 1:
                anims.append(ApplyMethod(segments[i].rotate, TAU/4, -OUT))
            elif i % 4 == 2:
                anims.append(ApplyMethod(segments[i].rotate, TAU/4, -IN))
            else:
                anims.append(ApplyMethod(segments[i].rotate, TAU/2, -OUT))
        
        self.play(*anims, run_time=3)

        #self.play(LaggedStartMap(FadeIn, segments, lag_ratio=0), run_time=3)

        self.wait()