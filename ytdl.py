import math
import os
import sys
import traceback

import video


starterdir = os.path.dirname(os.path.realpath(sys.argv[0]))


def log(*msg, sep=" ", end="\n", file=sys.stdout):
    print(*msg, sep=sep, end=end, file=file)
    file.flush()


def error(*msg, shall_exit=True):
    log(*msg, file=sys.stderr)
    if shall_exit:
        sys.exit(1)


def download_progress_handler(fileinfo, completed, remaining):
    log(f'{fileinfo.filetype.label.title()}: "{fileinfo.path}"\t{(completed / (remaining + completed)) * 100}%')


def download_completed_handler(fileinfo):
    log(f'"{fileinfo.path}" downloaded')


def main():
    try:
        outdir = sys.argv[1]
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
