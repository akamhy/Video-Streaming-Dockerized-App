"""
This file contains the configuration for the application.
"""

import os

# When we upload the video we first store it in the tmpfs directory
# for processing as it is faster than storing it on the disk.
# Once the video is processed we move it to the redis database.
# When the request is made to download the video we move the video
# from the redis database to the tmpfs directory and then process
# it and serve it to the user.
BASE_TMPFS_VIDEO_PATH = os.getenv("BASE_TMPFS_VIDEO_PATH", "/tmp/videos")


INGRESS_PATH = os.path.join(BASE_TMPFS_VIDEO_PATH, "ingress")
EGRESS_PATH = os.path.join(BASE_TMPFS_VIDEO_PATH, "egress")


# To cache request, we don't want to process the video again and again.
# But need to delete the cache after a certain time.
# So first we check if the video is in the cache, if it is we serve it.
# If it is not we process the request and store it in the cache.
CACHE_PATH = os.path.join(BASE_TMPFS_VIDEO_PATH, "cache")

# Make sure the directories exist
os.makedirs(INGRESS_PATH, exist_ok=True)
os.makedirs(EGRESS_PATH, exist_ok=True)
os.makedirs(CACHE_PATH, exist_ok=True)


# REDIS CONFIGURATION

# The redis database is used to store the video metadata and list of videos.
REDIS_HASH_NAME = "redis_video_list"
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
