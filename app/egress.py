"""
This module is responsible for egressing the video from redis and saving it as a file in
 the cache directory.
"""

import os
from typing import List

import assemble
import config
import containerize
import db
import information
import unique


def generate_all_integers_in_range(start: int, end: int) -> List:
    """
    Generate all the integers in a range.
    """
    return list(range(start, end + 1))


def generate_all_chunks_in_range(start: int, end: int) -> List:
    """
    Generate all the chunks in a range.
    """
    return [f"chunk_{i}" for i in generate_all_integers_in_range(start, end)]


def get_video_chunks(video_id: str) -> List:
    """
    Get all the video chunks for a video.
    """
    return db.get_video_chunks(video_id=video_id)


def save_audio_from_redis_as_file(video_id: str, output_file: str) -> None:
    """
    Save the audio from redis as a file.
    """
    file_data = db.get_audio(video_id=video_id)
    with open(output_file, "wb") as file:
        file.write(file_data)


def cut_audio_based_on_start_end_time(
    input_file: str, output_file: str, video_id: str, start: int, end: int
) -> None:
    """
    Cut the audio based on the start and end time using ffmpeg.
    The start and end time are in seconds.
    """
    duration = int(information.get_video_information(video_id=video_id)["duration"])

    if end == -1:
        end = duration

    ffmpeg_t = f"-t {end - start + 1}" if end != duration else ""

    os.system(f"ffmpeg -i {input_file} -ss {start} {ffmpeg_t} -c copy {output_file}")


def save_chunks_as_file(
    video_id: str, video_chunk_dir: str, start: int, end: int
) -> List:
    """
    Save all the video and audio chunks as files.
    """
    if end == -1:
        end = int(information.get_video_information(video_id=video_id)["duration"])

    required_chunks = generate_all_chunks_in_range(start, end)

    # save video chunks
    for video_chunk in get_video_chunks(video_id=video_id):

        chunk_id, chunk = list(video_chunk[1].items())[0]
        chunk_id = chunk_id.decode("utf-8")

        if chunk_id not in required_chunks:
            continue

        file_path = f"{video_chunk_dir}/{chunk_id}.mkv"
        with open(file_path, "wb") as file:
            file.write(chunk)

    return required_chunks


def egress(video_id: str, start: int, end: int) -> str:
    """
    Egress the video from redis and save it as a file in the cache directory.

    Returns the path to the video file.
    """

    # create temporary directory
    egress_dir = os.path.join(config.EGRESS_PATH, unique.get_new_fetch_id())
    os.mkdir(egress_dir)

    # create audio and video chunk directory
    audio_chunk_dir = os.path.join(egress_dir, "chunks", "audio")
    video_chunk_dir = os.path.join(egress_dir, "chunks", "video")
    os.makedirs(audio_chunk_dir)
    os.makedirs(video_chunk_dir)

    # create directory to store these assembled chunks
    assembled_chunk_dir = os.path.join(egress_dir, "assembled")
    os.mkdir(assembled_chunk_dir)

    # create directory to store the final containerized video
    containerized_video_dir = os.path.join(egress_dir, "containerized")
    os.mkdir(containerized_video_dir)

    # create the cache directory for this video if it doesn't exist
    cache_directory = os.path.join(config.CACHE_PATH, video_id)
    if not os.path.exists(cache_directory):
        os.mkdir(cache_directory)

    # save all the chunks as files
    chunks = save_chunks_as_file(
        video_id=video_id,
        video_chunk_dir=video_chunk_dir,
        start=start,
        end=end,
    )

    # chunks will have the format chunk_1, chunk_2, chunk_3 etc.
    # we need to sort them in ascending order by the number
    chunks.sort(key=lambda x: int(x.split("_")[1]))

    # assemble the chunks
    # assembled video path
    assembled_video_path = os.path.join(assembled_chunk_dir, "video.mkv")
    video_input_txt_path = os.path.join(assembled_chunk_dir, "video_input.txt")

    # assemble the video chunks
    assemble.concatenate_videos(
        video_files=[os.path.join(video_chunk_dir, chunk + ".mkv") for chunk in chunks],
        output_file=assembled_video_path,
        video_input_txt_path=video_input_txt_path,
    )

    if information.get_video_information(video_id=video_id).get("audio_codec"):

        full_audio_path = os.path.join(assembled_chunk_dir, "full_audio.mkv")
        save_audio_from_redis_as_file(
            video_id=video_id,
            output_file=full_audio_path,
        )

        cut_audio_path = os.path.join(assembled_chunk_dir, "cut_audio.webm")
        cut_audio_based_on_start_end_time(
            input_file=full_audio_path,
            output_file=cut_audio_path,
            video_id=video_id,
            start=start,
            end=end,
        )

    else:
        cut_audio_path = None

    # containerize the video
    containerized_video_path = os.path.join(containerized_video_dir, "video.webm")
    containerize.mux_audio_video(
        audio_file=cut_audio_path,
        video_file=assembled_video_path,
        output_file=containerized_video_path,
    )

    # move the containerized video to cache directory

    # cache video should have the format video_id_start_end.webm
    # if start is 0 and end is -1 then it should be video_id.webm
    # if start is 0 and end is 10 then it should be video_id_0_10.webm
    # if start is 10 and end is 20 then it should be video_id_10_20.webm
    # if start is 20 and end is -1 then it should be video_id_20_{duration}.webm

    if start == 0 and end == -1:
        cache_video_path = os.path.join(cache_directory, f"{video_id}.webm")
    elif start == 0:
        cache_video_path = os.path.join(
            cache_directory, f"{video_id}_{start}_{end}.webm"
        )
    elif end == -1:
        end = information.get_video_information(video_id=video_id)["duration"]
        cache_video_path = os.path.join(
            cache_directory, f"{video_id}_{start}_{end}.webm"
        )
    else:
        cache_video_path = os.path.join(
            cache_directory, f"{video_id}_{start}_{end}.webm"
        )

    # move the containerized video to cache directory
    os.system(f"mv {containerized_video_path} {cache_video_path}")

    # delete the temporary directory
    os.system(f"rm -rf {egress_dir}")

    return cache_video_path


def requested_video_in_cache(video_id: str, start: int, end: int) -> str:
    """
    Check if the requested video is in the cache directory.

    Returns the path to the video file if it is in the cache directory.
    """

    # cache video should have the format video_id_start_end.webm
    # if start is 0 and end is -1 then it should be video_id.webm
    # if start is 0 and end is 10 then it should be video_id_0_10.webm
    # if start is 10 and end is 20 then it should be video_id_10_20.webm
    # if start is 20 and end is -1 then it should be video_id_20_{duration}.webm

    cache_directory = os.path.join(config.CACHE_PATH, video_id)

    if not os.path.exists(cache_directory):
        return None

    if start == 0 and end == -1:
        cache_video_path = os.path.join(cache_directory, f"{video_id}.webm")
    elif start == 0:
        cache_video_path = os.path.join(
            cache_directory, f"{video_id}_{start}_{end}.webm"
        )
    elif end == -1:
        end = information.get_video_information(video_id=video_id)["duration"]
        cache_video_path = os.path.join(
            cache_directory, f"{video_id}_{start}_{end}.webm"
        )
    else:
        cache_video_path = os.path.join(
            cache_directory, f"{video_id}_{start}_{end}.webm"
        )

    # check if file exist if it does then return it
    if os.path.isfile(cache_video_path):
        return cache_video_path

    return None
