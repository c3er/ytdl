import json
import os
import subprocess
import tempfile

import pytube
import pytube.helpers


class Video:
    def __init__(self, title, link):
        self.title = title
        self.link = link

    @property
    def filename(self):
        return pytube.helpers.safe_filename(self.title)

    @classmethod
    def collect(cls, path):
        with open(path, encoding="utf8") as f:
            return list(reversed([
                cls(v["title"], v["link"])
                for v in json.load(f)
            ]))

    def download(self, outdir, filename):
        streams = pytube.YouTube(self.link).streams
        video = (streams
            .filter(mime_type="video/mp4")
            .order_by('resolution')[-1])
        if video.includes_audio_track:
            video.download(output_path=outdir, filename=filename)
        else:
            with tempfile.TemporaryDirectory() as tmpdirname:
                video.download(output_path=tmpdirname, filename="video")
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
