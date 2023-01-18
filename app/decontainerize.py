"""
Extract audio and video from a video file.
"""

import subprocess
from typing import Dict


def extract_audio(input_file: str, output_file: str) -> Dict:
    """
    Extract audio from video file.
    """
    response: Dict = {}
    try:
        command = f"ffmpeg -i {input_file} -vn -acodec copy {output_file}"
        subprocess.run(command, shell=True, check=True)
        response["message"] = "Audio extracted successfully"
    except subprocess.CalledProcessError as err:
        response["error"] = err.output
    return response


def extract_video(input_file: str, output_file: str) -> Dict:
    """
    Extract video from video file.
    """
    response: Dict = {}
    try:
        command = f"ffmpeg -i {input_file} -an -vcodec copy {output_file}"
        subprocess.run(command, shell=True, check=True)
        response["message"] = "Video extracted successfully"
    except subprocess.CalledProcessError as err:
        response["error"] = err.output
    return response
