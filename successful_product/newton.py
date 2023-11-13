from manimlib import *

class test(Scene):
    def construct(self):
        quote = self.get_quote()
        movers = VGroup(*quote[:-1].family_members_with_points())
        for mover in movers:
            mover.save_state()
            disc = Circle(radius=0.05)
            disc.set_stroke(width=0)
            disc.set_fill(BLACK, 0)
            disc.move_to(mover)
            mover.become(disc)
        self.play(
            FadeIn(quote.author_part, LEFT),
            LaggedStartMap(
                # FadeInFromLarge,
                # quote[:-1].family_members_with_points(),
                Restore, movers,
                lag_ratio=0.005,
                run_time=2,
            )
            # FadeInFromDown(quote[:-1]),
            # lag_ratio=0.01,
        )
        self.wait()
        self.play(
            Write(quote.law_part.copy().set_color(YELLOW)),
            run_time=1,
        )
        self.wait()
        self.play(
            Write(quote.language_part.copy().set_color(BLUE)),
            run_time=1.5,
        )
        self.wait(2)

    def get_quote(self):
        law_words = "laws of physics"
        language_words = "language of differential equations"
        author = "-Steven Strogatz"
        quote = TexText(
            """
            \\Large
            ``Since Newton, mankind has come to realize
            that the laws of physics are always expressed
            in the language of differential equations.''\\\\
            """ + author,
            alignment="",
            arg_separator=" ",
            isolate=[law_words, language_words, author]
        )
        quote.law_part = quote.get_part_by_tex(law_words)
        quote.language_part = quote.get_part_by_tex(language_words)
        quote.author_part = quote.get_part_by_tex(author)
        quote.set_width(12)
        quote.to_edge(UP)
        quote[-2].shift(SMALL_BUFF * LEFT)
        quote.author_part.shift(RIGHT + 0.5 * DOWN)
        quote.author_part.scale(1.2, about_edge=UL)

        return quote