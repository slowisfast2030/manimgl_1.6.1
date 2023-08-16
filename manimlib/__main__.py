#!/usr/bin/env python
import manimlib.config
import manimlib.logger
import manimlib.extract_scene
import manimlib.utils.init_config
from manimlib import __version__
"""
这里的import语句可以进一步分析
前四行是把manimlib当做了一个普通的文件夹
第五行是把manimlib当做了一个包
执行到第五行的时候会进入manimlib文件夹下的__init__.py文件, 找到__version__变量
"""

"""
python -m manimlib test.py test_demo -ol
manimgl test.py test_demo -ol

manimgl是一个命令的别名, 可以在setup.cfg文件中找到定义
manimgl = manimlib.__main__:main
manim-render = manimlib.__main__:main

同理可知, manim-render也是一个命令的别名
"""
def main():
    print(f"ManimGL \033[32mv{__version__}\033[0m")

    args = manimlib.config.parse_cli()
    if args.version and args.file is None:
        return
    if args.log_level:
        manimlib.logger.log.setLevel(args.log_level)

    if args.config:
        manimlib.utils.init_config.init_customization()
    else:
        config = manimlib.config.get_configuration(args)
        scenes = manimlib.extract_scene.main(config)

        for scene in scenes:
            scene.run()


if __name__ == "__main__":
    main()
