from aiortc import VideoStreamTrack
from av import VideoFrame
import cv2
from cam import Camera

camera = Camera()

class CameraStreamTrack(VideoStreamTrack):
    async def recv(self):
        pts, time_base = await self.next_timestamp()

        frame = camera.read()
        if frame is None:
            return None

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        video_frame = VideoFrame.from_ndarray(frame, format="rgb24")
        video_frame.pts = pts
        video_frame.time_base = time_base

        return video_frame