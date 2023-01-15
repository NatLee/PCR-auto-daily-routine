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

    def show_debug_screenshot(self):
        cv2.imshow("debug-screenshot", self.get_debug_screenshot())
        cv2.waitKey()
        return

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

class Switcher:
    def __init__(self, before:str, after:str, name=''):
        self.name = name
        self.before = Button(before)
        self.after = Button(after)
    def switch(self):
        before_pts = self.before.wait_until(3)
        if not before_pts.is_valid():
            print(f'---- 此畫面找不到 Before {self.name} 按鈕')
            print(f'---- 嘗試搜尋 After {self.name} 按鈕')
            after_pts = self.after.wait_until(2)
            if not after_pts.is_valid():
                print(f'---- 找不到任何 Before & After {self.name} 按鈕')
                return False
            else:
                print(f'---- 已經在 {self.name} 頁面')
                return True
        else:
            print(f'---- 此畫面找到 Before {self.name} 按鈕')
            x, y = before_pts.get_center_pt()
            mouse_move(x, y)
            after_pts = self.after.wait_until(2)
            if not after_pts.is_valid():
                print(f'---- 此畫面找不到 After {self.name} 按鈕')
                return False
            else:
                print(f'---- 已經在 {self.name} 頁面')
                return True


def home() -> bool:
    print("---- 執行前往主頁")
    switch = Switcher(
        name='主頁按鈕',
        before='./img/home-before.png',
        after='./img/home-after.png',
    )
    return switch.switch()

def gachapon() -> bool:
    print("---- 執行前往轉蛋頁面")
    switch = Switcher(
        name='轉蛋',
        before='./img/gachapon-before.png',
        after='./img/gachapon-after.png',
    )
    return switch.switch()

def gachapon_common() -> bool:
    print("---- 執行點選轉蛋頁面的普通轉蛋按鈕")
    switch = Switcher(
        name='普通轉蛋按鈕',
        before='./img/gachapon-common-before.png',
        after='./img/gachapon-common-after.png',
    )
    return switch.switch()

def adventure() -> bool:
    print("---- 執行前往冒險")
    switch = Switcher(
        name='冒險按鈕',
        before='./img/adventure-before.png',
        after='./img/adventure-after.png',
    )
    return switch.switch()

def ok(timeout=3):
    ok_buttion = Button('./img/OK.png')
    pts = ok_buttion.wait_until(timeout)
    if not pts.is_valid():
        print("---- 找不到OK按鈕")
        return False
    x, y = pts.get_center_pt()
    mouse_move(x, y)
    print("---- 已點擊OK按鈕")
    return True

def action_click_skip_button() -> bool:
    print("---- 執行點擊跳過按鈕")
    skip_pattern = Button('./img/skip-play.png')
    pts = skip_pattern.wait_until(3)
    if pts.is_valid():
        x, y = pts.get_center_pt()
        mouse_move(x, y)
        return True
    return False

def action_skip_scene() -> bool:
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

def action_free_gachapon(after_wait_sec=3) -> bool:
    print("---- 執行免費轉蛋")
    if not gachapon():
        return False
    if not gachapon_common():
        return False

    gacha_10_free_buttion = Button('./img/gachapon-10-free.png')
    pts = gacha_10_free_buttion.wait_until(5)
    if not pts.is_valid():
        print("---- 找不到或是已使用過免費轉蛋")
        return False
    x, y = pts.get_center_pt()
    mouse_move(x, y, click_before_sec=2)
    print("---- 已點擊免費轉蛋按鈕")

    if not ok(timeout=5):
        return False

    time.sleep(after_wait_sec)

    return True

def action_explorer(after_wait_sec=3) -> bool:
    print('---- 執行探索')
    print('---- 先回到主頁')
    if not home():
        return False

    if not adventure():
        return False
    adventure_explorer_button = Button('./img/adventure-explorer.png')
    pts = adventure_explorer_button.wait_until(3)
    if not pts.is_valid():
        print("---- 找不到探索按鈕")
        return False
    x, y = pts.get_center_pt()
    mouse_move(x, y)
    print("---- 已點擊探索按鈕")

    adventure_explorer_exp_button = Button('./img/adventure-explorer-exp.png')
    pts = adventure_explorer_exp_button.wait_until(3)
    if not pts.is_valid():
        print("---- 找不到經驗值冒險按鈕")
        return False
    x, y = pts.get_center_pt()
    mouse_move(x, y)
    print("---- 已點擊經驗值冒險按鈕")

    adventure_explorer_exp_lv_button = Button('./img/adventure-explorer-exp-lv.png')
    pts = adventure_explorer_exp_lv_button.wait_until(3)
    if not pts.is_valid():
        print("---- 找不到經驗值冒險任務按鈕")
        return False
    x, y = pts.get_center_pt()
    mouse_move(x, y)
    print("---- 已點擊經驗值冒險任務按鈕")

    adventure_explorer_exp_lv_button = Button('./img/adventure-explorer-exp-lv.png')
    pts = adventure_explorer_exp_lv_button.wait_until(3)
    if not pts.is_valid():
        print("---- 找不到經驗值冒險任務按鈕")
        return False
    x, y = pts.get_center_pt()
    mouse_move(x, y)
    print("---- 已點擊經驗值冒險任務按鈕")

    adventure_explorer_lv_use_2_button = Button('./img/adventure-explorer-lv-use-2.png')
    pts = adventure_explorer_lv_use_2_button.wait_until(3)
    if not pts.is_valid():
        print("---- 找不到使用2張券按鈕")
        return False
    x, y = pts.get_center_pt()
    mouse_move(x, y)
    print("---- 已點擊使用2張券按鈕")

    if not ok(timeout=5):
        return False

    print('---- 等待動畫結束')
    time.sleep(5)

    adventure_explorer_exp_go_mana_button = Button('./img/adventure-explorer-exp-go-mana.png')
    pts = adventure_explorer_exp_go_mana_button.wait_until(3)
    if not pts.is_valid():
        print("---- 找不到前往瑪娜冒險按鈕")
        return False
    x, y = pts.get_center_pt()
    mouse_move(x, y)
    print("---- 已點擊前往瑪娜冒險按鈕")

    adventure_explorer_mana_lv_button = Button('./img/adventure-explorer-mana-lv.png')
    pts = adventure_explorer_mana_lv_button.wait_until(3)
    if not pts.is_valid():
        print("---- 找不到瑪娜冒險任務按鈕")
        return False
    x, y = pts.get_center_pt()
    mouse_move(x, y)
    print("---- 已點擊瑪娜冒險任務按鈕")

    adventure_explorer_lv_use_2_button = Button('./img/adventure-explorer-lv-use-2.png')
    pts = adventure_explorer_lv_use_2_button.wait_until(3)
    if not pts.is_valid():
        print("---- 找不到使用2張券按鈕")
        return False
    x, y = pts.get_center_pt()
    mouse_move(x, y)
    print("---- 已點擊使用2張券按鈕")

    back_explorer_button = Button('./img/back-explorer.png')
    pts = back_explorer_button.wait_until(3)
    if not pts.is_valid():
        print("---- 找不到返回探索TOP")
        return False
    x, y = pts.get_center_pt()
    mouse_move(x, y)
    print("---- 已點擊返回探索TOP按鈕")

    time.sleep(after_wait_sec)

    return True

def action_dungeon(after_wait_sec=3) -> bool:
    print('---- 執行地下城')
    print('---- 先回到主頁')
    if not home():
        return False
    print('---- 前往冒險')
    if not adventure():
        return False


    adventure_dungeon_button = Button('./img/adventure-dungeon.png')
    pts = adventure_dungeon_button.wait_until(3)
    if not pts.is_valid():
        print("---- 找不到地下城按鈕")
        return False
    x, y = pts.get_center_pt()
    mouse_move(x, y, click_after_sec=2)
    print("---- 已點擊地下城按鈕")

    adventure_dungeon_extreme_button = Button('./img/adventure-dungeon-extreme-v.png') # 這邊先只抓Extreme V的地城任務
    pts = adventure_dungeon_extreme_button.wait_until(3)
    if not pts.is_valid():
        print("---- 找不到地下城任務按鈕")
        return False
    x, y = pts.get_center_pt()
    mouse_move(x, y, click_after_sec=2)
    print("---- 已點擊地下城任務按鈕")

    adventure_dungeon_skip_button = Button('./img/adventure-dungeon-skip.png')
    pts = adventure_dungeon_skip_button.wait_until(3)
    if not pts.is_valid():
        print("---- 找不到跳過地下城任務按鈕")
        return False
    x, y = pts.get_center_pt()
    mouse_move(x, y)
    print("---- 已點擊跳過地下城任務按鈕")

    adventure_dungeon_ok_button = Button('./img/adventure-dungeon-ok.png')
    pts = adventure_dungeon_ok_button.wait_until(20)
    if not pts.is_valid():
        print("---- 找不到地下城任務OK按鈕")
        return False
    x, y = pts.get_center_pt()
    mouse_move(x, y)
    print("---- 已點擊地下城任務OK按鈕")

    time.sleep(after_wait_sec)

    return True


if __name__ == '__main__':
    #debug()
    #home()
    #action_skip_scene()

    # daily routine
    action_free_gachapon()
    action_explorer()
    action_dungeon()