import enum
import json
import os
import subprocess
import tempfile

import pytube
import pytube.helpers


_on_download_progress = None
_on_download_completed = None


class FileType(enum.Enum):
    VIDEO = enum.auto()
    AUDIO = enum.auto()
    UNKNOWN = enum.auto()

    @property
    def label(self):
        return {
            self.VIDEO: "video",
            self.AUDIO: "audio",
            self.UNKNOWN: "unknown",
        }[self]


class FileInfo:
    def __init__(self):
        self.filetype = FileType.UNKNOWN
        self.path = ""

    def set(self, filetype, path):
        self.filetype = filetype
        self.path = path


class Video:
    _fileinfo = FileInfo()

    def __init__(self, title, link):
        self.title = title
        self.link = link

    @property
    def filename(self):
        return pytube.helpers.safe_filename(self.title)

    @classmethod
    def collect(cls, path, progress_handler, completed_handler):
        cls._register_handlers(progress_handler, completed_handler)
        with open(path, encoding="utf8") as f:
            return list(reversed([
                cls(v["title"], v["link"])
                for v in json.load(f)
            ]))

    def download(self, outdir, filename):
        streams = pytube.YouTube(
            self.link,
            on_progress_callback=_on_download_progress,
            on_complete_callback=_on_download_completed
        ).streams

        video = (streams
            .filter(mime_type="video/mp4")
            .order_by('resolution')[-1])

        if video.includes_audio_track:
            self._fileinfo.set(FileType.VIDEO, os.path.join(outdir, f"{filename}"))
            video.download(output_path=outdir, filename=filename)
        else:
            with tempfile.TemporaryDirectory() as tmpdirname:
                self._fileinfo.set(FileType.VIDEO, os.path.join(tmpdirname, "video.mp4"))
                video.download(output_path=tmpdirname, filename="video")

                self._fileinfo.set(FileType.AUDIO, os.path.join(tmpdirname, "audio.mp4"))
                (streams
                    .get_audio_only()
                    .download(output_path=tmpdirname, filename="audio"))

                # Based on https://stackoverflow.com/a/11783474
                # How to add a new audio (not mixing) into a video using ffmpeg?
                subprocess.run([
                    "ffmpeg",
                    "-hide_banner",
                    "-loglevel", "warning",
                    "-i", os.path.join(tmpdirname, "video.mp4"),
                    "-i", os.path.join(tmpdirname, "audio.mp4"),
                    "-codec", "copy",
                    "-shortest",
                    os.path.join(outdir, f"{filename}.mp4")
                ])

    @classmethod
    def _register_handlers(cls, progress_handler, completed_handler):
        global _on_download_progress
        global _on_download_completed

        completed = 0

        def on_progress_callback(stream, chunk, bytes_remaining):
            nonlocal completed
            completed += len(chunk)
            progress_handler(cls._fileinfo, completed, bytes_remaining)

        def on_complete_callback(stream, file_path):
            completed_handler(cls._fileinfo)

        _on_download_progress = on_progress_callback
        _on_download_completed = on_complete_callback
