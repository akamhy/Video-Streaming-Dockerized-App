"""
Module for assembling videos.
Concatenate videos using the concat demuxer.
"""

import subprocess
from typing import List


def concatenate_videos(
    video_files: List[str], output_file: str, video_input_txt_path: str
):
    """
    Concatenate videos using the concat demuxer.
    """

    # Create a text file with a list of videos to concatenate
    with open(video_input_txt_path, "w", encoding="utf-8") as txt_file:
        for video in video_files:
            txt_file.write(f"file '{video}'\n")

    # Concatenate the videos using the concat demuxer
    subprocess.call(
        [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            video_input_txt_path,
            "-c",
            "copy",
            output_file,
        ]
    )
