"""
Module to delete video metadata, audio and video chunks from redis.
"""

import config
import db


def delete_video_metadata_and_audio_video_chunks(video_id: str) -> bool:
    """
    Delete video from redis hash and chunks in the redis stream.
    """
    status_metadata = db.delete_video_metadata_from_redis_hash(
        video_id=video_id, hash_name=config.REDIS_HASH_NAME
    )
    video_chunk_stream_name = f"video_{video_id}"
    status_video = db.delete_redis_stream(stream_name=video_chunk_stream_name)

    audio_chunk_stream_name = f"audio_{video_id}"
    status_audio = db.delete_redis_stream(stream_name=audio_chunk_stream_name)

    return status_metadata and status_video and status_audio
