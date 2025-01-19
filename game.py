import arcade
import threading
import pyglet
from deck import TarotDeck
from tarot_bot import TarotBot
from enum import Enum

# Screen title and size
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
DEFAULT_LINE_HEIGHT = 24
DEFAULT_FONT_SIZE = 16
FONT_PATH = r"assets\fonts\OldSchoolAdventures-42j9.ttf"


INTRO_TEXT = (
    "Ah, welcome, traveler!\n\n"
    "I am Mama Nyah, and the spirits have brought you to me for a reason.\n\n"
    "Sit, relax, and let us see what the universe whispers for you.\n\n"
    "But first, tell me—what is your intention? What does your heart seek to know, heal, or discover?\n\n"
    "Speak it, and we will find the truth together."
)

CATEGORIES = ["Love Life", "Professional Development", "Family and Friends", "Health", "Personal Growth", "Gain Clarity"]

class GameState(Enum): #UPDATE THIS TO BE IN CORRECT ORDER 
    INTRO = 1,
    DRAWN = 2,
    LOADING = 3,
    SPREAD = 4

class TarotGame(arcade.Window):
    """ Main application class. """

    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Voodoo Tarot GPT")
        self.tarot_bot = TarotBot()
        self.stage = GameState.INTRO
        self.intention = None
        self.drawn_cards = None
        self.fortune = None
        self.hovered_card = None
        self.hovered_button = None  # Track which button is hovered
        self.clicked_button = None  # Track which button is clicked
        self.current_revealed_card = None
        self.reveal_active= False
        self.start_reading_button_active = False
        self.background_image = arcade.load_texture("assets\original\TableClothbigger.png")
        arcade.set_background_color(arcade.color.IMPERIAL_PURPLE)
       
      
        pyglet.font.add_file(FONT_PATH)  # Load the font file
           


    def setup(self):
        """ Set up the game here. Call this function to restart the game. """
        pass

    def on_draw(self):
        """ Render the screen. """
        # Clear the screen
    
        self.clear()

        arcade.draw_lrwh_rectangle_textured(0,0, SCREEN_WIDTH, SCREEN_HEIGHT, self.background_image)

        if self.stage == GameState.INTRO:
            self.__draw_intro_stage()
        elif self.stage == GameState.DRAWN:
            self.__draw_drawn_stage()
        elif self.stage == GameState.LOADING:
            self.__draw_loading_stage()
        elif self.stage == GameState.SPREAD:
            self.__draw_spread_stage()
            

    def on_mouse_press(self, x, y, _button, _key_modifiers):
        
        if self.stage == GameState.INTRO:
            # Button positions
            button_positions = [
                (275, 300),  # Button 0
                (650, 300),  # Button 1
                (1025, 300),  # Button 2
                (275, 150),  # Button 3
                (650, 150),  # Button 4
                (1025, 150)  # Button 5
            ]

            # Check if a button is clicked
            for i, (bx, by) in enumerate(button_positions):
                if bx - 175 <= x <= bx + 175 and by - 100 <= y <= by + 100:  # Button bounds
                    self.clicked_button = f"button_{i}"
                    self.set_intention(CATEGORIES[i])  # Set intention based on button index
                    return
            
        elif self.stage == GameState.SPREAD:
           
            if self.reveal_active:
                if SCREEN_WIDTH // 2 - 175 <= x <= SCREEN_WIDTH // 2 + 175 and 25 <= y <= 125:
                    # Dismiss popup and place the revealed card in the corner
                    self.reveal_active = False
    
                    self.current_revealed_card = None
                    if len(self.selected_cards) == 3:
                        self.start_reading_button_active = True
                    if len(self.selected_cards) == 3:
                        self.drawn_cards = self.selected_cards
                        self.start_loading()
                        self.start_reading_button_active = False
                    return
                    

            # if self.start_reading_button_active and SCREEN_WIDTH // 2 - 175 <= x <= SCREEN_WIDTH // 2 + 175 and 25 <= y <= 125:
            #     self.stage = GameState.LOADING  # Proceed to the next stage
            #     self.start_reading_button_active = False
            #     return
            
            if not self.reveal_active:
                for card in reversed(self.deck.cards):
                    if card.is_clicked(x, y):
                        self.deck.cards.remove(card)
                        self.reveal_card(card) 
                        # Trigger popup for selected card
                        return

            

            
    def on_mouse_motion(self, x, y, dx, dy):
        """ Handle mouse movement to track hovered card. """
        self.hovered_card = None  

        self.hovered_button = None

        if self.stage == GameState.INTRO:
            # Loop through button positions and detect hover
            for i, (bx, by) in enumerate([
                (275, 300),  # Button 0
                (650, 300),  # Button 1
                (1025, 300),  # Button 2
                (275, 150),  # Button 3
                (650, 150),  # Button 4
                (1025, 150)  # Button 5
            ]):
                # Check if the mouse is within the button's bounds
                if bx - 175 <= x <= bx + 175 and by - 100 <= y <= by + 100:
                    self.hovered_button = f"button_{i}"
                    break

        if self.stage == GameState.SPREAD:
            # do reverse for topmost card

            if self.reveal_active:
                self.hovered_card = None
                self.hovered_button = "pull_next" if SCREEN_WIDTH // 2 - 175 <= x <= SCREEN_WIDTH // 2 + 175 and 25 <= y <= 125 else None
                return
            
            elif self.start_reading_button_active and SCREEN_WIDTH // 2 - 175 <= x <= SCREEN_WIDTH // 2 + 175 and 25 <= y <= 125:
                self.hovered_button = "begin_reading"

            # Normal hover behavior
            self.hovered_card = None
            self.hovered_button = None

            for card in reversed(self.deck.cards):
                if card.is_clicked(x, y): 
                    self.hovered_card = card
                    break
           
        

            # Check if hovering over "Begin Reading" button


    def set_intention(self, intention_text):
        """ Set the intention and transition to the spread stage. """
        self.intention = intention_text
        self.stage = GameState.SPREAD
        self.selected_cards = []  # reset selected cards for spread
        self.deck = TarotDeck()  # prepare deck
        self.deck.shuffle()

    def reveal_card(self, card):
        if card not in self.selected_cards:
            self.selected_cards.append(card)  # Add the card to selected cards
        self.current_revealed_card = card  # Track the card being revealed
        self.reveal_active = True  

    def start_loading(self):
        self.stage = GameState.LOADING
        self.loading_progress = 0.0
        self.api_call_complete = False

        
        def api_call():
            self.fortune = self.tarot_bot.fortune(self.drawn_cards, self.intention)
            self.api_call_complete = True

        threading.Thread(target=api_call).start()

    def on_update(self, delta_time):
        """ Update the game state. """
        if self.stage == GameState.LOADING:
            if not self.api_call_complete:
                # load progress bar with api is called
                self.loading_progress += delta_time / 5  # adjust speed
                self.loading_progress = min(self.loading_progress, 0.95)  # cap at 95%
            else:
                # finish progress bar if api is done loading first
                self.loading_progress += delta_time / 2  
                if self.loading_progress >= 1.0:
                    self.loading_progress = 1.0
                    self.stage = GameState.DRAWN


    def __draw_intro_stage(self):
        # Load textures
        self.button_texture = arcade.load_texture("assets/original/Purple Button Big.png")
        self.button_pressed_texture = arcade.load_texture("assets/original/Purple Button Pressed Big.png")

        # Intro text
        arcade.draw_text(
            INTRO_TEXT,
            0,
            SCREEN_HEIGHT - DEFAULT_LINE_HEIGHT * 5,
            arcade.color.WHITE,
            DEFAULT_FONT_SIZE,
            width=SCREEN_WIDTH,
            multiline=True,
            align="center",
            font_name="Old School Adventures"
        )

        # Button positions
        button_positions = [
            (275, 300),  # Button 0
            (650, 300),  # Button 1
            (1025, 300),  # Button 2
            (275, 150),  # Button 3
            (650, 150),    # Button 4
            (1025, 150)     # Button 5
        ]

        # Loop through categories and draw buttons
        for i, (x, y) in enumerate(button_positions):
            button_texture = (
                self.button_pressed_texture if self.hovered_button == f"button_{i}" else self.button_texture
            )
            arcade.draw_texture_rectangle(x, y, 350, 200, button_texture)

            arcade.draw_text(
                CATEGORIES[i],
                x - 125,  # Center text
                y,   # Position text slightly below center
                arcade.color.WHITE,
                DEFAULT_FONT_SIZE,
                width=250,
                align="center",
                font_name="Old School Adventures"
            )


    def __draw_drawn_stage(self):
        arcade.draw_text("Cards:",
                100,
                SCREEN_HEIGHT - DEFAULT_LINE_HEIGHT * 1.5,
                arcade.color.WHITE,
                DEFAULT_FONT_SIZE,
                width=500,
                align="left")
            
        for i, card in enumerate(self.drawn_cards):
            card.paint(150 + (i * 300), 550, show_front = True)

        arcade.draw_text("Fortune:",
                        100,
                        400,
                        arcade.color.WHITE,
                        DEFAULT_FONT_SIZE,
                        width=500,
                        align="left")
        
        arcade.draw_text(self.fortune,
                        100,
                        350,
                        arcade.color.WHITE,
                        DEFAULT_FONT_SIZE / 1.5,
                        multiline=True,
                        width=SCREEN_WIDTH - 100,
                        align="left")


    def __draw_loading_stage(self):
        """ Render the loading screen. """
       
        arcade.draw_text(
            "Loading, please wait...",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - DEFAULT_LINE_HEIGHT * 2,
            arcade.color.WHITE,
            DEFAULT_FONT_SIZE,
            width=SCREEN_WIDTH,
            align="center",
            anchor_x="center"
        )
        
    
        arcade.draw_lrtb_rectangle_filled(
            200, 
            800, 
            300, 
            250, 
            arcade.color.IMPERIAL_BLUE
        )
        
        
        progress_width = 200 + (self.loading_progress * 600)  # Scales from 200 to 800
        arcade.draw_lrtb_rectangle_filled(
            200, 
            progress_width, 
            300, 
            250, 
            arcade.color.INCHWORM
        )
        
       
        arcade.draw_text(
            "Please hold on while we prepare your reading...",
            SCREEN_WIDTH // 2,
            200,
            arcade.color.WHITE,
            DEFAULT_FONT_SIZE / 1.5,
            width=SCREEN_WIDTH - 200,
            align="center",
            anchor_x="center"
        )

    def __draw_spread_stage(self):
        """ Render the card spread stage with the backs of the cards. """
        if self.reveal_active and self.current_revealed_card:
            # Draw the revealed card in the center
            self.current_revealed_card.paint(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, show_front=True, scale=1.8, is_small=False)

            if len(self.selected_cards) < 3:
                    button_texture = (
                        self.button_pressed_texture if self.hovered_button == "pull_next" else self.button_texture
                    )
                    button_text = "Pull Next Card"
            else:
                    button_texture = (
                        self.button_pressed_texture if self.hovered_button == "begin_reading" else self.button_texture
                    )
                    button_text = "Begin Reading"

            arcade.draw_texture_rectangle(SCREEN_WIDTH // 2, 75, 350, 200, button_texture)

            arcade.draw_text(
                    button_text,
                    SCREEN_WIDTH // 2 - 125,
                    60,
                    arcade.color.WHITE,
                    DEFAULT_FONT_SIZE,
                    width=250,
                    align="center",
                    font_name="Old School Adventures"
                )
            
            arcade.draw_text(
                f"{self.current_revealed_card.name}",
                SCREEN_WIDTH // 2,
                SCREEN_HEIGHT - DEFAULT_LINE_HEIGHT * 4.5,
                arcade.color.WHITE,
                DEFAULT_FONT_SIZE * 1.8,
                width=SCREEN_WIDTH,
                align="center",
                anchor_x="center",
                font_name="Old School Adventures"
            )

            if len(self.selected_cards) >1 and self.selected_cards[1]:

                x = 300 
                y = 200  
                self.selected_cards[0].paint(x, y, show_front=True, is_small=True)
            
            if len(self.selected_cards) > 2 and self.selected_cards[2]:

                x=975
                y=200
                self.selected_cards[1].paint(x,y,show_front=True, is_small = True)

            return  # Stop drawing the rest of the stage while reveal is active


        # Draw instruction text
        arcade.draw_text(
            "Choose 3 Cards:",
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT - DEFAULT_LINE_HEIGHT * 4.5,
            arcade.color.WHITE,
            DEFAULT_FONT_SIZE *1.5,
            width=SCREEN_WIDTH,
            align="center",
            anchor_x="center",
            font_name="Old School Adventures"
        )

        # Draw the cards
        card_spacing = (SCREEN_WIDTH - 300) // len(self.deck.cards)  # Dynamic spacing
        for i, card in enumerate(self.deck.cards):
            x = 150 + (i * card_spacing)
            y = SCREEN_HEIGHT // 2
            card.paint(x, y, show_front=False, is_hovered=(card == self.hovered_card), is_small=True)

        # Draw previously selected cards in the left corner
        for i, card in enumerate(self.selected_cards):
            x = 300 + (i * 675)  # Spaced out horizontally with 150 pixels between cards
            y = 200  # Fixed y-coordinate for all cards
            card.paint(x, y, show_front=True, is_small=True)

       



        


def main():
    """ Main function """
    window = TarotGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()