from shutil import which

FFMPEG_COMMAND = "ffmpeg"


def find_ffmpeg() -> str | None:
    """Return the FFmpeg executable path, or None if unavailable."""
    return which(FFMPEG_COMMAND)
