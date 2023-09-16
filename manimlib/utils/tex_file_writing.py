import sys
import os
import hashlib
from contextlib import contextmanager

from manimlib.utils.directories import get_tex_dir
from manimlib.config import get_manim_dir
from manimlib.config import get_custom_config
from manimlib.logger import log


SAVED_TEX_CONFIG = {}


def get_tex_config():
    """
    Returns a dict which should look something like this:
    {
        "executable": "latex",
        "template_file": "tex_template.tex",
        "intermediate_filetype": "dvi",
        "text_to_replace": "YourTextHere",
        "tex_body": "..."
    }
    """
    """
    在default_config.yaml中的tex有这么一段配置:
    text_to_replace: "[tex_expression]"

    在tex模版中有这么一段:
    \begin{document}

    [tex_expression]

    \end{document}

    在manim中使用latex, 会将tex_expression替换成实际的latex表达式
    然后编译成dvi文件, 再转成svg文件
    """
    # Only load once, then save thereafter
    if not SAVED_TEX_CONFIG:
        custom_config = get_custom_config()
        SAVED_TEX_CONFIG.update(custom_config["tex"])
        # Read in template file
        template_filename = os.path.join(
            get_manim_dir(), "manimlib", "tex_templates",
            SAVED_TEX_CONFIG["template_file"],
        )
        with open(template_filename, "r", encoding="utf-8") as file:
            SAVED_TEX_CONFIG["tex_body"] = file.read()
    return SAVED_TEX_CONFIG


def tex_hash(tex_file_content):
    # Truncating at 16 bytes for cleanliness
    hasher = hashlib.sha256(tex_file_content.encode())
    return hasher.hexdigest()[:16]


def tex_to_svg_file(tex_file_content):
    """
    输入完整的tex模版内容, 返回转换后的svg文件path
    """
    # 需要为get_tex_dir()重新设置文件夹
    # 在default_config.yml文件中修改
    svg_file = os.path.join(
        get_tex_dir(), tex_hash(tex_file_content) + ".svg"
    )
    #print(svg_file)
    if not os.path.exists(svg_file):
        # If svg doesn't exist, create it
        tex_to_svg(tex_file_content, svg_file)
    return svg_file


def tex_to_svg(tex_file_content, svg_file):
    """
    将tex模版中的内容编译成svg文件

    tex_file_content --> dvi --> svg
    """
    tex_file = svg_file.replace(".svg", ".tex")
    #print(tex_file)
    with open(tex_file, "w", encoding="utf-8") as outfile:
        outfile.write(tex_file_content)
    svg_file = dvi_to_svg(tex_to_dvi(tex_file))

    # Cleanup superfluous documents
    tex_dir, name = os.path.split(svg_file)
    stem, end = name.split(".")
    for file in filter(lambda s: s.startswith(stem), os.listdir(tex_dir)):
        if not file.endswith(end):
            os.remove(os.path.join(tex_dir, file))

    return svg_file


def tex_to_dvi(tex_file):
    """
    将tex模版转成dvi文件
    """
    tex_config = get_tex_config()
    program = tex_config["executable"]
    file_type = tex_config["intermediate_filetype"]
    result = tex_file.replace(".tex", "." + file_type)
    if not os.path.exists(result):
        commands = [
            program,
            "-interaction=batchmode",
            "-halt-on-error",
            f"-output-directory=\"{os.path.dirname(tex_file)}\"",
            f"\"{tex_file}\"",
            ">",
            os.devnull
        ]
        exit_code = os.system(" ".join(commands))
        if exit_code != 0:
            log_file = tex_file.replace(".tex", ".log")
            log.error("LaTeX Error!  Not a worry, it happens to the best of us.")
            with open(log_file, "r", encoding="utf-8") as file:
                for line in file.readlines():
                    if line.startswith("!"):
                        log.debug(f"The error could be: `{line[2:-1]}`")
            sys.exit(2)
    return result


def dvi_to_svg(dvi_file, regen_if_exists=False):
    """
    Converts a dvi, which potentially has multiple slides, into a
    directory full of enumerated pngs corresponding with these slides.
    Returns a list of PIL Image objects for these images sorted as they
    where in the dvi
    """
    """
    将dvi文件转成svg文件
    """
    file_type = get_tex_config()["intermediate_filetype"]
    result = dvi_file.replace("." + file_type, ".svg")
    if not os.path.exists(result):
        commands = [
            "dvisvgm",
            "\"{}\"".format(dvi_file),
            "-n",
            "-v",
            "0",
            "-o",
            "\"{}\"".format(result),
            ">",
            os.devnull
        ]
        os.system(" ".join(commands))
    return result


# TODO, perhaps this should live elsewhere
@contextmanager
def display_during_execution(message):
    # Only show top line
    to_print = message.split("\n")[0]
    max_characters = os.get_terminal_size().columns - 1
    if len(to_print) > max_characters:
        to_print = to_print[:max_characters - 3] + "..."
    try:
        print(to_print, end="\r")
        yield
    finally:
        print(" " * len(to_print), end="\r")


class LatexError(Exception):
    pass
