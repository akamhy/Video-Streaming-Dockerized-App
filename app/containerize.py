"""
This module contains the functions to containerize the video and audio files.
Just simple muxing of the audio and video files.
"""

import subprocess


def mux_audio_video(audio_file: str, video_file: str, output_file: str) -> bool:
    """
    Mux audio and video files.
    """
    # generate the muxing command
    if not audio_file:
        mux_cmd = [
            "ffmpeg",
            "-i",
            video_file,
            "-c:v",
            "copy",
            "-y",
            output_file,
        ]
    else:
        mux_cmd = [
            "ffmpeg",
            "-i",
            audio_file,
            "-i",
            video_file,
            "-c:v",
            "copy",
            "-c:a",
            "copy",
            "-y",
            output_file,
        ]

    # run the muxing command
    try:
        subprocess.run(mux_cmd, check=True)
        return True
    except subprocess.CalledProcessError:
        return False
