import time
import mouse

def mouse_move(x, y, click=True, click_before_sec=0, click_after_sec=0):
    original_x, original_y = mouse.get_position()
    mouse.move(x, y, absolute=True)
    if click:
        if click_before_sec:
            time.sleep(click_before_sec)
        mouse.click(button='left')
    mouse.move(original_x, original_y, absolute=True)

    if click_after_sec:
        time.sleep(click_after_sec)
    return
