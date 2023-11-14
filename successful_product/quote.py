from manimlib import *

class OpeningQuote(Scene):
    quote = []
    quote_arg_separator = " "
    highlighted_quote_terms = {}
    author = ""
    fade_in_kwargs = {
        "lag_ratio": 0.5,
        "rate_func": linear,
        "run_time": 5,
    }
    text_size = R"\Large"
    use_quotation_marks = True
    top_buff = 1.0
    author_buff = 1.0

    def construct(self):
        self.quote = self.get_quote()
        self.author = self.get_author(self.quote)
        print(self.quote.tex_strings, self.author.tex_strings)

        self.play(FadeIn(self.quote, **self.fade_in_kwargs))
        self.wait(2)
        self.play(Write(self.author, run_time=3))
        self.wait()

    def get_quote(self, max_width=FRAME_WIDTH - 1):
        text_mobject_kwargs = {
            "alignment": "",
            "arg_separator": self.quote_arg_separator,
        }
        if isinstance(self.quote, str):
            if self.use_quotation_marks:
                quote = TexText("``%s''" %
                                    self.quote.strip(), **text_mobject_kwargs)
            else:
                quote = TexText("%s" %
                                    self.quote.strip(), **text_mobject_kwargs)
        else:
            if self.use_quotation_marks:
                words = [self.text_size + " ``"] + list(self.quote) + ["''"]
            else:
                words = [self.text_size] + list(self.quote)
            quote = TexText(*words, **text_mobject_kwargs)
            # TODO, make less hacky
            if self.quote_arg_separator == " ":
                quote[0].shift(0.2 * RIGHT)
                quote[-1].shift(0.2 * LEFT)
        
        # 报错。因为self.highlighted_quote_terms是一个字典，不是一个列表
        # for term, color in self.highlighted_quote_terms:
        #     quote.set_color_by_tex(term, color)
        for term, color in self.highlighted_quote_terms.items():
            quote.set_color_by_tex(term, color)

        quote.to_edge(UP, buff=self.top_buff)
        if quote.get_width() > max_width:
            quote.set_width(max_width)
        return quote

    def get_author(self, quote):
        author = TexText(self.text_size + " --" + self.author)
        author.next_to(quote, DOWN, buff=self.author_buff)
        author.set_color(YELLOW)
        return author
    

class Chapter1OpeningQuote(OpeningQuote):
    CONFIG = {
        "quote" : [
            """The art of doing mathematics is finding
            that """, "special case", 
            """that contains all the 
            germs of generality."""
        ],
        "quote_arg_separator" : " ",
        "highlighted_quote_terms" : {
            "special case" : BLUE
        },
        "author" : "David Hilbert",
    }