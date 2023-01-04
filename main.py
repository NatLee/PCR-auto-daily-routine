# -*- coding: utf-8 -*-

from pathlib import Path
import time

import cv2
import numpy as np

import mss
import mouse

def get_screenshot(default_monitor_number=0):
    with mss.mss() as sct:
        monitor = sct.monitors[default_monitor_number] # 預設擷取全螢幕
        screenshot = np.array(sct.grab(monitor))
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    return screenshot


def mouse_move(x, y, click=True):
    original_x, original_y = mouse.get_position()
    mouse.move(x, y, absolute=True)
    if click:
        mouse.click(button='left')
    mouse.move(original_x, original_y, absolute=True)
    return

def get_pts(image, pattern, threshold=0.7) -> list:
    # 獲得對應物件的位置
    pattern = cv2.cvtColor(pattern, cv2.COLOR_BGR2GRAY)
    w, h = pattern.shape[::-1]
    res = cv2.matchTemplate(
        image,
        pattern,
        cv2.TM_CCOEFF_NORMED
    )
    loc = np.where( res >= threshold)
    pts = []
    for pt in zip(*loc[::-1]):
        x1, y1 = pt # 左上點
        x2, y2 = w+x1, h+y1 # 右下點
        pts.append((x1, y1, x2, y2))
    return pts

def get_center_pt(*pt):
    pt, *_ = pt
    x1, y1, x2, y2 = pt
    return ((x1+x2)//2, (y1+y2)//2)


class Button:
    def __init__(self, pattern_path):
        self.pattern_path = pattern_path
        self.pattern = self.load_pattern()

    def load_pattern(self):
        return cv2.imread(self.pattern_path)

    def detect(self):
        screenshot = get_screenshot()
        pts = get_pts(screenshot, self.pattern)
        if pts:
            print(f'---- Find [{self.pattern_path}]')
        return pts, screenshot

    def wait_until(self, timeout):
        print(f"---- Wait [{self.pattern_path}]")
        start_time = time.time()
        pts = []
        screenshot = None
        count = 1
        while not pts and (time.time() - start_time) <= timeout:
            print(f"Waiting count: {count}")
            count += 1
            pts, screenshot = self.detect()
        if not pts:
            print(f'---- Timeout [{self.pattern_path}]')
        return pts, screenshot


def back_to_home() -> bool:
    print("---- 執行回到主頁")
    home_before = Button('./img/home-before.png')
    home_after = Button('./img/home-after.png')

    pts, screenshot = home_before.wait_until(3)
    if pts:
        pt = pts[0]
        x, y = get_center_pt(pt)
        mouse_move(x, y)
        return True
    pts, screenshot = home_after.wait_until(1)
    if pts:
        print('---- 已經在Home頁面')
    else:
        print(f'---- 此畫面找不到Home按鈕')
    return False

def debug():
    img_paths = [img for img in Path('./img').glob('*.png')]
    for img_path in img_paths:
        button = Button(img_path.as_posix())
        pts, screenshot = button.wait_until(timeout=3)
        if not pts:
            continue

        pt = pts[0]
        x1, y1, x2, y2 = pt

        cv2.rectangle(
            screenshot,
            (x1, y1),
            (x2, y2),
            (0, 0, 255),
            2
        )

        center = get_center_pt(pt)
        print(center)
        x, y = center
        mouse_move(x, y)

        screenshot_ = cv2.resize(screenshot, fx=0.3, fy=0.3, dsize=None)
        cv2.imshow(f"{img_path}", screenshot_)
        cv2.waitKey()

if __name__ == '__main__':
    #debug()
    back_to_home()

