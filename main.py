# -*- coding: utf-8 -*-

from pathlib import Path
import time

import cv2
import numpy as np

from utils.get_screenshot import get_screenshot
from utils.mouse_move import mouse_move


class PatternPosition:
    def __init__(self, screenshot, pattern, threshold=0.7):
        self.threshold = threshold
        self.screenshot = screenshot
        self.pattern = cv2.cvtColor(pattern, cv2.COLOR_BGR2GRAY)
        self.pts = self.get_pts()

    def is_valid(self):
        if self.pts:
            return True
        return False

    def get_pts(self) -> list:
        # 獲得對應物件的位置
        w, h = self.pattern.shape[::-1]
        res = cv2.matchTemplate(
            self.screenshot,
            self.pattern,
            cv2.TM_CCOEFF_NORMED
        )
        loc = np.where( res >= self.threshold)
        pts = []
        for pt in zip(*loc[::-1]):
            x1, y1 = pt # 左上點
            x2, y2 = w+x1, h+y1 # 右下點
            pts.append((x1, y1, x2, y2))
        return pts
    
    def get_screenshot(self):
        return self.screenshot

    def get_debug_screenshot(self):
        x1, y1, x2, y2 = self.get_pt()
        screenshot = self.get_screenshot()
        cv2.rectangle(
            screenshot,
            (x1, y1),
            (x2, y2),
            (0, 0, 255),
            2
        )
        screenshot = cv2.resize(screenshot, fx=0.3, fy=0.3, dsize=None)
        return screenshot

    def get_pt(self):
        x1, y1, x2, y2 = self.pts[0]
        return x1, y1, x2, y2

    def get_center_pt(self):
        x1, y1, x2, y2 = self.pts[0]
        return ((x1+x2)//2, (y1+y2)//2)


class Button:
    def __init__(self, pattern_path):
        self.pattern_path = pattern_path
        self.pattern = self.load_pattern()

    def load_pattern(self):
        return cv2.imread(self.pattern_path)

    def detect(self):
        screenshot = get_screenshot()
        pts = PatternPosition(screenshot, self.pattern)
        if pts.is_valid():
            print(f'---- Find [{self.pattern_path}]')
        return pts

    def wait_until(self, timeout):
        print(f"---- Wait [{self.pattern_path}]")
        start_time = time.time()
        pts = self.detect()
        count = 1
        while not pts.is_valid() and (time.time() - start_time) <= timeout:
            print(f"Waiting count: {count}")
            count += 1
            pts = self.detect()
        if not pts:
            print(f'---- Timeout [{self.pattern_path}]')
        return pts


def back_to_home() -> bool:
    print("---- 執行回到主頁")
    home_before = Button('./img/home-before.png')
    home_after = Button('./img/home-after.png')
    pts = home_before.wait_until(3)
    if pts.is_valid():
        x, y = pts.get_center_pt()
        mouse_move(x, y)
        return True
    pts = home_after.wait_until(1)
    if pts:
        print('---- 已經在Home頁面')
    else:
        print(f'---- 此畫面找不到Home按鈕')
    return False

def debug():
    img_paths = [img for img in Path('./img').glob('*.png')]
    for img_path in img_paths:
        button = Button(img_path.as_posix())
        pts = button.wait_until(timeout=3)
        if not pts.is_valid():
            continue
        x, y = pts.get_center_pt()
        print(x, y)
        mouse_move(x, y)

        cv2.imshow(f"{img_path}", pts.get_debug_screenshot())
        cv2.waitKey()

def click_skip_button() -> bool:
    print("---- 執行點擊跳過按鈕")
    skip_pattern = Button('./img/skip-play.png')
    pts = skip_pattern.wait_until(3)
    if pts.is_valid():
        x, y = pts.get_center_pt()
        mouse_move(x, y)
        return True
    return False

def skip_scene() -> bool:
    print("---- 執行跳過劇情")
    menu = Button('./img/menu.png')
    pts = menu.wait_until(3)
    if pts.is_valid():
        x, y = pts.get_center_pt()
        mouse_move(x, y)
        print("---- 已點擊清單")

    skip_scene = Button('./img/skip-scene.png')
    pts = skip_scene.wait_until(3)
    if pts.is_valid():
        x, y = pts.get_center_pt()
        mouse_move(x, y)
        print("---- 已點擊跳過")

    dialog_skip = Button('./img/dialog-skip.png')
    pts = dialog_skip.wait_until(3)
    if pts.is_valid():
        x, y = pts.get_center_pt()
        mouse_move(x, y)
        print("---- 已點擊對話跳過")

    return True

if __name__ == '__main__':
    #debug()
    #back_to_home()
    skip_scene()

