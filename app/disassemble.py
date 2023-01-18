"""
Module for disassembling a video into chunks.
"""
import subprocess
from typing import Dict


def disassemble_video(input_file: str, output_dir: str) -> Dict:
    """
    Disassemble a video into chunks.
    """
    response: Dict = {}
    chunks = []
    try:
        # get video duration
        command = f"ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {input_file}"
        video_duration = float(
            subprocess.run(command, shell=True, stdout=subprocess.PIPE)
            .stdout.strip()
            .decode("utf-8")
        )
        # calculate number of chunks
        num_chunks = int(video_duration)
        # chunk video
        for i in range(num_chunks):
            output_file = f"{output_dir}/chunk_{i}.mkv"
            chunks.append(output_file)
            command = (
                f"ffmpeg -i {input_file} -ss {i} -t 1 -c:v libvpx-vp9 {output_file}"
            )
            subprocess.run(command, shell=True, check=True)
        # handle last chunk
        if video_duration > num_chunks:
            last_chunk_duration = video_duration - num_chunks
            output_file = f"{output_dir}/chunk_{num_chunks}.mkv"
            chunks.append(output_file)
            command = f"ffmpeg -i {input_file} -ss {num_chunks} -t {last_chunk_duration} -c:v libvpx-vp9 {output_file}"
            subprocess.run(command, shell=True, check=True)
        response["message"] = f"Video chunks: {chunks}"
    except subprocess.CalledProcessError as err:
        response["error"] = err.output
    return response
