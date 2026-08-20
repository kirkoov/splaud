import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chapter:
    index: int
    title: str
    start: float
    end: float

    @property
    def duration(self) -> float:
        return self.end - self.start


def get_chapters(input_file: Path) -> list[Chapter]:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-print_format",
        "json",
        "-show_chapters",
        str(input_file),
    ]

    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )

    data = json.loads(result.stdout)

    return [
        Chapter(
            index=chapter["id"],
            title=chapter.get("tags", {}).get("title", ""),
            start=float(chapter["start_time"]),
            end=float(chapter["end_time"]),
        )
        for chapter in data.get("chapters", [])
    ]
