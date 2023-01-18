# Video Streaming Dockerized App
## Video Streaming API
API for video streaming that stores the video as chunks in redis and serves the video after re-assembling the chunks.

The app will expose port 8000 to the host, redis and the app share the same network.

![Screenshot of Video Streaming Dockerized App](https://user-images.githubusercontent.com/64683866/213198470-29f7a615-f087-4156-b3bd-ad1f7824bed5.png)



### How to start

Run:
```bash
docker compose up -d
```

Then open:

<http://localhost:8000> or <http://[::1]:8000>

### How to stop

```bash
docker compose down
```



Sample video to test the sync of audio and video: <https://www.youtube.com/watch?v=U03lLvhBzOw>
