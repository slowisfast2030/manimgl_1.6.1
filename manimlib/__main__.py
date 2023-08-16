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
        """
        {'module': <module 'test' from 'test.py'>, 'scene_names': ['test_demo'], 
        'file_writer_config': 
            {'write_to_movie': True, 'break_into_partial_movies': False, 
            'save_last_frame': False, 'save_pngs': False, 'png_mode': 'RGB', 
            'movie_file_extension': '.mp4', 'mirror_module_path': False, 
            'output_directory': '/Users/linus/Desktop', 'file_name': None, 
            'input_file_path': 'test.py', 'open_file_upon_completion': False, 
            'show_file_location_upon_completion': False, 'quiet': False}, 
        'quiet': False, 'write_all': False, 'skip_animations': False, 
        'start_at_animation_number': None, 'end_at_animation_number': None, 
        'preview': False, 'presenter_mode': False, 'leave_progress_bars': False, 
        'camera_config': 
            {'pixel_width': 854, 'pixel_height': 480, 'frame_rate': 15, 
            'background_color': <Color #333>}, 
        'window_config': {'size': (720, 405)}}
        """
        scenes = manimlib.extract_scene.main(config)
        """
        [<test.test_demo object at 0x7f89ba7754c0>]
        """
        for scene in scenes:
            scene.run()


if __name__ == "__main__":
    main()
