import datetime
import math
import os
import sys
import traceback

import progress
import video


starterdir = os.path.dirname(os.path.realpath(sys.argv[0]))

_bandwidth = None


class Bandwidth:
    MICROSECOND = 1000000

    def __init__(self):
        self.completed = 0
        self.per_second = 0
        self._chunks_per_second = 0
        self._time = self._oldtime = datetime.datetime.now()

    def update(self, completed):
        time = datetime.datetime.now()
        if (time - self._oldtime).seconds < 1:
            self._chunks_per_second += completed - self.completed
        else:
            self._oldtime = time
            self.per_second = self._chunks_per_second
            self._chunks_per_second = 0
        self.completed = completed
        return self.per_second


def log(*msg, sep=" ", end="\n", file=sys.stdout):
    print(*msg, sep=sep, end=end, file=file)
    file.flush()


def error(*msg, shall_exit=True):
    progress.complete()
    log(*msg, file=sys.stderr)
    if shall_exit:
        sys.exit(1)


def download_progress_handler(fileinfo, completed, remaining):
    progress.progress(
        completed,
        remaining + completed,
        f"{_bandwidth.update(completed) / 1024 :.2f} kB/s")


def download_completed_handler(fileinfo):
    progress.complete(f'"{fileinfo.path}" downloaded')


def main():
    global _bandwidth
    try:
        outdir = sys.argv[1]
        _bandwidth = Bandwidth()
        videos = video.Video.collect(
            os.path.join(starterdir, "videos.json"),
            download_progress_handler,
            download_completed_handler)
        video_count = len(videos)
        digit_count = int(math.log10(video_count)) + 1
        log(f"Downloading {video_count} videos...")
        if not os.path.exists(outdir):
            os.mkdir(outdir)
        for i, v in enumerate(videos):
            filename = f"{str(i + 1).rjust(digit_count, '0')} {v.filename}"
            if os.path.exists(os.path.join(outdir, f"{filename}.mp4")):
                log(f'Video "{v.title}" does already exist.')
                continue
            log(f'Download video "{v.title}"...')
            try:
                v.download(outdir, filename)
            except Exception:
                error("Error", shall_exit=False)
                error(traceback.format_exc())
    except KeyboardInterrupt:
        error("Aborted")


if __name__ == "__main__":
    main()
