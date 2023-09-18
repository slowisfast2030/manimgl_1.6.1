import sys
sys.path.append('/Users/linus/Desktop/slow-is-fast/manimgl_1.6.1/3b1b-videos-master')

from manim_imports_ext_new import *

LEFT_EYE_INDEX: int = 0
RIGHT_EYE_INDEX: int = 1
LEFT_PUPIL_INDEX: int = 2
RIGHT_PUPIL_INDEX: int = 3
BODY_INDEX: int = 4
MOUTH_INDEX: int = 5

class NowWeHaveEmotions(TeacherStudentsScene):
    def construct(self):
        """
        blink的效果没有
        """
        self.play(self.change_students('happy', 'hooray', 'hello'))
        self.play(self.teacher.change_mode, 'happy')
        self.teacher_says('Now we have emotions!')
        
        self.wait()
        self.student_says('Hooray!', index=1, target_mode='hooray',
                         added_anims=[self.teacher.change, "hooray"])
        self.play(self.teacher.change_mode, 'hooray')
        self.wait(2)
        self.play(RemovePiCreatureBubble(self.students[1]), target_mode='hooray')
        self.wait(3)


class Pi(PiCreatureScene):
    def construct(self):
        # modes = ['sassy', 'happy', 'hooray']
        # self.play(self.pi_changes(*modes, run_time=1)) 

        # self.introduce_bubble(pi_creature=self.pi_creature, 
        #                       content="To be or not to be, that is a question",
        #                       bubble_type=ThoughtBubble,
        #                       target_mode="thinking")
        
        #self.change_mode('happy')
        self.blink()
    

class test(Scene):
    def construct(self):
        # p = NumberPlane()
        # self.add(p)

        modes = ('plain', 'sassy', 'happy', 'hooray', 'sad', 'thinking', 'confused',
                 'angry', 'speaking', 'pleading', 'shruggie', 'maybe', 'surprised',
                 'well', 'pondering', 'erm', 'raise_right_hand', 'raise_left_hand',
                 'guilty', 'hesitant', 'dance_kick', 'horrified', 'dance_1',
                 'dance_2', 'dance_3', 'gracious', 'tired')
        pi = PiCreature(mode='plain').scale(1)
        self.add(pi)
        for mode in modes:
            t = Text(mode).move_to(UP*2).scale(1)
            self.add(t)
            pi.change_mode(mode)
            self.wait(0.3)
            self.remove(t)


class test1(Scene):
    def construct(self):
       pi = PiCreature(mode='plain') 
       pii = pi.copy()
       self.add(pi)
       #pi.look_at(UP+LEFT)
       self.wait()
       pi.blink()
       #bubble = pi.get_bubble(content="hello")
       #self.add(bubble)
       #pi.shrug()
       #self.play(pi.thinks("hello world"))
       #self.play(pi.replace_bubble("hi"))
       #self.wait()
       #self.play(pi.change("happy"))
       self.wait(0.2)
       self.add(pii)
       self.wait()

class test2(Scene):
    def construct(self):
       pi = PiCreature(mode='plain') 
       self.add(pi)
       pi.target = pi.generate_target()
       pi.target.shrug()
       self.play(MoveToTarget(pi, rate_func=there_and_back, run_time=2))
       #self.play(MoveToTarget(pi, rate_func=linear, run_time=1))