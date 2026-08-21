import subprocess
from pathlib import Path

from splaud.ffmpeg import find_ffmpeg

from .chapters import Chapter, get_chapters


def format_duration(seconds: float) -> str:
    """Format seconds as HH:MM:SS."""
    total_seconds = int(seconds)
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def warn_long_chapters(
    chapters: list[Chapter],
    threshold: float = 3600,
) -> None:
    """Warn about chapters that may take considerable processing time."""
    long_chapters = [chapter for chapter in chapters if chapter.duration > threshold]

    if not long_chapters:
        return

    print(
        f"\nWARNING: {len(long_chapters)} chapter(s) "
        "may take considerable processing time:"
    )

    for chapter in long_chapters:
        print(
            f"  {chapter.index:2}: {format_duration(chapter.duration)} {chapter.title}"
        )

    print()


def split_fixed(
    input_file: Path,
    output_file: Path,
    duration: int,
    ffmpeg: str,
) -> None:
    """Create one fixed-duration audio chunk."""
    command = [
        ffmpeg,
        "-hide_banner",
        "-i",
        str(input_file),
        "-map",
        "0:a:0",
        "-map",
        "0:v:0?",
        "-c",
        "copy",
        "-t",
        str(duration),
        str(output_file),
    ]

    subprocess.run(command, check=True)


def split_chapter(
    input_file: Path,
    output_file: Path,
    chapter: Chapter,
    ffmpeg: str,
) -> None:
    """Create one audio file from a chapter."""
    command = [
        ffmpeg,
        "-hide_banner",
        "-ss",
        str(chapter.start),
        "-i",
        str(input_file),
        "-map",
        "0:a:0",
        "-map",
        "0:v:0?",
        "-c",
        "copy",
        "-metadata",
        "title=" + chapter.title,
        "-t",
        str(chapter.duration),
        str(output_file),
    ]

    subprocess.run(command, check=True)


def split_chapters(
    input_file: Path,
    output_dir: Path,
) -> None:
    """Split an audio file into one file per embedded chapter."""
    ffmpeg = find_ffmpeg()

    if ffmpeg is None:
        print("FFmpeg was not found.")
        return

    chapters = get_chapters(input_file)
    warn_long_chapters(chapters)

    if not chapters:
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    for number, chapter in enumerate(chapters):
        print(
            f"[{number}/{len(chapters)}] "
            f"{chapter.title} "
            f"({format_duration(chapter.duration)})"
        )

        output_file = output_dir / f"chapter-{number:03d}{input_file.suffix}"
        split_chapter(input_file, output_file, chapter, ffmpeg)
