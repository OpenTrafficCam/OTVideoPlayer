import datetime
from pathlib import Path

import cv2

from helpers import _get_datetime_from_filename


class VideoCapture:
    def __init__(self, video_path=0):
        # Open the video source
        self.capture = cv2.VideoCapture(video_path)
        if not self.capture.isOpened():
            raise ValueError("Unable to open video source", video_path)

        # Get video source width and height
        self.width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.fps = self.capture.get(cv2.CAP_PROP_FPS)
        self.start_time = _get_datetime_from_filename(str(Path(video_path).name))
        self.get_current_time()
        self.total_frames = self.capture.get(cv2.CAP_PROP_FRAME_COUNT)

    def get_current_time(self):
        self.current_frame = self.capture.get(cv2.CAP_PROP_POS_FRAMES)
        self.current_time = self.start_time + datetime.timedelta(
            seconds=(self.current_frame - 1) / self.fps
        )

    def get_frame(self, frame_number=None):
        if not self.capture.isOpened():
            return (ret, None)
        if frame_number:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
        ret, frame = self.capture.read()
        self.get_current_time()
        return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) if ret else (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.capture.isOpened():
            self.capture.release()
