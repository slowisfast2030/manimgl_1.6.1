from __future__ import annotations

import os
import sys
import shutil
import platform
import subprocess as sp

import numpy as np
from pydub import AudioSegment
from tqdm import tqdm as ProgressDisplay

from manimlib.constants import FFMPEG_BIN
from manimlib.utils.config_ops import digest_config
from manimlib.utils.file_ops import guarantee_existence
from manimlib.utils.file_ops import add_extension_if_not_present
from manimlib.utils.file_ops import get_sorted_integer_files
from manimlib.utils.sounds import get_full_sound_file_path
from manimlib.logger import log

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from manimlib.scene.scene import Scene
    from manimlib.camera.camera import Camera
    from PIL.Image import Image


"""
这个类最重要的两个函数:
1.open_movie_pipe
2.write_to_movie

open_movie_pipe是开启一个进程, 可以接收原始图片数据 (通过ffmpeg命令可以将一系列图片数据生成视频)
write_to_movie是将原始图片数据写入到进程中

在scene.py文件中会不断调用write_to_movie函数
"""
class SceneFileWriter(object):
    CONFIG = {
        "write_to_movie": False,
        "break_into_partial_movies": False,
        # TODO, save_pngs is doing nothing
        "save_pngs": False,
        "png_mode": "RGBA",
        "save_last_frame": False,
        "movie_file_extension": ".mp4",
        # Should the path of output files mirror the directory
        # structure of the module holding the scene?
        "mirror_module_path": False,
        # What python file is generating this scene
        "input_file_path": "",
        # Where should this be written
        "output_directory": None,
        "file_name": None,
        "open_file_upon_completion": False,
        "show_file_location_upon_completion": False,
        "quiet": False,
        "total_frames": 0,
        "progress_description_len": 60,
    }

    def __init__(self, scene, **kwargs):
        digest_config(self, kwargs)
        self.scene: Scene = scene
        self.writing_process: sp.Popen | None = None
        self.has_progress_display: bool = False
        self.init_output_directories()
        self.init_audio()

    # Output directories and files
    """
    执行一个非常简单的test_demo场景，经过打印发现
    下面这个函数执行了两次
    一次打印了image_file_path
    一次打印了movie_file_path
    难怪，每次执行场景都会自动生成一个图片和一个视频

    那么，生成文件的命令是哪里来的？
    初步猜测：write_to_movie和save_last_frame都是对命令行参数的解析
    """
    def init_output_directories(self) -> None:
        #print("-"*100)
        out_dir = self.output_directory
        if self.mirror_module_path:
            module_dir = self.get_default_module_directory()
            out_dir = os.path.join(out_dir, module_dir)
            # print("out_dir:", out_dir) 没有打印

        scene_name = self.file_name or self.get_default_scene_name()
        # print("scene_name:", scene_name)
        # scene_name: test_demo

        if self.save_last_frame:
            image_dir = guarantee_existence(os.path.join(out_dir, "images"))
            image_file = add_extension_if_not_present(scene_name, ".png")
            self.image_file_path = os.path.join(image_dir, image_file)
            # print("image_file_path:", self.image_file_path)
            # image_file_path: /Users/linus/Desktop/images/test_demo.png

        if self.write_to_movie:
            movie_dir = guarantee_existence(os.path.join(out_dir, "videos"))
            movie_file = add_extension_if_not_present(scene_name, self.movie_file_extension)
            self.movie_file_path = os.path.join(movie_dir, movie_file)
            # print("movie_file_path:", self.movie_file_path)
            # movie_file_path: /Users/linus/Desktop/videos/test_demo.mp4
            if self.break_into_partial_movies:
                self.partial_movie_directory = guarantee_existence(os.path.join(
                    movie_dir, "partial_movie_files", scene_name,
                ))

    def get_default_module_directory(self) -> str:
        path, _ = os.path.splitext(self.input_file_path)
        if path.startswith("_"):
            path = path[1:]
        return path

    def get_default_scene_name(self) -> str:
        name = str(self.scene)
        saan = self.scene.start_at_animation_number
        eaan = self.scene.end_at_animation_number
        if saan is not None:
            name += f"_{saan}"
        if eaan is not None:
            name += f"_{eaan}"
        return name

    def get_resolution_directory(self) -> str:
        pixel_height = self.scene.camera.pixel_height
        frame_rate = self.scene.camera.frame_rate
        return "{}p{}".format(
            pixel_height, frame_rate
        )

    # Directory getters
    def get_image_file_path(self) -> str:
        """
        返回的是生成的图片文件的路径
        比如：/Users/linus/Desktop/images/test_demo.png
        """
        return self.image_file_path

    def get_next_partial_movie_path(self) -> str:
        """
        返回的是生成的partial movie文件的路径
        """
        result = os.path.join(
            self.partial_movie_directory,
            "{:05}{}".format(
                self.scene.num_plays,
                self.movie_file_extension,
            )
        )
        return result

    def get_movie_file_path(self) -> str:
        """
        返回的是生成的视频文件的路径
        比如：/Users/linus/Desktop/videos/test_demo.mp4
        """
        return self.movie_file_path

    # Sound
    def init_audio(self) -> None:
        self.includes_sound: bool = False

    def create_audio_segment(self) -> None:
        self.audio_segment = AudioSegment.silent()

    def add_audio_segment(
        self,
        new_segment: AudioSegment,
        time: float | None = None,
        gain_to_background: float | None = None
    ) -> None:
        if not self.includes_sound:
            self.includes_sound = True
            self.create_audio_segment()
        segment = self.audio_segment
        curr_end = segment.duration_seconds
        if time is None:
            time = curr_end
        if time < 0:
            raise Exception("Adding sound at timestamp < 0")

        new_end = time + new_segment.duration_seconds
        diff = new_end - curr_end
        if diff > 0:
            segment = segment.append(
                AudioSegment.silent(int(np.ceil(diff * 1000))),
                crossfade=0,
            )
        self.audio_segment = segment.overlay(
            new_segment,
            position=int(1000 * time),
            gain_during_overlay=gain_to_background,
        )

    def add_sound(
        self,
        sound_file: str,
        time: float | None = None,
        gain: float | None = None,
        gain_to_background: float | None = None
    ) -> None:
        file_path = get_full_sound_file_path(sound_file)
        new_segment = AudioSegment.from_file(file_path)
        if gain:
            new_segment = new_segment.apply_gain(gain)
        self.add_audio_segment(new_segment, time, gain_to_background)

    # Writers
    def begin(self) -> None:
        if not self.break_into_partial_movies and self.write_to_movie:
            self.open_movie_pipe(self.get_movie_file_path())

    def begin_animation(self) -> None:
        if self.break_into_partial_movies and self.write_to_movie:
            self.open_movie_pipe(self.get_next_partial_movie_path())

    def end_animation(self) -> None:
        if self.break_into_partial_movies and self.write_to_movie:
            self.close_movie_pipe()

    def finish(self) -> None:
        """
        果然, write_to_movie和save_last_frame都被执行了
        """
        # print("="*80)
        # print("self.write_to_movie: ", self.write_to_movie)
        # print("self.save_last_frame: ", self.save_last_frame)
        """
        非常困惑
        执行 ```manimgl test.py test -o -s```
        self.write_to_movie:  False
        self.save_last_frame:  True

        执行 ```manimgl test.py test -o -l``` 执行两次
        第一次
        self.write_to_movie:  False
        self.save_last_frame:  True
        第二次
        self.write_to_movie:  True
        self.save_last_frame:  False
        """

        if self.write_to_movie:
            #print("write_to_movie")
            if self.break_into_partial_movies:
                self.combine_movie_files()
            else:
                self.close_movie_pipe()
            if self.includes_sound:
                self.add_sound_to_video()
            # 打印视频文件已生成
            self.print_file_ready_message(self.get_movie_file_path())
        
        if self.save_last_frame:
            #print("save_last_frame")
            self.scene.update_frame(ignore_skipping=True)
            self.save_final_image(self.scene.get_image())
        
        if self.should_open_file():
            # 打开视频文件
            self.open_file()

    def open_movie_pipe(self, file_path: str) -> None:
        """
        打开movie pipe

        file_path: /Users/linus/Desktop/videos/test_demo.mp4
        """
        # stem: /Users/linus/Desktop/videos/test_demo
        # ext: .mp4
        stem, ext = os.path.splitext(file_path)
        self.final_file_path = file_path
        self.temp_file_path = stem + "_temp" + ext

        # fps, width和height都是随着命令行参数的变化而变化
        # -l -m --uhd
        fps = self.scene.camera.frame_rate
        width, height = self.scene.camera.get_pixel_shape()

        command = [
            FFMPEG_BIN,
            '-y',  # overwrite output file if it exists
            '-f', 'rawvideo',
            '-s', f'{width}x{height}',  # size of one frame
            '-pix_fmt', 'rgba',
            '-r', str(fps),  # frames per second
            '-i', '-',  # The input comes from a pipe
            '-vf', 'vflip',
            '-an',  # Tells FFMPEG not to expect any audio
            '-loglevel', 'error',
        ]
        if self.movie_file_extension == ".mov":
            # This is if the background of the exported
            # video should be transparent.
            command += [
                '-vcodec', 'qtrle',
            ]
        elif self.movie_file_extension == ".gif":
            command += []
        else:
            command += [
                '-vcodec', 'libx264',
                '-pix_fmt', 'yuv420p',
            ]
        command += [self.temp_file_path]
        # 创建一个新进程，执行command命令，从sp.PIPE读取数据
        # 也就是说，这个进程会从sp.PIPE读取数据，然后写入到temp_file_path文件中
        # 那么，这个进程的输入数据是从哪里来的呢？
        self.writing_process = sp.Popen(command, stdin=sp.PIPE)

        if self.total_frames > 0:
            self.progress_display = ProgressDisplay(
                range(self.total_frames),
                # bar_format="{l_bar}{bar}|{n_fmt}/{total_fmt}",
                leave=False,
                ascii=True if platform.system() == 'Windows' else None,
                dynamic_ncols=True,
            )
            self.has_progress_display = True

    def set_progress_display_subdescription(self, sub_desc: str) -> None:
        desc_len = self.progress_description_len
        file = os.path.split(self.get_movie_file_path())[1]
        full_desc = f"Rendering {file} ({sub_desc})"
        if len(full_desc) > desc_len:
            full_desc = full_desc[:desc_len - 4] + "...)"
        else:
            full_desc += " " * (desc_len - len(full_desc))
        self.progress_display.set_description(full_desc)

    def write_frame(self, camera: Camera) -> None:
        '''
        写入视频帧

        这个函数会被多次调用, 将raw_bytes写入ffmpeg的sp.PIPE
        在scene.py文件中, 有一个emit_frame函数, 会调用这个函数
        而emit_frame函数又在一个循环中, 会被多次调用
        '''
        if self.write_to_movie:
            raw_bytes = camera.get_raw_fbo_data()
            self.writing_process.stdin.write(raw_bytes)
            if self.has_progress_display:
                self.progress_display.update()

    def close_movie_pipe(self) -> None:
        """
        关闭movie pipe
        """
        self.writing_process.stdin.close()
        self.writing_process.wait()
        self.writing_process.terminate()
        if self.has_progress_display:
            self.progress_display.close()
        shutil.move(self.temp_file_path, self.final_file_path)

    def combine_movie_files(self) -> None:
        """
        将多个paitial movies合并成一个完整的movie
        """
        kwargs = {
            "remove_non_integer_files": True,
            "extension": self.movie_file_extension,
        }
        if self.scene.start_at_animation_number is not None:
            kwargs["min_index"] = self.scene.start_at_animation_number
        if self.scene.end_at_animation_number is not None:
            kwargs["max_index"] = self.scene.end_at_animation_number
        else:
            kwargs["remove_indices_greater_than"] = self.scene.num_plays - 1
        partial_movie_files = get_sorted_integer_files(
            self.partial_movie_directory,
            **kwargs
        )
        if len(partial_movie_files) == 0:
            log.warning("No animations in this scene")
            return

        # Write a file partial_file_list.txt containing all
        # partial movie files
        file_list = os.path.join(
            self.partial_movie_directory,
            "partial_movie_file_list.txt"
        )
        with open(file_list, 'w') as fp:
            for pf_path in partial_movie_files:
                if os.name == 'nt':
                    pf_path = pf_path.replace('\\', '/')
                fp.write(f"file \'{pf_path}\'\n")

        movie_file_path = self.get_movie_file_path()
        commands = [
            FFMPEG_BIN,
            '-y',  # overwrite output file if it exists
            '-f', 'concat',
            '-safe', '0',
            '-i', file_list,
            '-loglevel', 'error',
            '-c', 'copy',
            movie_file_path
        ]
        if not self.includes_sound:
            commands.insert(-1, '-an')

        combine_process = sp.Popen(commands)
        combine_process.wait()

    def add_sound_to_video(self) -> None:
        movie_file_path = self.get_movie_file_path()
        stem, ext = os.path.splitext(movie_file_path)
        sound_file_path = stem + ".wav"
        # Makes sure sound file length will match video file
        self.add_audio_segment(AudioSegment.silent(0))
        self.audio_segment.export(
            sound_file_path,
            bitrate='312k',
        )
        temp_file_path = stem + "_temp" + ext
        commands = [
            FFMPEG_BIN,
            "-i", movie_file_path,
            "-i", sound_file_path,
            '-y',  # overwrite output file if it exists
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "320k",
            # select video stream from first file
            "-map", "0:v:0",
            # select audio stream from second file
            "-map", "1:a:0",
            '-loglevel', 'error',
            # "-shortest",
            temp_file_path,
        ]
        sp.call(commands)
        shutil.move(temp_file_path, movie_file_path)
        os.remove(sound_file_path)

    def save_final_image(self, image: Image) -> None:
        file_path = self.get_image_file_path()
        image.save(file_path)
        self.print_file_ready_message(file_path)

    def print_file_ready_message(self, file_path: str) -> None:
        if not self.quiet:
            log.info(f"File ready at {file_path}")

    def should_open_file(self) -> bool:
        return any([
            self.show_file_location_upon_completion,
            self.open_file_upon_completion,
        ])

    def open_file(self) -> None:
        if self.quiet:
            curr_stdout = sys.stdout
            sys.stdout = open(os.devnull, "w")

        current_os = platform.system()
        file_paths = []

        if self.save_last_frame:
            file_paths.append(self.get_image_file_path())
        if self.write_to_movie:
            file_paths.append(self.get_movie_file_path())

        for file_path in file_paths:
            if current_os == "Windows":
                os.startfile(file_path)
            else:
                commands = []
                if current_os == "Linux":
                    commands.append("xdg-open")
                elif current_os.startswith("CYGWIN"):
                    commands.append("cygstart")
                else:  # Assume macOS
                    commands.append("open")

                if self.show_file_location_upon_completion:
                    commands.append("-R")

                commands.append(file_path)

                FNULL = open(os.devnull, 'w')
                sp.call(commands, stdout=FNULL, stderr=sp.STDOUT)
                FNULL.close()

        if self.quiet:
            sys.stdout.close()
            sys.stdout = curr_stdout
