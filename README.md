# OTVideoPlayer

Tkinter and OpenCV based videoplayer that can be used as standalone application and as an embedded LabelFrame of a custom window in other OpenTrafficCam applications

## Standalone application

### Installation

1. Install Python
2. Download and unzip this repository (or alternatively clone this repository using git via shell or an IDE like VS Code)
3. Install OTVideoplayer by click on `install.bat`

### Usage

#### Windows

Run OTVideoPlayer by click on `OTVideoPlayer.bat`

#### Other systems

Instructions will be added later

## Python package

### API usage example

```python
import tkinter as tk
from OTVideoPlayer import FrameVideoPlayer

window = tk.Tk("My custom video player")

frame_video_player = FrameVideoPlayer(video_path=r"path/to/my/video")
frame_video_player.pack()

# Here you can put the other widgets

# Get video time, absolute time and number of current frame 
time_video, time_since_epoch, frame_number = frame_video_player.get_timestamp()

window.mainloop()
```
