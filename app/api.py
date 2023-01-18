"""
API for video streaming that stores the video as chunks in redis and serves the video after re-assembling the chunks.
"""
from fastapi import FastAPI, File, Request, UploadFile
from fastapi.exceptions import HTTPException
from fastapi.responses import FileResponse, RedirectResponse

import delete
import egress
import information
import ingress
import videolist

app = FastAPI()

app = FastAPI(
    title="Video Streaming API",
    description="API for video streaming that stores the video as \
        chunks in redis and serves the video after re-assembling the chunks.",
)


@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    """
    Redirect to docs if 404.
    """
    return RedirectResponse("/docs")


@app.post("/video/ingest")
def ingest_video(video: UploadFile = File(...)):
    """
    Ingest video file. Returns video metadata.
    """
    video_id = ingress.get_new_video_id()
    video_file_ingest_path = ingress.get_video_ingest_path(video_id)
    file_name = video.filename

    try:
        contents = video.file.read()
        with open(video_file_ingest_path, "wb") as upload_file:
            upload_file.write(contents)
    except Exception:
        return {"message": "There was an error ingesting the file"}
    finally:
        video.file.close()

    data = ingress.ingress(video_file_ingest_path, video_id, file_name)
    data["message"] = "Video ingested successfully"

    return data


@app.get("/video/all")
def list_all_videos():
    """
    Get all video metadata.
    """
    return videolist.get_all_video_information()


@app.get("/video/{video_id}.webm")
def egest_video(video_id: str, start: int = 0, end: int = -1):
    """
    Get video file.
    Start and end are in seconds. Start and end are optional.
    Start and end are inclusive.
    """

    # check if video exists
    video_information = information.get_video_information(video_id)
    if not video_information:
        return {"message": "Video not found"}

    # check if start and end are valid
    if start < 0 or end < -1:
        return {
            "message": "Invalid start and end values start must be >= 0 and end must be >= -1"
        }

    if end != -1 and start > end:
        return {"message": "Invalid start and end values start must be <= end"}

    # check if start and end are within video duration
    if start > video_information["duration"] or end > video_information["duration"]:
        return {
            "message": f"Invalid start and end values start and end must be <= video duration. Video duration is {video_information['duration']}"
        }

    # check cache before making request to redis
    cached_video = egress.requested_video_in_cache(video_id, start, end)
    if cached_video:
        return FileResponse(cached_video)

    requested_video_file_path = egress.egress(video_id, start, end)
    return FileResponse(requested_video_file_path)


@app.get("/video/{video_id}/information")
def get_video_information(video_id: str):
    """
    Get video metadata.
    """

    video_information = information.get_video_information(video_id)
    if video_information:
        return video_information

    return {"message": "Video not found"}


@app.delete("/video/{video_id}")
def delete_video(video_id: str):
    """
    Delete video and all its metadata, audio and video chunks.
    """

    # check if video exists
    video_information = information.get_video_information(video_id)
    if not video_information:
        return {"message": "Video not found"}

    if delete.delete_video_metadata_and_audio_video_chunks(video_id):
        return {"message": "Video deleted"}

    return {"message": "Video could not be deleted"}
