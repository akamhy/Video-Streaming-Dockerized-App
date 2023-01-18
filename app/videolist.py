"""
Module for getting all video information.
"""

from typing import Dict

import config
import db


def get_all_video_information() -> Dict:
    """
    Get all video information from redis hash.
    """
    video_information = db.get_all_video_metadata_from_redis_hash(
        hash_name=config.REDIS_HASH_NAME
    )
    return video_information
