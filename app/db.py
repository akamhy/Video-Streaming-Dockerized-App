"""
Database module. Contains functions to interact with Redis.
"""

import json
import os
from typing import Any, Dict

import redis

import config

# Connect to Redis
r = redis.Redis()
r = redis.Redis(host=config.REDIS_HOST, port=6379, db=0)


def add_video_metadata_to_redis_hash(video_metadata: Dict, hash_name: str) -> bool:
    """
    Add video metadata to redis hash.
    """
    try:
        r.hset(
            name=hash_name,
            key=video_metadata["video_id"],
            value=json.dumps(video_metadata),
        )
        return True
    except Exception:
        return False


def delete_video_metadata_from_redis_hash(video_id: str, hash_name: str) -> bool:
    """
    Delete video metadata from redis hash.

    """
    try:
        r.hdel(hash_name, video_id)
        return True
    except Exception:
        return False


def delete_redis_hash(hash_name: str) -> bool:
    """
    Delete redis hash.

    """
    try:
        r.delete(hash_name)
        return True
    except Exception:
        return False


def get_video_metadata_from_redis_hash(video_id: str, hash_name: str) -> Dict:
    """
    Get video metadata from redis hash.

    """
    try:
        return json.loads(r.hget(name=hash_name, key=video_id))
    except Exception:
        return {}


def does_video_metadata_exist_in_redis_hash(video_id: str, hash_name: str) -> bool:
    """
    Check if video metadata exists in redis hash.

    """
    try:
        return r.hexists(name=hash_name, key=video_id)
    except Exception:
        return False


def get_all_video_metadata_from_redis_hash(hash_name: str) -> Dict:
    """
    Get all video metadata from redis hash.

    """
    try:
        video_metadata = r.hgetall(name=hash_name)
        return {k.decode(): json.loads(v.decode()) for k, v in video_metadata.items()}
    except Exception:
        return {}


def add_video_chunk_to_redis_stream(video_id: str, chunk_dir: str) -> bool:
    """
    Add video chunks to redis stream.
    """
    try:
        chunk_files = sorted(os.listdir(chunk_dir))
        for chunk_file in chunk_files:
            chunk_id = chunk_file.split(".")[0].split("_")[1]
            with open(chunk_dir + "/" + chunk_file, "rb") as file:
                chunk = file.read()
            r.xadd(
                name=f"video_{video_id}",
                fields={f"chunk_{chunk_id}": chunk},
            )
        return True
    except Exception:
        return False


def add_audio_to_redis(video_id: str, audio_file: str) -> bool:
    """
    Add audio to redis.
    """
    try:
        key = f"audio_{video_id}"
        with open(audio_file, "rb") as file:
            value = file.read()
        r.set(key, value)
        return True
    except Exception:
        return False


def get_video_chunks(video_id: str) -> Dict:
    """
    Get video chunks by chunk_id range from redis stream.

    """

    try:
        video_chunks = r.xrange(name=f"video_{video_id}", min="-", max="+")
    except Exception:
        return {}
    return video_chunks


def get_audio(video_id: str) -> Any:
    """
    Get audio redis
    """
    try:
        return r.get(f"audio_{video_id}")
    except Exception:
        return None


def delete_redis_stream(stream_name: str) -> bool:
    """
    Delete redis stream.
    """
    try:
        r.delete(stream_name)
    except Exception:
        return False
    return True
