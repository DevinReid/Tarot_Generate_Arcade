import arcade
import random
import textwrap

speed = random.uniform(.95,1.05)
DEFAULT_FONT_SIZE = 16
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
DEFAULT_LINE_HEIGHT = 24

def draw_outlined_line(
    line,
    x,
    y,
    font_size=18,
    font_name="Old School Adventures",
    color=arcade.color.WHITE,
    outline_color=arcade.color.BLACK,
    outline_thickness=1.2,
    align="left"
):
    """Draw a single line of text with an outline, at a fixed position."""
    # If alpha is 0, don't draw anything
    if isinstance(color, tuple) and len(color) == 4 and color[3] == 0:
        return

    offsets = [
        (-outline_thickness, 0),
        (outline_thickness, 0),
        (0, -outline_thickness),
        (0, outline_thickness),
        (-outline_thickness, -outline_thickness),
        (-outline_thickness, outline_thickness),
        (outline_thickness, -outline_thickness),
        (outline_thickness, outline_thickness),
    ]

    # Draw outline by offsetting in all directions
    for dx, dy in offsets:
        arcade.draw_text(
            text=line,
            start_x=x + dx,
            start_y=y + dy,
            color=outline_color,
            font_size=font_size,
            anchor_x=align,
            font_name=font_name
        )

    # Draw the main text on top
    arcade.draw_text(
        text=line,
        start_x=x,
        start_y=y,
        color=color,
        font_size=font_size,
        anchor_x=align,
        font_name=font_name
    )

def set_typing_text(game, new_text):
    """
    Sets the text to be typed dynamically.
    Only resets typing if the text is different.
    """
    if game.current_text != new_text:  # Only reset if the text is different
        game.current_text = new_text
        game.displayed_text = ""  # Reset displayed text
        game.text_index = 0       # Reset typing progress
        game.typing_timer = 0

def wrap_text_paragraphs(text):
    """Split and wrap the text text into paragraphs."""
    paragraphs = text.split('\n')  # Split the text into paragraphs

    # Handle wrapping logic
    default_width = 35   # Reduced by 30 characters
    last_paragraph_width = 35  # Reduced by 30 characters
    last_index = len(paragraphs) - 1
    wrapped_paragraphs = [
        textwrap.fill(p.strip(), width=last_paragraph_width if i == last_index else default_width)
        for i, p in enumerate(paragraphs) if p.strip()
    ]

    return wrapped_paragraphs

def set_paragraph_typing(game, paragraph, font_size=18, font_name="Old School Adventures", color=arcade.color.WHITE, width=(SCREEN_WIDTH-200)):
    """
    Sets up the typing effect for a multi-line paragraph.
    """
    if not game.lines_to_type or game.current_text != paragraph:  # Prevent resetting
        # First wrap the paragraphs properly
        wrapped_paragraphs = wrap_text_paragraphs(paragraph)
        
        # Join the wrapped paragraphs with newlines
        formatted_text = "\n".join(wrapped_paragraphs)
        
        # Split into individual lines
        lines = formatted_text.split('\n')
        
        game.lines_to_type = lines  # Store all lines
        game.current_line_index = 0  # Start from the first line
        game.line_widths = []
        for line in game.lines_to_type:  # This measure the pixel width of each line dynamically
            text_image = arcade.create_text_image(
                text=line,
                font_size=font_size,
                font_name=font_name,
                text_color=color,
                align="center"
            )
            line_width = text_image.width * 1.5  # Account for the fonts larger size and glyph boxes
            game.line_widths.append(line_width)
        
        set_typing_text(game, game.lines_to_type[0])

def typewriter_lines(
    game,
    center_x,
    start_y,
    font_size=18,
    font_name="Old School Adventures",
    color=arcade.color.WHITE,
    outline_color=arcade.color.BLACK,
    outline_thickness=1.2,
    line_height=DEFAULT_LINE_HEIGHT * 2.5
):
    """
    Renders the pre-wrapped lines in `game.lines_to_type`, using 
    the pre-calculated widths in `game.line_widths` for dynamic centering.
    """
    for i, line in enumerate(game.lines_to_type):
        # Calculate where the line should go vertically
        y = start_y - (i * line_height)

        # Get the pre-calculated width for this line
        line_width = game.line_widths[i]
        
        # Calculate the left-aligned starting position from the center line
        adjusted_x = center_x - (line_width // 2)

        if i < game.current_line_index:
            # Fully typed line
            draw_outlined_line(
                line=line,
                x=adjusted_x,
                y=y,
                font_size=font_size,
                font_name=font_name,
                color=color,
                outline_color=outline_color,
                outline_thickness=outline_thickness
            )
        elif i == game.current_line_index:
            # Current line in the process of typing
            draw_outlined_line(
                line=game.displayed_text,
                x=adjusted_x,
                y=y,
                font_size=font_size,
                font_name=font_name,
                color=color,
                outline_color=outline_color,
                outline_thickness=outline_thickness
            )

def update_typing_effect(game, delta_time):
    """
    Updates the typing effect, moving to the next line if necessary.
    """
    game.typing_timer += delta_time
    
    if game.typing_timer >= game.typing_speed:
        if game.text_index < len(game.current_text):  # Typing the current line
            game.text_index += 1
            game.displayed_text = game.current_text[:game.text_index]
            
            if hasattr(game, "sound_manager"):
                if not game.visited_stages[game.stage]:
                    if game.text_index % 2 == 0:
                        game.sound_manager.play_sfx("typewriter", volume=.5, speed=speed)

            game.typing_timer = 0
        else:  # Current line is finished
            if game.current_line_index < len(game.lines_to_type) - 1:
                # Move to the next line
                game.current_line_index += 1
                set_typing_text(game, game.lines_to_type[game.current_line_index])
            else:
                # All lines are finished
                game.typing_complete = True

def reset_typing_state(game):
    """
    Resets typing-related state for transitioning to a new stage or card.
    """
    game.active_card_index = None
    game.current_line_index = 0
    game.lines_to_type = []
    game.current_text = ""
    game.displayed_text = ""
    game.typing_complete = False 