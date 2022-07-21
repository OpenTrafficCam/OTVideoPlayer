# OTVideoPlayer: Tk LabelFrame of the actual video player
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
import tkinter as tk
from pathlib import Path
from tkinter import font
from tkinter.messagebox import showinfo
from turtle import width

import cv2
import PIL.Image
import PIL.ImageTk

from helpers import EPOCH
from video_capture import VideoCapture


class FrameVideoPlayer(tk.LabelFrame):
    def __init__(self, video_path, canvas_height=500, **kwargs):
        super().__init__(**kwargs)

        self.video_path = video_path
        self.video_capture = VideoCapture(self.video_path)
        self.paused = True

        self.canvas_height = canvas_height
        self.canvas_width = int(
            self.canvas_height * self.video_capture.width / self.video_capture.height
        )

        self.symbol_font_size = 15
        self.symbol_font = font.Font(
            family="Helvetica", size=self.symbol_font_size, weight=font.BOLD
        )
        self.SYMBOL_PLAY_PAUSE = "\u23EF"
        self.SYMBOL_SNAPSHOT = "\U0001F4F7"

        self.after_id = None

        self.layout()
        self.bind_keyboard_and_mouse_events()
        self.play()

    def layout(self):

        # Heading
        self.label_heading = tk.Label(
            master=self, text="OTVideoPlayer", font=("Arial", 14)
        )
        self.label_heading.pack()

        # VIDEO CANVAS

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(
            self,
            width=self.canvas_width,
            height=self.canvas_height,
        )
        self.canvas.pack()
        # self.canvas.config(width=200, height=200)

        # VIDEO CONTROLS
        self.controls = tk.Frame(master=self)
        self.controls.pack()

        # Play/pause button
        self.btn_play_pause = tk.Button(
            self.controls,
            text=self.SYMBOL_PLAY_PAUSE,
            command=self.play_pause,
            font=self.symbol_font,
        )
        self.btn_play_pause.pack(anchor=tk.CENTER, expand=True, side="left")

        # Next/previous frames buttons
        self.button_previous_frame = tk.Button(master=self.controls, text="-1")
        self.button_previous_frame.bind(
            "<ButtonRelease-1>",
            lambda event: self.set_delta_frames(event, delta_frames=-1),
        )
        self.button_previous_frame.pack(anchor="center", expand=True, side="left")
        self.button_next_frame = tk.Button(master=self.controls, text="+1")
        self.button_next_frame.bind(
            "<ButtonRelease-1>",
            lambda event: self.set_delta_frames(event, delta_frames=+1),
        )
        self.button_next_frame.pack(anchor="center", expand=True, side="left")

        # Slider
        self.slider_frame_var = tk.IntVar()
        self.slider_frame = tk.Scale(
            self.controls,
            orient="horizontal",
            length=400,
            from_=1,
            to=self.video_capture.total_frames,
            command=self.slide,
        )
        self.slider_frame.pack(anchor=tk.CENTER, expand=True, side="left")

        # Current time
        self.label_current_time_var = tk.StringVar()
        self.label_current_time = tk.Label(
            self.controls, text="", textvariable=self.label_current_time_var
        )
        self.label_current_time.pack(anchor=tk.CENTER, expand=True, side="left")

        # Button that lets the user take a snapshot
        self.btn_snapshot = tk.Button(
            self.controls,
            text=self.SYMBOL_SNAPSHOT,
            command=self.snapshot,
            font=self.symbol_font,
        )
        self.btn_snapshot.pack(anchor=tk.CENTER, expand=True, side="left")

    def bind_keyboard_and_mouse_events(self):
        self.master.bind("<space>", self.play_pause)
        self.frames_per_mousewheelgrid = 1
        self.master.bind("<MouseWheel>", self.set_delta_frames)

    def test(self, event):
        print(event)

    def play_pause(self, event=None):
        if self.paused:
            self.paused = False
            self.play()
        else:
            self.paused = True

    def snapshot(self):
        # Get a frame from the video source
        if self.frame.any():
            video_path = Path(self.video_path)
            video_time_str = self.video_capture.current_time.strftime(
                "%Y-%m-%d_%H-%M-%S-%f"
            )[:-3]
            snapshot_path_str = str(
                video_path.with_stem(f"{video_path.stem}_{video_time_str}").with_suffix(
                    ".jpg"
                )
            )
            cv2.imwrite(
                filename=snapshot_path_str,
                img=cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR),
            )
            showinfo(self.master, f"Snapshot saved at: {snapshot_path_str}")

    def play(self, next_show=None, previous_time=None):
        self.display_new_frame()

        if not self.paused:
            current_time = datetime.datetime.now()
            if previous_time:
                delay_already = (current_time - previous_time).total_seconds() * 1000
                delay_wanted = 1000 / self.video_capture.fps
                delay_open = max(int(delay_wanted - delay_already), 1)
            else:
                delay_open = 1
            self.after_id = self.after(
                delay_open, lambda: self.play(previous_time=current_time)
            )
        elif self.after_id:
            self.after_cancel(self.after_id)

    def slide(self, event=None):
        if self.paused:
            frame_number = int(float(self.slider_frame.get()))
            self.display_new_frame(frame_number)

    def set_delta_frames(self, event=None, delta_frames: int = None):
        if self.paused:
            if not delta_frames and event:  # if called from MouseWheel
                delta_frames = event.delta / 120 * self.frames_per_mousewheelgrid
            if delta_frames == 0:
                pass
            elif delta_frames == 1:
                self.display_new_frame()
            elif delta_frames:
                new_frame = self.video_capture.current_frame + delta_frames
                self.display_new_frame(new_frame)

    def display_new_frame(self, frame_number=None):
        # Get a frame from the video source
        ret, self.frame = self.video_capture.get_frame(
            frame_number=frame_number,
            height=self.canvas_height,
            width=self.canvas_width,
        )

        if ret:
            scale = self.canvas_height / self.video_capture.height
            self.photo = PIL.ImageTk.PhotoImage(
                image=PIL.Image.fromarray(self.frame).resize(
                    (
                        int(scale * self.video_capture.width),
                        int(scale * self.video_capture.height),
                    )
                )
            )
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.slider_frame.set(self.video_capture.current_frame)
            self.label_current_time_var.set(
                datetime.datetime.strftime(
                    self.video_capture.current_time, "%d.%m.%Y %H:%M:%S.%f"
                )[:-3]
            )

    def get_timestamp(self):
        return (
            (self.video_capture.current_time - EPOCH).total_seconds(),
            (
                self.video_capture.current_time - self.video_capture.start_time
            ).total_seconds(),
            int(self.video_capture.current_frame),
        )
