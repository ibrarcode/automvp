"""
Caption rendering using FFmpeg + ASS subtitles (moviepy removed).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple, Optional
import subprocess
import tempfile
import time

from app.ass_renderer import build_ass


def render_captions(
    video_path: str | Path,
    captions: List[Dict],
    style_key: str,
    output_path: str | Path,
    position: str | None = None,  # kept for backward compatibility
    position_xy: Tuple[float, float] | None = None,
    fast: bool = True,
    target_width: int = 1280,
    mode: Optional[str] = None,  # ignored; for backward compatibility
) -> Dict:
    """
    Burn captions onto video using FFmpeg and ASS.
    Returns dict with output path and duration seconds.
    """
    started_at = time.perf_counter()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as td:
        ass_path = Path(td) / "captions.ass"
        build_ass(captions, style_key, ass_path, pos_xy=position_xy)

        vf_parts = []
        if fast and target_width:
            vf_parts.append(f"scale='min({target_width},iw)':-2")
        vf_parts.append(f"subtitles=filename='{ass_path.as_posix()}'")
        vf = ",".join(vf_parts)

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vf",
            vf,
            "-c:v",
            "libx264",
            "-preset",
            "ultrafast" if fast else "medium",
            "-crf",
            "18",
            "-c:a",
            "copy",
            str(output_path),
        ]
        subprocess.run(cmd, check=True)

    duration = time.perf_counter() - started_at
    return {"output_path": output_path, "burn_seconds": duration}
