# OTVideoPlayer: Tk LabelFrame and Menu for QuickTimeStamps in Standalone
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


import datetime as dt
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

import pandas as pd
from helpers import EPOCH

REALTIME = "realtime"
VIDEOTIME = "videotime"
FRAME = "frame"
EVENT = "event"
VIDEOPATH = "videopath"
CREATED = "created"
CREATOR = "creator"

HEADERS = [REALTIME, VIDEOTIME, FRAME, EVENT, VIDEOPATH, CREATED, CREATOR]

class FrameQuickTimeStamps(tk.LabelFrame):
    def __init__(self, buttons_per_row=3, **kwargs):
        super().__init__(**kwargs)
        self.path = None
        self.btns = {}
        self.buttons_per_row = buttons_per_row
        self.timestamps = []
        self.tree_visibility_dict = {
            "video": True,
            "creator": False,
            "realtime": True,
            "videotime": False,
            "frame": False,
        }
        self.layout()
        self.bind_keyboard_and_mouse_events()

    def layout(self):
        # Heading
        self.label_heading = tk.Label(
            master=self, text="QuickTimeStamps", font=("Arial", 14)
        )
        self.label_heading.pack()

        # Frames
        self.frame_tree = tk.Frame(master=self)
        self.frame_tree.pack(fill="both", expand=True)
        self.frame_controls = tk.Frame(master=self)
        self.frame_controls.pack()
        self.frame_buttons = tk.Frame(master=self)
        self.frame_buttons.pack()

        # Label timestamps file above treeview
        self.stringvar_timestamps_path = tk.StringVar()
        self.stringvar_timestamps_path.set("Please open or save csv with timestamps!")
        self.label_timestamps_path = tk.Label(
            master=self.frame_tree, textvariable=self.stringvar_timestamps_path
        )
        self.label_timestamps_path.pack()

        # Treeview
        self.tree = ttk.Treeview(master=self.frame_tree)
        self.tree.bind(
            "<ButtonRelease-3>",
            [self.tree.selection_remove(item) for item in self.tree.selection()],
        )

        # tree_columns = ("event", "video", "creator")
        self.tree.columns = {
            "#0": "Created",
            "created": "Created_seconds",
            "event": "Event",
            "realtime": "Realtime",
            "videotime": "Videotime",
            "frame": "Frame",
            "video": "Video",
            "creator": "Creator",
        }
        self.tree["columns"] = tuple(
            {k: v for k, v in self.tree.columns.items() if k != "#0"}.keys()
        )
        self.set_visible_tree_columns()

        for tree_col_id, tree_col_text in self.tree.columns.items():
            width = 155 if tree_col_id == "#0" else 140
            self.tree.column(tree_col_id, width=width, anchor="center")
            self.tree.heading(tree_col_id, text=tree_col_text, anchor="center")
        self.tree.pack(side="left", fill="both", expand=True)

        # Scrollbar for treeview
        self.tree_scrollbar = ttk.Scrollbar(
            master=self.frame_tree, orient="vertical", command=self.tree.yview
        )
        self.tree_scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.tree_scrollbar.set)

        # Delete selected buttons
        self.button_delete_selected = tk.Button(
            master=self.frame_controls,
            text="Delete selected",
            command=self.delete_selected_timestamps,
        )
        self.button_delete_selected.pack(
            padx=5,
            pady=5,
        )

    def bind_keyboard_and_mouse_events(self):
        self.master.bind("<Control-s>", self.save)
        # TODO: Unbind MouseWheel-VideoControls-connectin when mouse is in frame_tree
        # self.frame_tree.unbind("<MouseWheel>")  # , self.set_delta_frames

    def test(self, event):
        print(event.char)
        print(event.keysym)

    def set_visible_tree_columns(self):
        invisibility_list = [
            col for col, visible in self.tree_visibility_dict.items() if not visible
        ]
        self.tree["displaycolumns"] = tuple(
            {
                k: v
                for k, v in self.tree.columns.items()
                if k not in ["#0", "created"] + invisibility_list
            }.keys()
        )

    def add_button(self, label=None):
        if not label:
            label = simpledialog.askstring(
                "Button label", "Enter description for time stamp:"
            )
        if not label:
            messagebox.showinfo("Button has to have a label", "Please choose a label")
        elif label in list(self.btns.keys()):
            messagebox.showinfo("Button already exists", "Please choose another label")
        else:
            if not self.path:
                self.path = filedialog.asksaveasfilename(defaultextension=".csv")
            self.btns[label] = tk.Button(
                self.frame_buttons,
                text=label,
                command=lambda: self.add_timestamp(label),
            )
            row = (len(self.btns) - 1) // self.buttons_per_row
            column = (len(self.btns) - 1) % self.buttons_per_row
            # bad option "-anchor": must be -column, -columnspan, -in, -ipadx, -ipady, -padx, -pady, -row, -rowspan, or -sticky
            self.btns[label].grid(
                row=row,
                column=column,
                sticky="nesw",
                padx=5,
                pady=5,
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

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        for timestamp in self.timestamps:
            self.tree.insert(
                parent="",
                index="end",
                text=dt.datetime.utcfromtimestamp(timestamp["created"]).strftime(
                    "%d.%m.%Y %H:%M:%S.%f"
                )[:-3],
                values=(
                    timestamp["created"],
                    timestamp["event"],
                    dt.datetime.utcfromtimestamp(timestamp["realtime"]).strftime(
                        "%d.%m.%Y %H:%M:%S.%f"
                    )[:-3],
                    dt.datetime.utcfromtimestamp(timestamp["videotime"]).strftime(
                        "%d.%m.%Y %H:%M:%S.%f"
                    )[:-3],
                    timestamp["frame"],
                    Path(timestamp["videopath"]).name,
                    timestamp["creator"],
                ),
            )
        self.tree.yview_moveto(1)

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
                REALTIME: timestamp_real,
                VIDEOTIME: timestamp_video,
                FRAME: frame,
                EVENT: label,
                VIDEOPATH: videopath,
                CREATED: (dt.datetime.now() - EPOCH).total_seconds(),
                CREATOR: os.getlogin(),
            }
        )

        self.update_tree()

    def delete_selected_timestamps(self):
        # Get list of creation times of selected timestamps
        timestamps_selected_created = [
            float(self.tree.item(item)["values"][0]) for item in self.tree.selection()
        ]
        # Remove timestamps with matching creatiom times
        self.timestamps = [
            timestamp
            for timestamp in self.timestamps
            if timestamp["created"] not in timestamps_selected_created
        ]

        self.update_tree()

    def open(self):
        print("Open timestamps csv")
        path = filedialog.askopenfilename(
            title="Please choose a csv file of timestamps (metainfo in 1st line)",
            filetypes=[("CSV", "*.csv")],
        )
        if path:
            # Set new path
            self.path = path
            self.stringvar_timestamps_path.set(path)
            # Read buttons from csv file (first line is comment with button names)
            with open(path, "r") as f:
                comment = f.readline()
            comment = comment.replace("# Buttons: ", "")
            comment = comment.replace("\n", "")
            btn_list = comment.split(",")
            [self.add_button(label=label.rstrip()) for label in btn_list]
            # Read timestamps
            timestamps_df = pd.read_csv(path, sep=",", comment="#")
            self.timestamps = timestamps_df.to_dict("records")

            self.update_tree()

    def save_as(self):
        print("Save as... timestamps csv")
        # Get path
        path = filedialog.asksaveasfilename(filetypes=[("CSV file", "*.csv")])
        # Save
        if path:
            self.save(path=path)

    def save(self, event=None, path=None):
        print("Save timestamps csv")
        if not path:
            path = self.path
        try:
            # Write to csv file (first line is comment with button names)
            with open(path, "w") as f:
                btns_str = ",".join(self.btns.keys())
                f.write(f"# Buttons: {btns_str}\n")
            if self.timestamps:
                # Convert timestamps to table and write to csv file using pandas
                pd.DataFrame(self.timestamps).to_csv(path, index=False, mode="a")
            else:
                pd.DataFrame(columns=HEADERS).to_csv(path, index=False, mode="a")
            # Update file path
            self.path = path
            self.stringvar_timestamps_path.set(path)
        except Exception as e:
            print(e)
            self.save_as()


class MenuQuickTimeStamps(tk.Menu):
    def __init__(self, master, **kwargs):
        super().__init__(master=master, **kwargs)
        self.layout()

    def layout(self):

        # Menu quick time stamps
        self.master.add_cascade(menu=self, label="Quick time stamps")

        # Open
        self.add_command(
            label="Open ...",
            command=self.master.master.frame_quick_timestamps.open,
        )

        # Save
        self.add_separator()
        self.add_command(
            label="Save",
            command=lambda: self.master.master.frame_quick_timestamps.save(),
        )
        self.add_command(
            label="Save as ...",
            command=lambda: self.master.master.frame_quick_timestamps.save_as(),
        )

        # Buttons
        self.add_separator()
        self.add_command(
            label="Add button",
            command=self.master.master.frame_quick_timestamps.add_button,
        )
        self.add_command(
            label="Delete last button",
            command=self.master.master.frame_quick_timestamps.delete_button,
        )
        self.add_command(
            label="Delete all buttons",
            command=self.master.master.frame_quick_timestamps.delete_all_buttons,
        )
