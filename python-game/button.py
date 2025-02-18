import arcade
import resource_path

class Button():
    def __init__(
            self,
            game,
            name,
            copy,
            x_center,
            y_center,
            text_x_start,
            text_y_start, 
            width=350,
            height=200,
        ):
        button_texture = arcade.load_texture(resource_path.path("assets/original/Purple Button Big.png"))
        button_pressed_texture = arcade.load_texture(resource_path.path("assets/original/Purple Button Pressed Big.png"))

        applied_text = button_pressed_texture if game.hovered_button == name else button_texture
        
        arcade.draw_texture_rectangle(
            x_center,
            y_center,
            width,
            height,
            applied_text
        )
        
        arcade.draw_text(
            copy,
            text_x_start,
            text_y_start,
            arcade.color.WHITE,
            16,
            width=250,
            align="center",
            font_name="Old School Adventures"
        )
