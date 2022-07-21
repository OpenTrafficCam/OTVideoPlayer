# OTVideoPlayer: Tk window for usage as standalone application
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


import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from frame_quick_time_stamps import FrameQuickTimeStamps, MenuQuickTimeStamps
from frame_video_player import FrameVideoPlayer
from helpers import ON_WINDOWS


class WindowVideoPlayer(tk.Tk):
    def __init__(
        self,
        title="OTVideoPlayer",
        video_path=None,
        quick_time_stamps_enabled=True,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.title(title)
        if ON_WINDOWS:
            self.iconbitmap(Path(__file__).parents[0] / r"OTC.ico")
        self.quick_time_stamps_enabled = quick_time_stamps_enabled
        self.video_path = video_path
        self.frame_video_player = None
        self.width, self.height = self.winfo_screenmmwidth(), self.winfo_screenheight()
        self.state("zoomed")
        self.layout()
        self.mainloop()

    def layout(self):

        # Frame video player
        self.open_video(video_path=self.video_path)

        # Frame quick timestamps
        if self.quick_time_stamps_enabled:
            self.frame_quick_timestamps = FrameQuickTimeStamps(master=self)
            self.frame_quick_timestamps.grid(column=1, row=0, sticky="NSEW")

        # Menu
        self.option_add("*tearOff", False)
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)
        self.menu_file = MenuFile(self.menubar)
        if self.quick_time_stamps_enabled:
            self.menu_quick_time_stamps = MenuQuickTimeStamps(master=self.menubar)

        # Make window responsive
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    def open_video(self, video_path=None):
        if self.frame_video_player:
            self.frame_video_player.destroy()
        if not video_path:
            video_path = filedialog.askopenfilename(
                title="Please choose a video file to play",
                filetypes=[
                    ("mp4", "*.mp4"),
                    ("avi", "*.avi"),
                    ("mkv", "*.mkv"),
                    ("mov", "*.mov"),
                    ("wmv", "*.wmv"),
                    ("h264", "*.h264"),
                ],
            )
        self.frame_video_player = FrameVideoPlayer(master=self, video_path=video_path)
        self.frame_video_player.grid(column=0, row=0, sticky="NSEW")


class MenuFile(tk.Menu):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)
        self.layout()

    def layout(self):
        self.master.add_cascade(menu=self, label="File")
        self.add_command(label="Open video...", command=self.master.master.open_video)
        self.add_separator()
        self.add_command(label="Quit", command=self.master.master.destroy)
