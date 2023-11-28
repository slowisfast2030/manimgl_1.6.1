from manim_imports_ext_new import *

"""
这份文件是新加的
因为cahpter1.py中没有定义PatreonThanks
"""
class PatreonThanks(Scene):
    CONFIG = {
        "specific_patrons" : [
            "CrypticSwarm",
            "Ali Yahya",
            "Juan    Batiz-Benet",
            "Yu  Jun",
            "Othman  Alikhan",
            "Joseph  John Cox",
            "Luc Ritchie",
            "Einar Johansen",
            "Rish    Kundalia",
            "Achille Brighton",
            "Kirk    Werklund",
            "Ripta   Pasay",
            "Felipe  Diniz",
        ]
    }
    def construct(self):
        morty = Mortimer()
        morty.next_to(ORIGIN, DOWN)

        n_patrons = len(self.specific_patrons)
        special_thanks = TexText("Special thanks to:")
        special_thanks.set_color(YELLOW)
        special_thanks.shift(3*UP)

        left_patrons = VGroup(*list(map(TexText, 
            self.specific_patrons[:n_patrons/2]
        )))
        right_patrons = VGroup(*list(map(TexText, 
            self.specific_patrons[n_patrons/2:]
        )))
        for patrons, vect in (left_patrons, LEFT), (right_patrons, RIGHT):
            patrons.arrange(DOWN, aligned_edge = LEFT)
            patrons.next_to(special_thanks, DOWN)
            patrons.to_edge(vect, buff = LARGE_BUFF)

        self.play(morty.change_mode, "gracious")
        self.play(Write(special_thanks, run_time = 1))
        self.play(
            Write(left_patrons),
            morty.look_at, left_patrons
        )
        self.play(
            Write(right_patrons),
            morty.look_at, right_patrons
        )
        self.play(Blink(morty))
        for patrons in left_patrons, right_patrons:
            for index in 0, -1:
                self.play(morty.look_at, patrons[index])
                self.wait()