import pathlib
import re
import shutil

from contextlib import contextmanager
from typing import Optional

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
        return ("This is a fairly complex example tool that uses [FFMpeg](https://www.ffmpeg.org/) to convert "
                "a video using the *x265 (HEVC)* codec.\n\nThe following techniques are demonstrated:\n\n"
                "* using the interface's subprocess mechanism\n"
                "* setting up callbacks to monitor stdout and stderr\n"
                "* storing settings between sessions.")

    @classmethod
    def collection(cls) -> str:
        return "Examples"

    def __init__(self, *, interface: xappt.BaseInterface, **kwargs):
        """ We're overriding `__init__` to set up some instance variables and to call
        `load_config`. See the note in `init_config()`.

        Note that `init_config()` is called in `BasePlugin.__init__`, so don't forget to
        call `self.load_config()` _after_ `super().__init__()`
        """
        super().__init__(interface=interface, **kwargs)
        self.total_seconds: Optional[float] = None
        self.current_file: Optional[str] = None
        self.load_config()

    def init_config(self):
        """ Set up persistent data. We're looping through all parameters and setting up a
        loader and saver function for each, except for "source".

        During `execute` we're calling `self.save_config()` which stores all config items
        using the specified saver function, and likewise during `__init__` we're calling
        `self.load_config()` which uses the specified loader function.
        """
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

    @contextmanager
    def progress_callbacks(self):
        """ This context manager is simply to ensure that the progress handler callbacks
        are removed when we are done with them. This way we don't have to worry about tools
        that have not yet been garbage collected modifying the progress bars
        unintentionally. """
        self.interface.progress_start()
        self.interface.on_write_stdout.add(self.handle_progress)
        self.interface.on_write_stderr.add(self.handle_progress)
        try:
            yield
        finally:
            self.interface.on_write_stderr.remove(self.handle_progress)
            self.interface.on_write_stdout.remove(self.handle_progress)
            self.interface.progress_end()
            self.flush_progress_deferred_ops()

    def flush_progress_deferred_ops(self):
        """ Make sure there's a call to "invoke" to trigger callback removals. Pausing the callback
        prevents the invoke from actually doing anything other than processing deferred operations.
        """
        self.interface.on_write_stderr.paused = True
        self.interface.on_write_stderr.invoke("")
        self.interface.on_write_stderr.paused = False

        self.interface.on_write_stdout.paused = True
        self.interface.on_write_stdout.invoke("")
        self.interface.on_write_stdout.paused = False

    def execute(self, **kwargs) -> int:
        ffmpeg_bin = shutil.which('ffmpeg')
        if ffmpeg_bin is None:
            self.interface.error("ffmpeg binary not found")
            return 1

        self.save_config()

        source_path = pathlib.Path(self.source.value)

        self.total_seconds = None
        self.current_file = source_path.stem

        command = (ffmpeg_bin,) + build_ffmpeg_command(source_path, self.crf.value, self.preset.value)
        self.interface.write_stdout(xappt.CommandRunner.command_sequence_to_string(command))

        with self.progress_callbacks():
            result = self.interface.run_subprocess(command)

        if result == 0:
            self.interface.message("Complete")
        else:
            self.interface.error(f"Error: process finished with error code {result}")

        return result
