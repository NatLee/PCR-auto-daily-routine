
import mouse

def mouse_move(x, y, click=True):
    original_x, original_y = mouse.get_position()
    mouse.move(x, y, absolute=True)
    if click:
        mouse.click(button='left')
    mouse.move(original_x, original_y, absolute=True)
    return
