import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext import *

# 三个小球在右上角的坐标
Mob1_coord = [1.78, 6.7, 0.]
Mob2_coord = [2.7, 6.7, 0.]
Mob3_coord = [3.62, 6.7, 0.]

# 单词在左上角的坐标
Word_coord = [-2.3, 6.8, 0]

# VT的坐标
VT_coord = [-3.72, 5.81836484, 0.] 

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

def get_image_anims(image_segments):

    # group对象不支持索引，所以要转换成list
    image_segments = list(image_segments)

    # 在翻转之前，先执行一次翻转
    for i in range(len(image_segments)):
        if i % 4 == 0:
            image_segments[i]= image_segments[i].rotate(TAU/2, UP).copy()
        elif i % 4 == 1:
            image_segments[i].rotate(TAU/4, OUT)
        elif i % 4 == 2:
            image_segments[i].rotate(TAU/4, IN)
        else:
            image_segments[i].rotate(TAU/2, OUT)

    anims = []
    for i in range(len(image_segments)):
        if i % 4 == 0:
            anims.append(ApplyMethod(image_segments[i].rotate, TAU/2, UP))
        elif i % 4 == 1:
            anims.append(ApplyMethod(image_segments[i].rotate, TAU/4, -OUT))
        elif i % 4 == 2:
            anims.append(ApplyMethod(image_segments[i].rotate, TAU/4, -IN))
        else:
            anims.append(ApplyMethod(image_segments[i].rotate, TAU/2, -OUT))

    return anims

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

def meaning(parts, parts_ch, sents, sents_ch):
    # parts是单词含义的各个部分，每个部分都是一个str
    VT = Text("V-T", font_size=40, t2c={'V-T': RED})
    #VT = SVGMobject("svg-teapot.svg").scale(0.25)
    VT.move_to(VT_coord) 

    meaning_gr = [VT]

    # 英文释义
    for index, part in enumerate(parts):
        if index == 0:
            meaning_en = Text(part, 
                             font_size=40,
                             t2c={'abandon': BLUE, 'V-T': RED}).set_width(7.3)
            meaning_en.next_to(VT, RIGHT)
            meaning_gr.append(meaning_en)

        elif index == len(parts)-1:
            meaning_en = Text(part, 
                             font_size=40,
                             t2c={'abandon': BLUE, 'V-T': RED})
            meaning_en.next_to(VT, RIGHT).shift(DOWN*0.5*index)
            meaning_gr.append(meaning_en)

        else:
            meaning_en = Text(part, 
                             font_size=40,
                             t2c={'abandon': BLUE, 'V-T': RED}).set_width(7.3)
            meaning_en.next_to(VT, RIGHT).shift(DOWN*0.5*index)
            meaning_gr.append(meaning_en)
    
    # 中文释义
    for index, part in enumerate(parts_ch):

        if index == len(parts_ch)-1:
            index = index + len(parts)

            meaning_ch = Text(part, 
                             font_size=36,
                             t2c={'放弃': BLUE, 'V-T': RED})
            meaning_ch.next_to(VT, RIGHT).shift(DOWN*0.5*index)
            meaning_gr.append(meaning_ch)

        else:
            index = index + len(parts)

            meaning_ch = Text(part, 
                             font_size=36,
                             t2c={'放弃': BLUE, 'V-T': RED}).set_width(7.3)
            meaning_ch.next_to(VT, RIGHT).shift(DOWN*0.5*index)
            meaning_gr.append(meaning_ch)

    
    # VT是释义的定位点，例句也需要一个定位点
    eg = Text("E.G.", font_size=40, t2c={'E.G.': BLUE})
    #eg = SVGMobject("svg-water-cup.svg").scale(0.3)
    eg_coord = VT_coord + (len(parts)+len(parts_ch))*DOWN*0.5 + DOWN * 0.2 # 0.2是调整的参数
    eg.move_to(eg_coord)
    sentence_gr = [eg]

    # 英文例句
    for index, sent in enumerate(sents):
        if index == 0:
            sentence = Text(sent, font_size=40, t2c={'abandoned': BLUE}).set_width(7.3)
            sentence.next_to(eg, RIGHT)
            sentence_gr.append(sentence)
        
        elif index == len(sents)-1:
            sentence = Text(sent, font_size=40, t2c={'abandoned': BLUE})
            sentence.next_to(eg, RIGHT).shift(DOWN*0.5*index)
            sentence_gr.append(sentence)

        else:
            sentence = Text(sent, font_size=40, t2c={'abandoned': BLUE}).set_width(7.3)
            sentence.next_to(eg, RIGHT).shift(DOWN*0.5*index)
            sentence_gr.append(sentence)
    
    # 中文例句
    for index, sent in enumerate(sents_ch):
        if index == len(sents_ch)-1:
            index = index + len(sents)

            sentence = Text(sent, font_size=36, t2c={'抛弃': BLUE})
            sentence.next_to(eg, RIGHT).shift(DOWN*0.5*index)
            sentence_gr.append(sentence)

        else:
            index = index + len(sents)

            sentence = Text(sent, font_size=36, t2c={'抛弃': BLUE}).set_width(7.3)
            sentence.next_to(eg, RIGHT).shift(DOWN*0.5*index)
            sentence_gr.append(sentence)

    meaning_gr = Group(*meaning_gr)
    sentence_gr = Group(*sentence_gr)

    return Group(meaning_gr, sentence_gr)

    


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
        self.wait(0.5)

        # 给出中英文释义
        parts = ["you abandon an activity or piece of work, you", 
                 "stop doing it before it is finished.", 
                 ]
        
        parts_ch = ["如果你放弃一个地方、一件事或一个人，你",
                    "其是当你不应该这样做的时候。"]

        sents = ["The authorities have abandoned any attempt to", 
                 "distribute food in an orderly fashion."]
        
        sents_ch = ["他声称他的父母抛弃了他。"] 

        meaning_sentence = meaning(parts, parts_ch, sents, sents_ch)
        meaning_gr = meaning_sentence[0]
        sentence_gr = meaning_sentence[1]

        self.play(FadeIn(meaning_gr))
        self.play(
            *[Write(sent) for sent in sentence_gr])

        self.wait(1)
        
        # 图片位置固定
        #image_boy = image_divide("dall-house.png", 10, 10).shift(DOWN*3.5).space_out_submobjects(1.01).scale(1)
        # 图片位置不固定
        image_boy = image_divide("dall-house.png", 10, 10).next_to(meaning_sentence, DOWN*2).space_out_submobjects(1.01).scale(1)

        self.add(*image_boy)

        image_anims = get_image_anims(image_boy)
        self.play(*image_anims, run_time=1.5)
        self.wait(1)