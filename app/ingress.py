"""
Module for ingressing a video into the system.
"""

import os
import shutil
from typing import Dict

import config
import db
import decontainerize
import disassemble
import metadata
import transcode
import unique


def audio_codec(input_file: str) -> str:
    """
    Get the audio codec of the input file.

    If the audio codec is not found, return None.
    """

    try:
        return metadata.get_video_metadata(input_file)["audio_codec"]
    except KeyError:
        return None


def video_codec(input_file: str) -> str:
    """
    Get the video codec of the input file.
    """
    return metadata.get_video_metadata(input_file)["video_codec"]


def extract_audio(input_file: str, output_file: str) -> Dict:
    """
    Extract the audio from the input file.
    """
    decontainerize.extract_audio(input_file, output_file)


def extract_video(input_file: str, output_file: str) -> Dict:
    """
    Extract the video from the input file.
    """
    return decontainerize.extract_video(input_file, output_file)


def transcode_audio(input_file: str, output_file: str) -> Dict:
    """
    Transcode the audio to opus.
    """
    return transcode.transcode_to_opus(input_file, output_file)


def disassemble_video(input_file: str, output_file: str) -> Dict:
    """
    Disassemble the video to vp9.
    """
    return disassemble.disassemble_video(input_file, output_file)


def delete_video_ingress_directory(video_id: str) -> None:
    """
    Delete the video ingress directory after the video has been ingressed.
    This is recursive and will delete all the files and directories in the
    video upload directory.
    """
    video_directory = os.path.join(config.INGRESS_PATH, video_id)
    shutil.rmtree(video_directory)


def get_new_video_id() -> str:
    """
    Get a new video ID.
    """
    return unique.get_new_video_id()


def get_video_ingest_path(video_id: str) -> str:
    """
    Get the video ingest path.
    """
    video_directory = os.path.join(config.INGRESS_PATH, video_id)
    os.makedirs(video_directory, exist_ok=True)
    return os.path.join(video_directory, "video.mkv")


def ingress(input_file: str, video_id: str, file_name: str) -> Dict:
    """
    First we create a new video ID.

    Our target is to extract the audio and video from the input file, and
    check if the audio and video codecs are opus and vp9 respectively.

    If they are, we can just extract the audio and video. If not, we need
    transcode the audio and video to opus and vp9 respectively.

    After that we have a opus audio file and a vp9 video file.

    Then we disassemble the video file into a one second video file.
    Then we disassemble the audio file into a one second audio file.

    The last chunk in the disassembled file maybe less than one second as it
    is the last chunk and the file may be in decimal seconds example 100.5 seconds.

    Then we store these chunks into the redis time series.

    Then we store the video metadata into the redis stream.

    We finally return the video metadata and the video ID.
    """

    video_metadata = metadata.get_video_metadata(input_file)
    print("checking video metadata")
    print(video_metadata)
    video_metadata["video_id"] = video_id
    video_metadata["url"] = f"/video/{video_id}.webm"
    video_metadata["file_name"] = file_name

    # create a directory for with name as the video ID
    video_directory = os.path.join(config.INGRESS_PATH, video_id)
    os.makedirs(video_directory, exist_ok=True)

    # create a directory for the the extracted audio and video
    extracted_audio_video_directory = os.path.join(video_directory, "extracted")
    os.makedirs(extracted_audio_video_directory, exist_ok=True)

    # extract the audio and video
    extracted_output_audio_file = os.path.join(
        extracted_audio_video_directory, "audio.mkv"
    )
    extracted_output_video_file = os.path.join(
        extracted_audio_video_directory, "video.mkv"
    )
    extract_audio(input_file, extracted_output_audio_file)
    extract_video(input_file, extracted_output_video_file)

    transcoded_audio_video_directory = os.path.join(video_directory, "transcoded")
    os.makedirs(transcoded_audio_video_directory, exist_ok=True)

    transcoded_output_audio_file = os.path.join(
        transcoded_audio_video_directory, "audio.mkv"
    )

    if audio_codec(extracted_output_audio_file):

        if audio_codec(extracted_output_audio_file) != "opus":

            transcode_audio(extracted_output_audio_file, transcoded_output_audio_file)
        else:
            # copy the extracted audio file to the transcoded audio directory
            os.system(
                f"cp {extracted_output_audio_file} {transcoded_audio_video_directory}"
            )

    # create a directory for the disassembled audio and video
    # disassembled_audio_directory = os.path.join(
    #     video_directory, "disassembled", "audio"
    # )
    disassembled_video_directory = os.path.join(
        video_directory, "disassembled", "video"
    )
    # os.makedirs(disassembled_audio_directory, exist_ok=True)
    os.makedirs(disassembled_video_directory, exist_ok=True)

    # disassemble the audio and video
    # disassemble_audio(extracted_output_audio_file, disassembled_audio_directory)
    disassemble_video(extracted_output_video_file, disassembled_video_directory)

    # store the audio and video chunks into the redis time series
    status = db.add_video_chunk_to_redis_stream(
        video_id=video_metadata["video_id"], chunk_dir=disassembled_video_directory
    )
    print("status of adding video chunk to redis stream: ", status)

    if audio_codec(extracted_output_audio_file):
        status = db.add_audio_to_redis(
            video_id=video_metadata["video_id"], audio_file=transcoded_output_audio_file
        )
        print("status of adding audio to redis: ", status)

    status = db.add_video_metadata_to_redis_hash(
        video_metadata, hash_name=config.REDIS_HASH_NAME
    )
    print("status of adding video metadata to redis stream: ", status)

    # delete the video directory
    delete_video_ingress_directory(video_metadata["video_id"])

    return db.get_video_metadata_from_redis_hash(
        video_id=video_metadata["video_id"], hash_name=config.REDIS_HASH_NAME
    )
