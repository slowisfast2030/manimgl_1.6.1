from manimlib import *

# 输入图片的路径，小正方形在长宽上的个数，返回这一系列小正方的集合
def image_divide(image_path, num_rows, num_cols):

    full_image = ImageMobject(image_path).scale(1.5)
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
    segments = Group(*segments).space_out_submobjects(1.1)
    return segments

class test(Scene):
    def construct(self):
        image_path = image_divide("dall-path.png", 10, 10)
        image_house = image_divide("dall-house.png", 10, 10)
        image_boy = image_divide("dall-boy.png", 10, 10).rotate(PI/2)

        # image_path = ImageMobject("dall-path.png").scale(1.5)
        # image_house = ImageMobject("dall-house.png").scale(1.5)
        # image_boy = ImageMobject("dall-boy.png").rotate(PI/2).scale(1.5)

        radius = image_path.get_height()/2
        image_path.move_to(radius * OUT)
        image_house.move_to(radius * OUT)
        image_boy.move_to(radius * OUT)

        result = [image_path]
        
        result.append(image_house.copy().rotate(PI/2, RIGHT, about_point=ORIGIN))
        result.append(image_boy.copy().rotate(PI/2, UP, about_point=ORIGIN))

        result = Group(*result).space_out_submobjects(1.01)
        self.add(*result)   

        frame = self.camera.frame
        def update_frame(frame, dt):
            frame.increment_theta(-0.1 * dt)

        self.play(frame.animate.reorient(60, 70), run_time=2)
        frame.add_updater(update_frame)

        self.wait(5)

        
