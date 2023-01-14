import cv2
import numpy as np

import mss

def get_screenshot(default_monitor_number=0):
    with mss.mss() as sct:
        monitor = sct.monitors[default_monitor_number] # 預設擷取全螢幕
        screenshot = np.array(sct.grab(monitor))
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    return screenshot
