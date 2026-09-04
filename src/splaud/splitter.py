import subprocess
from pathlib import Path

from splaud.ffmpeg import find_ffmpeg

from .chapters import Chapter, get_chapters

FRAME_PRE_ROLL = 0.026


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
    duration: float,
    ffmpeg: str,
    start: int = 0,
    title: str | None = None,
) -> None:
    """Create one fixed-duration audio chunk."""
    seek = max(0, start - FRAME_PRE_ROLL)

    command = [
        ffmpeg,
        "-hide_banner",
        "-ss",
        str(seek),
        "-i",
        str(input_file),
        "-map",
        "0:a:0",
        "-map",
        "0:v:0?",
        "-c",
        "copy",
    ]

    if title is not None:
        command.extend(["-metadata", f"title={title}"])

    command.extend(
        [
            "-t",
            str(duration),
            str(output_file),
        ]
    )
    subprocess.run(command, check=True)


def split_fixed_chunks(
    input_file: Path,
    output_dir: Path,
    duration: int,
    ffmpeg: str,
    adjustment: int = 0,
) -> None:
    """Split an audio file into fixed-duration chunks."""
    output_dir = output_dir / input_file.stem
    output_dir.mkdir(parents=True, exist_ok=True)

    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        str(input_file),
    ]

    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )

    total_duration = float(result.stdout)
    chunk_count = int((total_duration + duration - 1) // duration)

    for number in range(chunk_count):
        start = number * duration

        if number > 0:
            start += adjustment

        chunk_duration = min(
            duration - adjustment if number > 0 else duration,
            total_duration - start,
        )

        print(
            f"[{number}/{chunk_count}] "
            f"{input_file.name} "
            f"({format_duration(min(duration, total_duration - start))})"
        )

        output_file = output_dir / f"chunk-{number:03d}{input_file.suffix}"

        split_fixed(
            input_file,
            output_file,
            chunk_duration,
            ffmpeg,
            start,
            output_file.stem,
        )


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
