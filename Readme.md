# OBS Widescreen Autofollow

This python script uses OBS websocket API to automatically adjust the position of the Display Capture source to follow the active window. When the active window is wider than the window, the script will 'split' the window into three zones and will snap to the nearest zone.


## Windows

### Installation

```
pip install -r requirements.txt
```

1. `OBS > Tools > Websocket Server Settings > Enable Websocket Server`
1. Open obs-autofollow.py > `#Configuration`
  1. Set targetHeight, targetWidth == OBS canvas size
  1. Port == port
  1. Password == password

### Usage

```bat
python obs_autofollow.py
```