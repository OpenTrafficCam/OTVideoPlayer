import datetime
import tkinter as tk
from pathlib import Path
from tkinter import font

import cv2
import PIL.Image
import PIL.ImageTk

from helpers import EPOCH
from video_capture import VideoCapture


class FrameVideoPlayer(tk.LabelFrame):
    def __init__(self, video_path=None, canvas_height=500, **kwargs):
        super().__init__(**kwargs)

        self.paused = True
        self.update_video(video_path=video_path)

        self.canvas_height = canvas_height

        self.symbol_font_size = 15
        self.symbol_font = font.Font(
            family="Helvetica", size=self.symbol_font_size, weight=font.BOLD
        )
        self.SYMBOL_PLAY_PAUSE = "\u23EF"
        self.SYMBOL_SNAPSHOT = "\U0001F4F7"

        self.after_id = None

    def update_layout(self):

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(
            self,
            width=int(self.canvas_height * self.vid.width / self.vid.height),
            height=self.canvas_height,
        )
        self.canvas.pack()
        # self.canvas.config(width=200, height=200)

        # Play/pause button
        self.btn_play_pause = tk.Button(
            self,
            text=self.SYMBOL_PLAY_PAUSE,
            command=self.play_pause,
            font=self.symbol_font,
        )
        self.btn_play_pause.pack(anchor=tk.CENTER, expand=True, side="left")

        # Move frames buttons
        delta_frames_list = [-1, +1]
        self.btn_set_delta_frames = {}
        for delta_frames in delta_frames_list:
            delta_frames_str = (
                f"+{str(delta_frames)}" if delta_frames > 0 else str(delta_frames)
            )
            self.btn_set_delta_frames[delta_frames] = tk.Button(
                self,
                text=delta_frames_str,
                # command=lambda: self.set_delta_frames(delta_frames=delta_frames),
            )
            self.btn_set_delta_frames[delta_frames].bind(
                "<ButtonRelease-1>",
                lambda event, btn=self.btn_set_delta_frames[
                    delta_frames
                ]: self.set_delta_frames(event, btn, delta_frames),
            )  # BUG: #2 Only last delta_frames from delta_frames_list sent to fun
            self.btn_set_delta_frames[delta_frames].pack(
                anchor=tk.CENTER, expand=True, side="left"
            )

        # Slider
        self.slider_frame_var = tk.IntVar()
        self.slider_frame = tk.Scale(
            self,
            orient="horizontal",
            length=400,
            from_=1,
            to=self.vid.total_frames,
        )
        self.slider_frame.bind("<ButtonRelease-1>", self.slide)
        self.slider_frame.pack(anchor=tk.CENTER, expand=True, side="left")

        # Current time
        self.label_current_time_var = tk.StringVar()
        self.label_current_time = tk.Label(
            self, text="", textvariable=self.label_current_time_var
        )
        self.label_current_time.pack(anchor=tk.CENTER, expand=True, side="left")

        # Button that lets the user take a snapshot
        self.btn_snapshot = tk.Button(
            self,
            text=self.SYMBOL_SNAPSHOT,
            command=self.snapshot,
            font=self.symbol_font,
        )
        self.btn_snapshot.pack(anchor=tk.CENTER, expand=True, side="left")

    def update_video(self, video_path):
        # open video source (by default this will try to open the computer webcam)
        self.video_path = video_path
        if self.video_path:
            self.vid = VideoCapture(self.video_path)
            self.update_layout()
            self.play()

    def play_pause(self):
        if self.paused:
            self.paused = False
            self.play()
        else:
            self.paused = True

    def snapshot(self):
        # Get a frame from the video source
        if self.frame.any():
            video_path = Path(self.video_path)
            video_time_str = self.vid.current_time.strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
            snapshot_path_str = str(
                video_path.with_stem(f"{video_path.stem}_{video_time_str}").with_suffix(
                    ".jpg"
                )
            )
            cv2.imwrite(
                filename=snapshot_path_str,
                img=cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR),
            )

    def play(self, next_show=None, previous_time=None):
        self.display_new_frame()

        if not self.paused:
            current_time = datetime.datetime.now()
            if previous_time:
                delay_already = (current_time - previous_time).total_seconds() * 1000
                delay_wanted = 1000 / self.vid.fps
                delay_open = max(int(delay_wanted - delay_already), 1)
            else:
                delay_open = 1
            self.after_id = self.after(
                delay_open, lambda: self.play(previous_time=current_time)
            )
        elif self.after_id:
            self.after_cancel(self.after_id)

    def slide(self, event):
        frame_number = int(float(self.slider_frame.get()))
        self.display_new_frame(frame_number)

    def set_delta_frames(self, event, btn, delta_frames: int):
        if self.paused:
            if delta_frames == 0:
                pass
            elif delta_frames == 1:
                self.display_new_frame()
            else:
                new_frame = self.vid.current_frame + delta_frames
                self.display_new_frame(new_frame)

    def display_new_frame(self, frame_number=None):
        # Get a frame from the video source
        ret, self.frame = self.vid.get_frame(frame_number=frame_number)

        if ret:
            scale = self.canvas_height / self.vid.height
            self.photo = PIL.ImageTk.PhotoImage(
                image=PIL.Image.fromarray(self.frame).resize(
                    (int(scale * self.vid.width), int(scale * self.vid.height))
                )
            )
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.slider_frame.set(self.vid.current_frame)
            self.label_current_time_var.set(
                datetime.datetime.strftime(
                    self.vid.current_time, "%d.%m.%Y %H:%M:%S.%f"
                )[:-3]
            )

    def get_timestamp(self):
        return (
            (self.vid.current_time - EPOCH).total_seconds(),
            (self.vid.current_time - self.vid.start_time).total_seconds(),
            int(self.vid.current_frame),
        )
