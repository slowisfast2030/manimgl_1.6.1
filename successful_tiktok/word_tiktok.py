import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

# 三个小球在右上角的坐标
mob1_coord = [1.78, 6.7, 0.]
mob2_coord = [2.7, 6.7, 0.]
mob3_coord = [3.62, 6.7, 0.]

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
    
    segments = Group(*segments).space_out_submobjects(1.02)
    return segments

# 传入三张图片的地址，返回3个小球
def three_sphere_with_texture(texture1, texture2, texture3):
    sphere1 = Sphere(radius=3)
    sphere2 = Sphere(radius=3)
    sphere3 = Sphere(radius=3)

    def update_sphere_right(sphere, dt):
        sphere.rotate(0.3 * dt, axis=RIGHT)
    
    def update_sphere_up(sphere, dt):
        sphere.rotate(0.3 * dt, axis=UP)

    def update_sphere(sphere, dt):
        sphere.rotate(0.3 * dt)

    mob1 = TexturedSurface(sphere1, texture1).scale(0.3).rotate(PI/2, axis=RIGHT)
    mob1.add_updater(update_sphere_right)

    mob2 = TexturedSurface(sphere2, texture2).scale(0.3).rotate(PI/2, axis=RIGHT)
    mob2.add_updater(update_sphere_up)

    mob3 = TexturedSurface(sphere3, texture3).scale(0.3).rotate(PI/2, axis=RIGHT)
    mob3.add_updater(update_sphere)

    gr = Group(mob1, mob2, mob3).arrange(RIGHT, buff=1).shift(UP*2)
    return gr