"""
Get video information from redis.
"""

from typing import Dict

import config
import db


def get_video_information(video_id: str) -> Dict:
    """
    Get video information from redis hash.
    """
    if not db.does_video_metadata_exist_in_redis_hash(video_id, config.REDIS_HASH_NAME):
        return False

    video_information = db.get_video_metadata_from_redis_hash(
        video_id=video_id, hash_name=config.REDIS_HASH_NAME
    )
    return video_information
