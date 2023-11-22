from manimlib import *

# 输入图片的路径，小正方形在长宽上的个数，返回这一系列小正方的集合
def image_divide(image_path, num_rows, num_cols):

    full_image = ImageMobject(image_path).scale(2)
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

    segments = random.sample(list(segments), num_rows*num_cols)

    # Display all the segments
    segments = Group(*segments).space_out_submobjects(1.02)
    return segments

class test(Scene):
    def construct(self):
        segments = image_divide("dall-path.png", 3, 3)
        print(len(segments))
        self.add(*segments)

        segments_copy = segments.copy().shift(OUT*3)
        segments_copy.rotate(TAU/4, UP)

        for source, target in zip(segments, segments_copy):
            source.target = target
            source.shift(IN*3)

        frame = self.camera.frame
        frame.reorient(20, 70)

        #self.add(*segments_copy)
        # self.play(LaggedStart(*[MoveToTarget(source) for source in segments], lag_ratio=0), run_time=5)

        for source in segments:
            self.play(MoveToTarget(source, rate=smooth), run_time=0.1)
        
        self.wait(1)
