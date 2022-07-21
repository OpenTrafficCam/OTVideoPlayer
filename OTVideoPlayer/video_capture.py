# OTVideoPlayer: VideoCapture class for the video player
# Copyright (C) 2022 OpenTrafficCam Contributors
# <https://github.com/OpenTrafficCam
# <team@opentrafficcam.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


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

    def get_frame(self, frame_number=None, height=None, width=None):
        if not height:
            height = self.height
        if not width:
            width = self.width
        if not self.capture.isOpened():
            return (ret, None)
        if frame_number:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
        ret, frame = self.capture.read()
        self.get_current_time()
        if height != self.height or width != self.width:
            frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
        return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) if ret else (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.capture.isOpened():
            self.capture.release()
