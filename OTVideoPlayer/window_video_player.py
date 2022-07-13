import tkinter as tk
from tkinter import filedialog

from frame_quick_time_stamps import FrameQuickTimeStamps, layout_menu_quick_time_stamps
from frame_video_player import FrameVideoPlayer


class WindowVideoPlayer(tk.Tk):
    def __init__(
        self, title="OTVideoPlayer", video_path=None, quick_time_stamps=True, **kwargs
    ):
        super().__init__(**kwargs)
        self.title(title)
        self.quick_time_stamps = quick_time_stamps
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

        # Frame quick timestamps
        if self.quick_time_stamps:
            self.frame_quick_timestamps = FrameQuickTimeStamps(master=self)
            self.frame_quick_timestamps.pack()

        # Menu
        self.option_add("*tearOff", False)
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        self.layout_menu_file()

        if self.quick_time_stamps:
            layout_menu_quick_time_stamps(self)

    def layout_menu_file(self):
        # Menu file
        self.menu_file = tk.Menu(self.menubar)
        self.menubar.add_cascade(menu=self.menu_file, label="File")
        self.menu_file.add_command(label="Open file...", command=self.open_file)
        self.menu_file.add_separator()
        self.menu_file.add_command(label="Quit", command=self.destroy)

    def open_file(self):
        video_path = filedialog.askopenfilename()
        self.frame_video_player.update_video(video_path=video_path)
