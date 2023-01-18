"""
This module contains functions for generating unique IDs and related values.
"""

import uuid


def generate_uuid() -> str:
    """
    Generate a new UUID, and return it as a string.
    """
    return str(uuid.uuid4())


def get_new_video_id() -> str:
    """
    Generate a new video ID, from a UUID without '-' characters.
    """
    return generate_uuid().replace("-", "")


def get_new_fetch_id() -> str:
    """
    Generate a new fetch ID, from a UUID without '-' characters.
    """
    return generate_uuid().replace("-", "")
