import os
import sys
import traceback

import video


starterdir = os.path.dirname(os.path.realpath(sys.argv[0]))


def log(*msg, sep=" ", end="\n", file=sys.stdout):
    print(*msg, sep=sep, end=end, file=file)
    file.flush()


def main():
    outdir = sys.argv[1]
    videos = video.Video.collect(os.path.join(starterdir, "videos.json"))
    video_count = len(videos)
    digit_count = len(str(video_count))
    log(f"Downloading {video_count} videos...")
    for i, v in enumerate(videos):
        filename = f"{str(i + 1).rjust(digit_count, '0')} {v.filename}"
        if os.path.exists(os.path.join(outdir, f"{filename}.mp4")):
            log(f'Video "{v.title}" does already exist.')
            continue
        log(f'Download video "{v.title}"...', end="\t")
        try:
            v.download(outdir, filename)
            log("Done")
        except Exception:
            log("Error", file=sys.stderr)
            log(traceback.format_exc(), file=sys.stderr)



if __name__ == "__main__":
    main()
