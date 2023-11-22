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

    # Display all the segments
    segments = Group(*segments).space_out_submobjects(1)
    return segments

class test(Scene):
    def construct(self):
        image_path_gr = image_divide("dall-path.png", 20, 20)
        #self.add(*image_path_gr)

        def update_func_alpha(mobs, alpha):
            for mob in mobs:
                x = mob.get_center()[0]
                y = mob.get_center()[1]
                wave_phase = 1 * np.sin(alpha * 1 +x)
                mob.move_to(np.array([x, y, wave_phase]))
            
            return Group(*mobs)

        
        frame = self.camera.frame
        frame.reorient(20,70)

        self.play(UpdateFromAlphaFunc(image_path_gr, update_func_alpha), run_time=3)

