import json
import os
import sys

import pytube


starterdir = os.path.dirname(os.path.realpath(sys.argv[0]))


class Video:
    def __init__(self, title, link):
        self.title = title
        self.link = link

    @property
    def filename(self):
        forbidden = {
            "/": "-",
            "\\": "-",
            ":": ";",
            "*": "~",
            "?": "",
            '"': "",
            "'": "",
            ",": "",
            "<": "(",
            ">": ")",
            "|": "@",
        }
        chars = list(self.title)
        for i, c in enumerate(chars):
            if c in forbidden.keys():
                chars[i] = forbidden[c]
        return f"{''.join(chars)}"

    @classmethod
    def collect(cls, path):
        datafile = os.path.join(starterdir, path)
        with open(datafile, encoding="utf8") as f:
            return list(reversed([
                cls(v["title"], v["link"])
                for v in json.load(f)
            ]))


def log(*msg, sep=" ", end="\n"):
    print(*msg, sep=sep, end=end)
    sys.stdout.flush()


def main():
    outdir = sys.argv[1]
    videos = Video.collect(os.path.join(starterdir, "videos.json"))
    video_count = len(videos)
    digit_count = len(str(video_count))
    log(f"Downloading {video_count} videos...")
    for i, v in enumerate(videos):
        filename = f"{str(i + 1).rjust(digit_count, '0')} {v.filename}"
        if os.path.exists(os.path.join(outdir, f"{filename}.mp4")):
            log(f'Video "{v.title}" does already exist.')
            continue
        log(f'Download video "{v.title}"...', end="\t")
        (pytube.YouTube(v.link)
            .streams
            .filter(mime_type="video/mp4")
            .order_by("audio_codec")
            .order_by('resolution')[-1]
            .download(output_path=outdir, filename=filename))
        log("Done")


if __name__ == "__main__":
    main()
