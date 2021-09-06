import os
import pathlib
import re
import shutil

from contextlib import contextmanager
from typing import Generator, Optional

import xappt

FFMPEG_PRESETS = ("ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow")  # noqa
TC_LINE_RE = re.compile(r"^\s*(?P<label>[a-z0-9_-]+)\s*[:=]\s*(?P<tc>\d\d:\d\d:\d\d\.\d+).*?", re.I)
TIMECODE_RE = re.compile(r"(?P<hours>\d\d):(?P<minutes>\d\d):(?P<seconds>\d\d\.\d+)$")
EXTENSIONS = (".mp4", ".mkv")


def timecode_to_seconds(tc: str) -> float:
    match = TIMECODE_RE.match(tc)
    if match is None:
        return 0
    hours = float(match.group("hours")) * 60.0 * 60.0
    minutes = float(match.group("minutes")) * 60.0
    seconds = float(match.group("seconds"))
    return hours + minutes + seconds


def build_ffmpeg_command(source: pathlib.Path, crf: int, preset: str) -> tuple:
    destination = xappt.unique_path(source.with_stem(f"{source.stem}.x265"), delimiter="-", length=2,
                                    mode=xappt.UniqueMode.INTEGER)
    return ("-i", str(source), "-c:v", "libx265", "-crf", str(crf), "-preset", preset,
            "-c:a", "copy", str(destination), "-y", "-progress", "pipe:1")


# noinspection DuplicatedCode
@xappt.register_plugin
class ConvertX265(xappt.BaseTool):
    source = xappt.ParamString(options={"ui": "file-open", "accept": ('Video files *.mp4;*.mkv', )},
                               validators=[xappt.ValidateFileExists])
    crf = xappt.ParamInt(minimum=1, maximum=51, default=18)
    preset = xappt.ParamString(choices=FFMPEG_PRESETS, default="veryfast")

    @classmethod
    def name(cls) -> str:
        return "convert-x265"

    @classmethod
    def help(cls) -> str:
        return "Convert a video with the x265 (HEVC) codec."

    @classmethod
    def collection(cls) -> str:
        return "Image"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.total_seconds: Optional[float] = None
        self.current_file: Optional[str] = None
        self.load_config()
        self.ffmpeg_bin_location = shutil.which('ffmpeg')
        self.interface: Optional[xappt.BaseInterface] = None

    def init_config(self):
        """ Set up persistent data """
        super().init_config()
        for param in self.parameters():
            if param.name == 'source':
                continue
            self.add_config_item(param.name,
                                 saver=lambda p=param: getattr(p, "value"),
                                 loader=lambda x, p=param: setattr(p, "value", x),
                                 default=param.default)

    def handle_progress(self, message: str):
        tc_match = TC_LINE_RE.match(message)
        if tc_match is None:
            return

        if self.total_seconds is None:
            if tc_match.group("label") == "Duration":
                self.total_seconds = timecode_to_seconds(tc_match.group("tc"))
        else:
            if tc_match.group("label") == "out_time":
                progress = timecode_to_seconds(tc_match.group("tc")) / self.total_seconds
                self.interface.progress_update(f"encoding {self.current_file} {progress * 100.0:.2f}%...", progress)

    def convert_file(self, file_path: pathlib.Path, message_suffix: str = "") -> int:
        self.interface.progress_start()
        self.current_file = f'"{file_path.stem}" {message_suffix}'.strip()

        command = (self.ffmpeg_bin_location, ) + build_ffmpeg_command(file_path, self.crf.value, self.preset.value)
        print(xappt.CommandRunner.command_sequence_to_string(command))
        result = self.interface.run_subprocess(command)

        self.interface.progress_end()

        return result

    @contextmanager
    def progress_callbacks(self, interface: xappt.BaseInterface):
        interface.on_write_stdout.add(self.handle_progress)
        interface.on_write_stderr.add(self.handle_progress)
        try:
            yield
        finally:
            interface.on_write_stdout.remove(self.handle_progress)
            interface.on_write_stderr.remove(self.handle_progress)

    def execute(self, interface: xappt.BaseInterface, **kwargs) -> int:
        if self.ffmpeg_bin_location is None:
            interface.error("ffmpeg binary not found")
            return 1

        self.interface = interface

        self.save_config()

        self.total_seconds = None
        self.current_file = None

        with self.progress_callbacks(interface):
            result = self.convert_file(pathlib.Path(self.source.value))

        if result == 0:
            interface.message("Complete")
        else:
            interface.error(f"Error: process finished with error code {result}")

        return result


@xappt.register_plugin
class ConvertX265Folder(ConvertX265):
    source = xappt.ParamString(options={"ui": "folder-select"}, validators=[xappt.ValidateFolderExists])
    recursive = xappt.ParamBool()

    @classmethod
    def name(cls) -> str:
        return "convert-x265-folder"

    @classmethod
    def help(cls) -> str:
        return "Convert a directory of videos with the x265 (HEVC) codec."

    @classmethod
    def collection(cls) -> str:
        return "Image"

    @staticmethod
    def recurse_folder(folder: pathlib.Path) -> Generator[pathlib.Path, None, None]:
        for root, dirs, files in os.walk(folder):
            root_path = pathlib.Path(root)
            for f in files:
                item = root_path.joinpath(f)
                if item.suffix.lower() not in EXTENSIONS:
                    continue
                yield item

    def collect_files(self) -> Generator[pathlib.Path, None, None]:
        source_path = pathlib.Path(self.source.value)

        self.interface.progress_start()
        self.interface.progress_update("scanning files", 0.0)

        top_level_items = list(source_path.iterdir())

        for i, item in enumerate(top_level_items):
            progress = i / len(top_level_items)
            self.interface.progress_update(f"scanning {item.name}", progress)
            if item.is_dir() and self.recursive.value:
                yield from self.recurse_folder(item)
            elif item.is_file() and item.suffix.lower() in EXTENSIONS:
                yield item

        self.interface.progress_update("completed scan", 1.0)
        self.interface.progress_end()

    def execute(self, interface: xappt.BaseInterface, **kwargs) -> int:
        ffmpeg_bin = shutil.which('ffmpeg')
        if ffmpeg_bin is None:
            interface.error("ffmpeg binary not found")
            return 1

        self.interface = interface

        self.save_config()

        with self.progress_callbacks(interface):
            self.total_seconds = None
            self.current_file = None

            all_items = list(self.collect_files())
            all_items.sort()
            total_items: int = len(all_items)
            for i, item in enumerate(all_items, start=1):
                self.total_seconds = None

                result = self.convert_file(item, f"({i}/{total_items})")
                if result != 0:
                    interface.error(f"Error: process finished with error code {result}")
                    if not interface.ask("Continue processing additional items?"):
                        return result

        return 0
