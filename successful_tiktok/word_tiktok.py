import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

# 三个小球在右上角的坐标
Mob1_coord = [1.78, 6.7, 0.]
Mob2_coord = [2.7, 6.7, 0.]
Mob3_coord = [3.62, 6.7, 0.]

# 单词在左上角的坐标
Word_coord = [-2.3, 6.8,0]

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

    # 这里打乱了顺序，是因为要给每个小正方形加上动画
    segments = random.sample(list(segments), num_rows*num_cols)
    segments = Group(*segments).space_out_submobjects(1.02)

    return segments

# 传入三张图片的地址，返回3个小球
def three_sphere_with_texture(texture1, texture2, texture3):
    sphere1 = Sphere(radius=3)
    sphere2 = Sphere(radius=3)
    sphere3 = Sphere(radius=3)

    speed = 0.7

    def update_sphere_right(sphere, dt):
        sphere.rotate(speed * dt, axis=RIGHT)
    
    def update_sphere_up(sphere, dt):
        sphere.rotate(speed * dt, axis=UP)

    def update_sphere(sphere, dt):
        sphere.rotate(speed * dt)

    mob1 = TexturedSurface(sphere1, texture1).scale(0.3).rotate(PI/2, axis=RIGHT)
    mob1.add_updater(update_sphere_right)

    mob2 = TexturedSurface(sphere2, texture2).scale(0.3).rotate(PI/2, axis=RIGHT)
    mob2.add_updater(update_sphere_up)

    mob3 = TexturedSurface(sphere3, texture3).scale(0.3).rotate(PI/2, axis=RIGHT)
    mob3.add_updater(update_sphere)

    mob_gr = Group(mob1, mob2, mob3).arrange(RIGHT, buff=1).shift(UP*2)

    return mob_gr

def student_with_teacher():
    colors = [BLUE, RED]
    student_teacher = [PiCreature(color=color) for color in colors]
    student_teacher = VGroup(*student_teacher)
    student_teacher.arrange(RIGHT, buff=0.9).shift(DOWN*5.5).scale(0.8)

    _, teacher = student_teacher
    teacher.scale(1.3).shift(UP*1.2)

    return student_teacher


class test(Scene):
    def construct(self):
        # 画出3个小球
        textures = ["dall-boy.png", "dall-house.png", "dall-path.png"]
        mob_gr = three_sphere_with_texture(*textures)
        mob_coords = [Mob1_coord, Mob2_coord, Mob3_coord]
        for mob, coord in zip(mob_gr, mob_coords):
            mob.move_to(coord)
            mob.scale(0.4)
            self.add(mob)

        # 画出单词
        word = Text("Abandon").scale(2).move_to(Word_coord).set_color_by_gradient(RED, BLUE)
        self.add(word)
        self.wait(4)

        meaning_1 = Text("V-T If you abandon a place, thing, or person, you\n        leave the place, thing, or person permanently or for a long time, \n        especially when you should not do so.", 
                         font_size=40,
                         t2c={'abandon': BLUE, 'V-T': RED})
        meaning_1.next_to(word, DOWN*2).shift(RIGHT*2.2)

        self.add(meaning_1)