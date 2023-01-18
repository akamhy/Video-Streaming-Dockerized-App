"""
Module for getting metadata of videos.
"""

import json
import subprocess
from datetime import datetime
from typing import Dict


def get_video_metadata(file_path: str) -> Dict:
    """
    Get video metadata using ffprobe.
    """
    try:
        command = f"ffprobe -v quiet -print_format json -show_format -show_streams {file_path}"
        output = subprocess.check_output(command, shell=True)
        output = json.loads(output)
    except Exception as err:
        return {"error": f"An error occurred while getting video metadata: {err}"}

    video_metadata: Dict = {}
    video_metadata["duration"] = None
    video_metadata["video_codec"] = None
    video_metadata["audio_codec"] = None
    video_metadata["resolution"] = None
    video_metadata["fps"] = None
    video_metadata["timestamp"] = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    for stream in output["streams"]:
        if stream["codec_type"] == "video":
            video_metadata["video_codec"] = stream["codec_name"]
            video_metadata["resolution"] = f"{stream['width']}x{stream['height']}"
            video_metadata["fps"] = int(eval(stream.get("avg_frame_rate", None)))
        elif stream["codec_type"] == "audio":
            video_metadata["audio_codec"] = stream["codec_name"]
    video_metadata["duration"] = int(float(output["format"]["duration"]))

    return video_metadata
