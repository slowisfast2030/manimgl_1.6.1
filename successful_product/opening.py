from manimlib import *

class test(Scene):
    def construct(self):
        words = TexText(
            """
            ``There is hardly any theory which is more elementary 
            than linear algebra, in spite of the fact that generations 
            of professors and textbook writers have obscured its 
            simplicity by preposterous calculations with matrices.''
            """, 
            organize_left_to_right = False
        )
        words.set_width(2*(FRAME_X_RADIUS-1))
        words.to_edge(UP)        
        for mob in words.submobjects[48:49+13]:
            mob.set_color(GREEN)
        author = TexText("-Jean Dieudonn\\'e")
        author.set_color(YELLOW)
        author.next_to(words, DOWN)

        self.play(FadeIn(words))
        self.wait(3)
        self.play(Write(author, run_time = 5))
        self.wait()