import datetime
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog

import pandas as pd

from helpers import EPOCH


class FrameQuickTimeStamps(tk.LabelFrame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.path = filedialog.asksaveasfilename(defaultextension=".csv")
        self.btns = {}
        self.timestamps = []

    def add_button(self):
        label = simpledialog.askstring(
            "Button label", "Enter description for time stamp:"
        )
        if not label:
            messagebox.showinfo("Button has to have a label", "Please choose a label")
        elif label in list(self.btns.keys()):
            messagebox.showinfo("Button already exists", "Please choose another label")
        else:
            self.btns[label] = tk.Button(
                self,
                text=label,
                command=lambda: self.add_timestamp(label),
            )
            self.btns[label].pack(
                anchor=tk.CENTER, expand=True, side="left", padx=5, pady=5
            )

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
        print(pd.DataFrame(self.timestamps))
        pd.DataFrame(self.timestamps).to_csv(self.path, index=False)
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

def layout_menu_quick_time_stamps(parent):
    # Menu quick time stamps
    parent.menu_quick_timestamps = tk.Menu(parent.menubar)
    parent.menubar.add_cascade(
            menu=parent.menu_quick_timestamps, label="Quick time stamps"
        )
    parent.menu_quick_timestamps.add_command(
            label="Add button",
            command=lambda: parent.frame_quick_timestamps.add_button(),
        )
    parent.menu_quick_timestamps.add_command(
            label="Delete last button",
            command=parent.frame_quick_timestamps.delete_button,
        )
    parent.menu_quick_timestamps.add_command(
            label="Delete all buttons",
            command=parent.frame_quick_timestamps.delete_all_buttons,
        )
    parent.menu_quick_timestamps.add_separator()
    parent.menu_quick_timestamps.add_command(
            label="Load last buttons",
            command=lambda: parent.frame_quick_timestamps.load_buttons(last=True),
        )
    parent.menu_quick_timestamps.add_command(
            label="Load buttons",
            command=lambda: parent.frame_quick_timestamps.load_buttons(),
        )
    parent.menu_quick_timestamps.add_command(
            label="Save buttons",
            command=lambda: parent.frame_quick_timestamps.save_buttons(),
        )
    parent.menu_quick_timestamps.add_separator()
    parent.menu_quick_timestamps.add_command(
            label="Load last time stamps",
            command=lambda: parent.frame_quick_timestamps.load(last=True),
        )
    parent.menu_quick_timestamps.add_command(
            label="Load time stamps",
            command=lambda: parent.frame_quick_timestamps.load(),
        )
    parent.menu_quick_timestamps.add_command(
            label="Save time stamps",
            command=lambda: parent.frame_quick_timestamps.save(),
        )

