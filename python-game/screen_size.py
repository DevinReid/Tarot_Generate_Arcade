import arcade

TARGET_WIDTH = 1280
TARGET_HEIGHT = 960
TARGET_ASPECT = TARGET_WIDTH / TARGET_HEIGHT
DEFAULT_LINE_HEIGHT = 24

def init_screen(window, fullscreen=False):
    """call to initialize the window mode (fullscreen or windowed)"""
    if fullscreen:
        window.set_fullscreen(True)
    else:
        # pick a default windowed size:
        window.set_fullscreen(False)
        window.set_size(TARGET_WIDTH, TARGET_HEIGHT)

def handle_resize(window, width, height):
    """ Called from window.on_resize or manually.
    Adjusts viewport to maintain a 4:3 (TARGET_ASPECT) letterboxed area
    """
    user_aspect = width / height

    if user_aspect > TARGET_ASPECT:
        # Screen is relatively wide; letterbox top/bottom
        new_width = TARGET_ASPECT * height  
        x_margin = (width - new_width) / 2
        
        arcade.set_viewport(-x_margin, TARGET_WIDTH + x_margin, 0, TARGET_HEIGHT)
    else:
        # Screen is relatively tall; letterbox left/right
        new_height = width / TARGET_ASPECT
        y_margin = (height - new_height) / 2
        arcade.set_viewport(0, TARGET_WIDTH, -y_margin, TARGET_HEIGHT + y_margin)
