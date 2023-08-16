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
    print(args)
    """
    执行 manimgl test.py test_demo -ol 

    args: Namespace(color=None, config=False, config_file=None, embed=None, 
    file='test.py', file_name=None, finder=False, frame_rate=None, full_screen=False, 
    gif=False, hd=False, leave_progress_bars=False, log_level=None, low_quality=True, 
    medium_quality=False, open=True, presenter_mode=False, quiet=False, resolution=None, 
    save_pngs=False, scene_names=['test_demo'], skip_animations=False, 
    start_at_animation_number=None, transparent=False, uhd=False, version=False, 
    video_dir=None, write_all=False, write_file=False)
    """
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
