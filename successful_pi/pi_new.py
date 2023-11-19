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
        modes = ['sassy', 'happy', 'hooray']
        self.play(self.pi_changes(*modes, run_time=1)) 

        self.introduce_bubble(pi_creature=self.pi_creature, 
                              content="To be or not to be, that is a question!",
                              bubble_type=ThoughtBubble,
                              target_mode="thinking")
        
        self.change_mode('happy')
        
        # 没有什么效果。blink的效果需要修复
        #self.blink() 
    
class Pi_morty(MortyPiCreatureScene):
    def construct(self):
        modes = ['sassy', 'happy', 'hooray']
        self.play(self.pi_changes(*modes, run_time=1)) 

        self.introduce_bubble(pi_creature=self.pi_creature, 
                              content="To be or not to be, that is a question!",
                              bubble_type=ThoughtBubble,
                              target_mode="thinking")
        
        self.change_mode('happy')

        # 没效果
        self.joint_blink()

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
       pi.target = pi.generate_target()

       self.add(pi)
       self.wait()

       pi.blink()
       self.wait(0.2)
     
       self.remove(pi)
       self.add(pi.target)
       self.wait()

class test2(Scene):
    def construct(self):
       pi = PiCreature(mode='plain') 
       self.add(pi)
       pi.target = pi.generate_target()
       pi.target.blink()
       #pi.target.shrug() 
       self.play(MoveToTarget(pi, rate_func=there_and_back, run_time=1))

class test3(Scene):
    def construct(self):
       pi = PiCreature(mode='plain') 
       self.add(pi)
       pi.target = pi.generate_target()
       pii = pi.target.blink()
       pi.target.shrug() 
       self.play(Transform(pi, pii, rate_func=there_and_back, run_time=1))

class test4(Scene):
    def construct(self):
       pi = PiCreature(mode='plain') 
       self.add(pi)
       pi.look(DOWN+LEFT)
       dot = Dot(pi.eyes[0].get_center()).set_color(RED).scale(0.5)
       self.add(dot)

class test5(Scene):
    def construct(self):
       pi = PiCreature(mode='plain') 
       self.add(pi)
       self.play(Shrug(pi), run_time=3)

class test6(Scene):
    def construct(self):
        path_string = "M 245.05,118.499 L 245.678,118.478 L 246.104,118.016 C 248.603,115.298 250.2,111.95 250.2,108.2 C 250.2,98.9333 240.643,92 229.6,92 C 218.65,92 209.1,98.9376 209.1,108.2 C 209.1,112.039 211.091,116.433 213.983,119.102 L 214.435,119.52 L 215.05,119.499 L 245.05,118.499 Z"

        from svgelements import Path
        path = Path(path_string)

        smob = VMobjectFromSVGPath(path)
        self.add(smob.set_color(RED, 0.6))