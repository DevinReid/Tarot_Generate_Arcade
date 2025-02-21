import arcade
import random
import textwrap

speed = random.uniform(.95,1.05)
DEFAULT_FONT_SIZE = 16
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
DEFAULT_LINE_HEIGHT = 24

def typewriter_lines(
    game,
    center_x,
    start_y,
    font_size=18,
    font_name="Old School Adventures",
    color=arcade.color.WHITE,
    outline_color=arcade.color.BLACK,
    outline_thickness=1.2,
    line_height=DEFAULT_LINE_HEIGHT * 1.5
):
    """
    Renders the pre-wrapped lines in `game.lines_to_type`, using 
    the pre-calculated widths in `game.line_widths` for dynamic centering.
    This fixes the start of each line at the left alignment, but moves the x of each line to appear to be center aligned.
    The typewriter script effect only looks correct if its left aligned.
    """
    # if not game.line_widths:
    #     # Ensure line_widths exist, otherwise recalculate (Prevents empty list bugs)
    #     game.line_widths = []
    #     for line in game.lines_to_type:
    #         text_image = arcade.create_text_image(
    #             text=line,
    #             font_size=font_size,
    #             font_name=font_name,
    #             text_color=color,
    #             align="center"
    #         )
    #         line_width = text_image.width * 1.5
    #         game.line_widths.append(line_width)  # Store width

    for i, line in enumerate(game.lines_to_type):
        # Calculate where the line should go vertically
        y = start_y - (i * line_height)

        # Get the pre-calculated width for this line, this is calculated below in set_paragraph_typing()
        line_width = game.line_widths[i]
        
        # Calculate the left-aligned starting position from the center line
        adjusted_x = center_x - (line_width // 2)

        

        ## Determine which line is fully typed vs. the current typing line
        ## This keeps fully typed lines static, while moving to the next one, instead of printing each line over and over again, often times at the same time
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
            # Current line in the process of typing (game.displayed_text)
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
        # else: future lines after current_line_index remain unrendered (or blank)

        ## This is my debug tool for measuring the font's actual size, in set_paragraph_typing(), I set the line_width here, line_width = text_image.width * 1.5
        ## This helps us see where the actualy visual of the text box lies, because the internal measurement of the line_width is set for a standard, smaller font
        ## For the typewriter effect to be actually centered, we need the line_width in pixels to match what we see on screen for use in the adjusted_x above
        ## Let's keep this in case i need to adjust the font later

            # arcade.draw_rectangle_outline(
            #     center_x=adjusted_x + line_width / 2,
            #     center_y=y + font_size / 2,  # approximate vertical center
            #     width=line_width,
            #     height=font_size,
            #     color=arcade.color.RED
            # )


def draw_outlined_line(
        line,
        x,
        y,
        font_size=18,
        font_name="Old School Adventures",
        color=arcade.color.WHITE,
        outline_color=arcade.color.BLACK,
        outline_thickness=1.2,
        align = "left"
    ):
        

        """Draw a single line of text with an outline, at a fixed position."""


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


def set_paragraph_typing(game, paragraph, font_size=18, font_name = "Old School Adventures", color=arcade.color.WHITE, width =(SCREEN_WIDTH-200)):
    """
    Sets up the typing effect for a multi-line paragraph.
    """
    
    if not game.lines_to_type or game.current_text != paragraph:  # Prevent resetting
        lines = []
        for block in paragraph.split("\n\n"):  # Split into paragraphs
            wrapped_lines = textwrap.wrap(block, width= width // font_size)
            lines.extend(wrapped_lines + [""])  # Add wrapped lines and an empty line for spacing

        game.lines_to_type = lines  # Store all lines
        game.current_line_index = 0  # Start from the first line
        game.line_widths = []
        for line in game.lines_to_type:  ## This measure the pixel width of each line dynamically
            text_image = arcade.create_text_image(
                text=line,
                font_size=font_size,
                font_name=font_name,
                text_color=color,
                align= "center"
            )
            line_width = text_image.width * 1.5 ##Account for the fonts larger size and glyph boxes
          
            game.line_widths.append(line_width) 
            
        
        set_typing_text(game, game.lines_to_type[0])  


def draw_outlined_paragraph(
    game,
    center_x,
    start_y,
    font_size=16,
    font_name="Old School Adventures",
    color=arcade.color.WHITE,
    outline_color=arcade.color.BLACK,
    outline_thickness=1.2,
    line_height=DEFAULT_LINE_HEIGHT * 1.5,
):
    """Draws a paragraph using pre-wrapped text from `game.lines_to_type`, preventing double wrapping."""
    
    if not game.lines_to_type:
        return  # Prevent drawing if there's no text

    for i, line in enumerate(game.lines_to_type):  
        y = start_y - (i * line_height)

        # Ensure width is calculated the same way as in set_paragraph_typing()
        line_width = game.line_widths[i]  # Use pre-stored widths
        adjusted_x = center_x - (line_width // 2)

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
                            if game.text_index % 2 == 0:
                                game.sound_manager.play_sfx("typewriter", volume=.5, speed = speed)


            game.typing_timer = 0
        else:  # Current line is finished
            if game.current_line_index < len(game.lines_to_type) - 1:
                # Move to the next line
                
                game.current_line_index += 1
                #Debug tool for checking line width
                # debug_x_list =[]
                # for line in game.line_widths:
                #     debug_x_list.append((SCREEN_WIDTH //2)- (line //2))
                    # print(f"{debug_x_list}")
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

def wrap_text_paragraphs(text):
    """Split and wrap the text text into paragraphs."""

    paragraphs = text.split('\n')  # Split the text into paragraphs

    # Handle wrapping logic
    default_width = 40
    last_paragraph_width = 55
    last_index = len(paragraphs) - 1
    wrapped_paragraphs = [
        textwrap.fill(p.strip(), width=last_paragraph_width if i == last_index else default_width)
        for i, p in enumerate(paragraphs) if p.strip()
    ]

    return wrapped_paragraphs

