FROM python:3.11

RUN apt-get update && apt-get install -y ffmpeg

COPY . /video_app
WORKDIR /video_app

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN mkdir -p ${HOME}/videos && \
    chmod 1777 ${HOME}/videos

ENV BASE_TMPFS_VIDEO_PATH ${HOME}/videos
ENV REDIS_HOST redis

WORKDIR /video_app/app

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]