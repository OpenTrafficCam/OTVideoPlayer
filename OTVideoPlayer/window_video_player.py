import tkinter as tk
from tkinter import filedialog

from frame_quick_time_stamps import FrameQuickTimeStamps
from frame_video_player import FrameVideoPlayer


class WindowVideoPlayer(tk.Tk):
    def __init__(self, title="OTVideoPlayer", video_path=None, **kwargs):
        super().__init__(**kwargs)
        self.title(title)
        self.update_layout()
        if video_path:
            self.frame_video_player.update_video(video_path=video_path)
        self.width, self.height = self.winfo_screenmmwidth(), self.winfo_screenheight()
        self.state("zoomed")
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
            command=lambda: self.frame_quick_timestamps.add_button(),
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
