import random
import arcade
import os
import resource_path

positions = ['Upright', 'Reversed']

""" Variables for Copyright / Open Source Asset Switcher """

copyright_asset_path = resource_path.path("assets/copyright")
backup_assets_path = resource_path.path("assets/riderWeightPublicDomain/convertedx2")
current_asset_path = None
current_card_back_path = None
copyright_card_back_path = "backing_diamond_4x.png"
backup_card_back_path = "CardBacks.png"

if os.path.isdir(copyright_asset_path):
    current_asset_path = copyright_asset_path
    current_card_back_path = copyright_card_back_path
    is_backup = False
else:
    current_asset_path = backup_assets_path
    current_card_back_path = backup_card_back_path
    is_backup = True

class Card:
    def __init__(self, name, file_name):
        self.name = name 
        self.file_name = file_name
        self.dir_path = current_asset_path
        self.card_back_file_name = current_card_back_path
        self.position = positions[0]
        texture = arcade.load_texture(os.path.join(f"/{self.dir_path}/{self.file_name}"))
        self.width = texture.width
        self.height = texture.height
        self.x = 0
        self.y = 0
        self.x_offset = random.randint(-3, 3)  # Pre-generate random x offset
        self.y_offset = random.randint(-3, 3)   # Pre-generate random y offset
        self.rotation_angle = random.uniform(-2, 2)  # Pre-generate random rotation

    def __str__(self):
        return f"{self.name} - {self.position}"

    def reverse(self):
        self.position = positions[1]

    def paint(self, x, y, show_front, is_hovered = False, scale =.9, is_small = False, angle = 0):
        self.x = x
        self.y = y
        if is_small:
           scale /= 2
        if is_backup:
            scale = scale

        width = self.width * scale
        height = self.height * scale

        if is_hovered:
            y += 30  # Lift the card when hovered
            arcade.draw_rectangle_outline(
                center_x=x,
                center_y=y,
                width=width*.98,
                height=height*.98,
                color=arcade.color.LIGHT_BLUE,
                border_width=5,
                tilt_angle=angle,  # Rotate the outline to match the card
            )

        if show_front:
                texture_path = os.path.join(self.dir_path, self.file_name)
        else:
                texture_path = os.path.join(self.dir_path, self.card_back_file_name)

        texture = arcade.load_texture(texture_path)

        if self.position == positions[0]:
            arcade.draw_scaled_texture_rectangle(x, y, texture, scale, 0+angle,)
        else:
            arcade.draw_scaled_texture_rectangle(x, y, texture, scale, 180+angle)

    def is_clicked(self, mouse_x, mouse_y):
        """ Check if the card is clicked based on mouse coordinates. """
        half_width = (self.width ) // 4
        half_height = (self.height) // 4
        clicked = (self.x - half_width < mouse_x < self.x + half_width and
                self.y - half_height < mouse_y < self.y + half_height)

        return clicked


class TarotDeck:
    def __init__(self):
        self.cards = []
        

        if os.path.isdir(copyright_asset_path):
                self.cards = [
    # Major Arcana
                Card("The Fool", "major0_fool.1.png"),
                Card("The Magician", "major1_magician.1.png"),
                Card("The High Priestess", "major2_priestess.1.png"),
                Card("The Empress", "major3_empress.1.png"),
                Card("The Emperor", "major4_emperor.1.png"),
                Card("The Hierophant", "major5_hierophant.1.png"),
                Card("The Lovers", "major6_lovers.1.png"),
                Card("The Chariot", "major7_chariot.1.png"),
                Card("Strength", "major8_strength.1.png"),
                Card("The Hermit", "major9_hermit.1.png"),
                Card("Wheel of Fortune", "major10_wheel.1.png"),
                Card("Justice", "major11_justice.1.png"),
                Card("The Hanged Man", "major12_hanged.1.png"),
                Card("Death", "major13_death.1.png"),
                Card("Temperance", "major14_temperance.1.png"),
                Card("The Devil", "major15_devil.1.png"),
                Card("The Tower", "major16_tower.1.png"),
                Card("The Star", "major17_star.1.png"),
                Card("The Moon", "major18_moon.1.png"),
                Card("The Sun", "major19_sun.1.png"),  
                Card("Judgement", "major20_judgement.1.png"),
                Card("The World", "major21_world.1.png"),

                # Cups
                Card("Ace of Cups", "cups1.1.png"),
                Card("Two of Cups", "cups2.1.png"),
                Card("Three of Cups", "cups3.1.png"),
                Card("Four of Cups", "cups4.1.png"),
                Card("Five of Cups", "cups5.1.png"),
                Card("Six of Cups", "cups6.1.png"),
                Card("Seven of Cups", "cups7.1.png"),
                Card("Eight of Cups", "cups8.1.png"),
                Card("Nine of Cups", "cups9.1.png"),
                Card("Ten of Cups", "cups10.1.png"),
                Card("Page of Cups", "cupsP.1.png"),
                Card("Knight of Cups", "cupsKn.1.png"),
                Card("Queen of Cups", "cupsQ.1.png"),
                Card("King of Cups", "cupsK.1.png"),

                # Pentacles
                Card("Ace of Pentacles", "pentacles1.1.png"),
                Card("Two of Pentacles", "pentacles2.1.png"),
                Card("Three of Pentacles", "pentacles3.1.png"),
                Card("Four of Pentacles", "pentacles4.1.png"),
                Card("Five of Pentacles", "pentacles5.1.png"),
                Card("Six of Pentacles", "pentacles6.1.png"),
                Card("Seven of Pentacles", "pentacles7.1.png"),
                Card("Eight of Pentacles", "pentacles8.1.png"),
                Card("Nine of Pentacles", "pentacles9.1.png"),
                Card("Ten of Pentacles", "pentacles10.1.png"),
                Card("Page of Pentacles", "pentaclesP.1.png"),
                Card("Knight of Pentacles", "pentaclesKn.1.png"),
                Card("Queen of Pentacles", "pentaclesQ.1.png"),
                Card("King of Pentacles", "pentaclesK.1.png"),

                # Swords
                Card("Ace of Swords", "swords1.1.png"),
                Card("Two of Swords", "swords2.1.png"),
                Card("Three of Swords", "swords3.1.png"),
                Card("Four of Swords", "swords4.1.png"),
                Card("Five of Swords", "swords5.1.png"),
                Card("Six of Swords", "swords6.1.png"),
                Card("Seven of Swords", "swords7.1.png"),
                Card("Eight of Swords", "swords8.1.png"),
                Card("Nine of Swords", "swords9.1.png"),
                Card("Ten of Swords", "swords10.1.png"),
                Card("Page of Swords", "swordsP.1.png"),
                Card("Knight of Swords", "swordsKn.1.png"),
                Card("Queen of Swords", "swordsQ.1.png"),
                Card("King of Swords", "swordsK.1.png"),

                # Wands
                Card("Ace of Wands", "wands1.1.png"),
                Card("Two of Wands", "wands2.1.png"),
                Card("Three of Wands", "wands3.1.png"),
                Card("Four of Wands", "wands4.1.png"),
                Card("Five of Wands", "wands5.1.png"),
                Card("Six of Wands", "wands6.1.png"),
                Card("Seven of Wands", "wands7.1.png"),
                Card("Eight of Wands", "wands8.1.png"),
                Card("Nine of Wands", "wands9.1.png"),
                Card("Ten of Wands", "wands10.1.png"),
                Card("Page of Wands", "wandsP.1.png"),
                Card("Knight of Wands", "wandsKn.1.png"),
                Card("Queen of Wands", "wandsQ.1.png"),
                Card("King of Wands", "wandsK.1.png")
                ]

                self.card_back = Card("Card Back", "backing_diamond_4x.png")
        else: 
            self.cards = [
                # Major Arcana
                Card("The Fool", "00-TheFool.png"),
                Card("The Magician", "01-TheMagician.png"),
                Card("The High Priestess", "02-TheHighPriestess.png"),
                Card("The Empress", "03-TheEmpress.png"),
                Card("The Emperor", "04-TheEmperor.png"),
                Card("The Hierophant", "05-TheHierophant.png"),
                Card("The Lovers", "06-TheLovers.png"),
                Card("The Chariot", "07-TheChariot.png"),
                Card("Strength", "08-Strength.png"),
                Card("The Hermit", "09-TheHermit.png"),
                Card("Wheel of Fortune", "10-WheelOfFortune.png"),
                Card("Justice", "11-Justice.png"),
                Card("The Hanged Man", "12-TheHangedMan.png"),
                Card("Death", "13-Death.png"),
                Card("Temperance", "14-Temperance.png"),
                Card("The Devil", "15-TheDevil.png"),
                Card("The Tower", "16-TheTower.png"),
                Card("The Star", "17-TheStar.png"),
                Card("The Moon", "18-TheMoon.png"),
                Card("The Sun", "19-TheSun.png"),
                Card("Judgement", "20-Judgement.png"),
                Card("The World", "21-TheWorld.png"),
                
               
                # Cups (Ace=01, Two=02, ..., Ten=10, Page=11, Knight=12, Queen=13, King=14)
                Card("Ace of Cups", "Cups01.png"),
                Card("Two of Cups", "Cups02.png"),
                Card("Three of Cups", "Cups03.png"),
                Card("Four of Cups", "Cups04.png"),
                Card("Five of Cups", "Cups05.png"),
                Card("Six of Cups", "Cups06.png"),
                Card("Seven of Cups", "Cups07.png"),
                Card("Eight of Cups", "Cups08.png"),
                Card("Nine of Cups", "Cups09.png"),
                Card("Ten of Cups", "Cups10.png"),
                Card("Page of Cups", "Cups11.png"),
                Card("Knight of Cups", "Cups12.png"),
                Card("Queen of Cups", "Cups13.png"),
                Card("King of Cups", "Cups14.png"),
                
                # Pentacles (Ace=01, Two=02, ..., Ten=10, Page=11, Knight=12, Queen=13, King=14)
                Card("Ace of Pentacles", "Pentacles01.png"),
                Card("Two of Pentacles", "Pentacles02.png"),
                Card("Three of Pentacles", "Pentacles03.png"),
                Card("Four of Pentacles", "Pentacles04.png"),
                Card("Five of Pentacles", "Pentacles05.png"),
                Card("Six of Pentacles", "Pentacles06.png"),
                Card("Seven of Pentacles", "Pentacles07.png"),
                Card("Eight of Pentacles", "Pentacles08.png"),
                Card("Nine of Pentacles", "Pentacles09.png"),
                Card("Ten of Pentacles", "Pentacles10.png"),
                Card("Page of Pentacles", "Pentacles11.png"),
                Card("Knight of Pentacles", "Pentacles12.png"),
                Card("Queen of Pentacles", "Pentacles13.png"),
                Card("King of Pentacles", "Pentacles14.png"),
                
                # Swords (Ace=01, Two=02, ..., Ten=10, Page=11, Knight=12, Queen=13, King=14)
                Card("Ace of Swords", "Swords01.png"),
                Card("Two of Swords", "Swords02.png"),
                Card("Three of Swords", "Swords03.png"),
                Card("Four of Swords", "Swords04.png"),
                Card("Five of Swords", "Swords05.png"),
                Card("Six of Swords", "Swords06.png"),
                Card("Seven of Swords", "Swords07.png"),
                Card("Eight of Swords", "Swords08.png"),
                Card("Nine of Swords", "Swords09.png"),
                Card("Ten of Swords", "Swords10.png"),
                Card("Page of Swords", "Swords11.png"),
                Card("Knight of Swords", "Swords12.png"),
                Card("Queen of Swords", "Swords13.png"),
                Card("King of Swords", "Swords14.png"),
                
                # Wands (Ace=01, Two=02, ..., Ten=10, Page=11, Knight=12, Queen=13, King=14)
                Card("Ace of Wands", "Wands01.png"),
                Card("Two of Wands", "Wands02.png"),
                Card("Three of Wands", "Wands03.png"),
                Card("Four of Wands", "Wands04.png"),
                Card("Five of Wands", "Wands05.png"),
                Card("Six of Wands", "Wands06.png"),
                Card("Seven of Wands", "Wands07.png"),
                Card("Eight of Wands", "Wands08.png"),
                Card("Nine of Wands", "Wands09.png"),
                Card("Ten of Wands", "Wands10.png"),
                Card("Page of Wands", "Wands11.png"),
                Card("Knight of Wands", "Wands12.png"),
                Card("Queen of Wands", "Wands13.png"),
                Card("King of Wands", "Wands14.png")
            ]
            self.card_back = Card("Card Backs", "CardBacks.png")

    def __str__(self):
        returned_str = ""
        for card in self.cards:
            returned_str += str(card) + "\n"
        return returned_str

    def shuffle(self):
        random.shuffle(self.cards)
        for card in self.cards:
            coin_flip = random.randrange(0, 2)
            if coin_flip == 1:
                card.reverse()

    def draw(self, num):
        return self.cards[0: num]
