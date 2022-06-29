# OTVideoPlayer
Tkinter and OpenCV based videoplayer that can be used as standalone application and as an embedded LabelFrame of a custom window in other OpenTrafficCam applications

## Installation
Clone this repository (or download and unzip)

## Usage as standalone
### Windows
- Create virtual environment: ```python -m venv venv```
- Activate virtual environment: ```venv\Scripts\activate```
- Install dependencies: ```pip install -r requirements.txt```
- Deactivate virtual environment: ```deactivate```

## API usage example
```python
import tkinter as tk
from OTVideoPlayer import FrameVideoPlayer

window = tk.Tk("My custom video player")

frame_video_player = FrameVideoPlayer(video_path=r"path/to/my/video")
frame_video_player.pack()

# Here you can put the other widgets

window.mainloop()
```
