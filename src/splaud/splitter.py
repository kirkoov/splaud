import subprocess
from pathlib import Path


def split_fixed(
    input_file: Path,
    output_file: Path,
    duration: int,
) -> None:
    """Create one fixed-duration audio chunk."""
    command = [
        "ffmpeg",
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
