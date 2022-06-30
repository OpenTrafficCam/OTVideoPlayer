import csv
import datetime
import time
import tkinter as tk
from doctest import master
from pathlib import Path
from tkinter import filedialog, font, messagebox, simpledialog

import cv2
import pandas as pd
import PIL.Image
import PIL.ImageTk

from helpers import EPOCH, _get_datetime_from_filename


class WindowVideoPlayer(tk.Tk):
    def __init__(self, title="OTVideoPlayer", video_path=None, **kwargs):
        super().__init__(**kwargs)
        self.title(title)
        self.update_layout()
        if video_path:
            self.frame_video_player.update_video(video_path=video_path)
        self.mainloop()

    def update_layout(self):

        # Frame video player
        self.frame_video_player = FrameVideoPlayer(master=self)
        self.frame_video_player.pack()

        # Frame quick timestamp
        self.frame_quick_timestamps = FrameQuickTimeStamps(master=self)
        self.frame_quick_timestamps.pack()

        # Menu
        self.option_add("*tearOff", False)
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        self.menu_file = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_file, label="File")
        self.menu_file.add_command(label="Open file...", command=self.open_file)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Quit", command=self.destroy)
        self.menu_quick_timestamps = tk.Menu(self.menubar)
        self.menubar.add_cascade(
            menu=self.menu_quick_timestamps, label="Quick time stamps"
        )
        self.menu_quick_timestamps.add_command(
            label="Add button",
            command=lambda: self.frame_quick_timestamps.add_button(
                label=simpledialog.askstring(
                    "Button label", "Enter description for time stamp:"
                )
            ),
        )
        self.menu_quick_timestamps.add_command(
            label="Delete last button",
            command=self.frame_quick_timestamps.delete_button,
        )
        self.menu_quick_timestamps.add_command(
            label="Delete all buttons",
            command=self.frame_quick_timestamps.delete_all_buttons,
        )
        self.menu_quick_timestamps.add_separator()
        self.menu_quick_timestamps.add_command(
            label="Load last buttons",
            command=lambda: self.frame_quick_timestamps.load_buttons(last=True),
        )
        self.menu_quick_timestamps.add_command(
            label="Load buttons",
            command=lambda: self.frame_quick_timestamps.load_buttons(),
        )
        self.menu_quick_timestamps.add_command(
            label="Save buttons",
            command=lambda: self.frame_quick_timestamps.save_buttons(),
        )
        self.menu_quick_timestamps.add_separator()
        self.menu_quick_timestamps.add_command(
            label="Load last time stamps",
            command=lambda: self.frame_quick_timestamps.load(last=True),
        )
        self.menu_quick_timestamps.add_command(
            label="Load time stamps",
            command=lambda: self.frame_quick_timestamps.load(),
        )
        self.menu_quick_timestamps.add_command(
            label="Save time stamps",
            command=lambda: self.frame_quick_timestamps.save(),
        )

    def open_file(self):
        video_path = filedialog.askopenfilename()
        self.frame_video_player.update_video(video_path=video_path)


class FrameVideoPlayer(tk.LabelFrame):
    def __init__(self, video_path=None, **kwargs):
        super().__init__(**kwargs)

        self.paused = True
        self.update_video(video_path=video_path)

        self.symbol_font_size = 15
        self.symbol_font = font.Font(
            family="Helvetica", size=self.symbol_font_size, weight=font.BOLD
        )
        self.SYMBOL_PLAY_PAUSE = "\u23EF"
        self.SYMBOL_SNAPSHOT = "\U0001F4F7"

        self.after_id = None

    def update_layout(self):

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(self, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()

        # Play/pause button
        self.btn_play_pause = tk.Button(
            self,
            text=self.SYMBOL_PLAY_PAUSE,
            command=self.play_pause,
            font=self.symbol_font,
        )
        self.btn_play_pause.pack(anchor=tk.CENTER, expand=True, side="left")

        # Slider
        self.slider_frame_var = tk.IntVar()
        self.slider_frame = tk.Scale(
            self,
            orient="horizontal",
            length=400,
            from_=1,
            to=self.vid.total_frames,
            command=lambda event: self.display_new_frame(int(float(event))),
        )
        self.slider_frame.pack(anchor=tk.CENTER, expand=True, side="left")
        # TODO: #1 Move slider when playback

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
        if self.frame:
            cv2.imwrite(
                "frame-" + time.strftime("%Y-%m-%d_%H-%M-%S") + ".jpg",
                cv2.cvtColor(self.frame, cv2.COLOR_RGB2BGR),
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

    def display_new_frame(self, frame_number=None):
        # Get a frame from the video source
        ret, self.frame = self.vid.get_frame(frame_number=frame_number)

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(self.frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.slider_frame_var.set(self.vid.current_frame)
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
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.capture.read()
        self.get_current_time()
        return (ret, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)) if ret else (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.capture.isOpened():
            self.capture.release()


class FrameQuickTimeStamps(tk.LabelFrame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.btns = {}
        self.timestamps = []

    def add_button(self, label):
        if label not in list(self.btns.keys()):
            self.btns[label] = tk.Button(
                self,
                text=label,
                command=lambda: self.add_timestamp(label),
            )
            self.btns[label].pack(
                anchor=tk.CENTER, expand=True, side="left", padx=5, pady=5
            )
        else:
            messagebox.showinfo("Button already exists", "Please choose another name")

    def delete_button(self, label=None):
        if len(self.btns) > 0:
            if not label:
                label = list(self.btns.keys())[-1]
            self.btns[label].destroy()
            self.btns.pop(label, None)

    def delete_all_buttons(self):
        labels = list(self.btns.keys())
        for label in labels:
            self.btns[label].destroy()
            self.btns.pop(label, None)

    def save_buttons(self):

        path = filedialog.asksaveasfilename(filetypes=[("Text files", "*.txt")])
        btn_paths = [
            path,
            Path("last.OTQuickButtons"),
        ]

        for btn_path in btn_paths:
            with open(btn_path, "w") as f:
                for btn in self.btns.keys():
                    f.write("%s\n" % btn)

    def load_buttons(self, last=False):
        if last:
            btn_file = Path("last.OTQuickButtons")
        else:
            btn_file = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        labels = []
        with open(btn_file) as f:
            labels = f.readlines()
        [self.add_button(label=label.rstrip()) for label in labels]

    def add_timestamp(self, label):
        import os

        videopath = self.master.frame_video_player.video_path
        (
            timestamp_real,
            timestamp_video,
            frame,
        ) = self.master.frame_video_player.get_timestamp()
        self.timestamps.append(
            {
                "realtime": timestamp_real,
                "videotime": timestamp_video,
                "frame": frame,
                "event": label,
                "videopath": videopath,
                "created": (datetime.datetime.now() - EPOCH).total_seconds(),
                "creator": os.getlogin(),
            }
        )
        print("Timestamps:")
        print(self.timestamps)

    def save(self):
        path = filedialog.asksaveasfilename(defaultextension=".csv")
        print(pd.DataFrame(self.timestamps))
        pd.DataFrame(self.timestamps).to_csv(path, index=False)
        pd.DataFrame(self.timestamps).to_csv(
            Path("last.OTQuickTimeStamps"), index=False
        )

    def load(self, last=False):
        path = (
            Path("last.OTQuickTimeStamps")
            if last
            else filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        )
        timestamps_loaded = pd.read_csv(path).to_dict(orient="records")
        self.timestamps = timestamps_loaded + self.timestamps
        # TODO: Handle duplicates


def main():
    # global app
    # Create a window and pass it to the Application object
    WindowVideoPlayer(
        video_path=r"C:\Users\Baerwolff\Testvideos\Validierungsmessung_Radeberg\raspberrypi_FR20_2020-02-20_12-00-00.mp4"
    )


if __name__ == "__main__":
    main()
