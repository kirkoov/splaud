from .ffmpeg import find_ffmpeg


def main() -> None:
    ffmpeg = find_ffmpeg()

    if ffmpeg is None:
        print("FFmpeg was not found.")
        return

    print(f"FFmpeg found: {ffmpeg}")
