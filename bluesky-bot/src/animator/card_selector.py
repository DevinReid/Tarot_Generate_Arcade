import random
from typing import Tuple, Dict
import os

class CardSelector:
    def __init__(self, assets_dir: str = "assets"):
        self.assets_dir = os.path.join(assets_dir, "cards", "copyright")
        self.cards = [
            # Major Arcana
            ("The Fool", "major0_fool.1.png"),
            ("The Magician", "major1_magician.1.png"),
            ("The High Priestess", "major2_priestess.1.png"),
            ("The Empress", "major3_empress.1.png"),
            ("The Emperor", "major4_emperor.1.png"),
            ("The Hierophant", "major5_hierophant.1.png"),
            ("The Lovers", "major6_lovers.1.png"),
            ("The Chariot", "major7_chariot.1.png"),
            ("Strength", "major8_strength.1.png"),
            ("The Hermit", "major9_hermit.1.png"),
            ("Wheel of Fortune", "major10_wheel.1.png"),
            ("Justice", "major11_justice.1.png"),
            ("The Hanged Man", "major12_hanged.1.png"),
            ("Death", "major13_death.1.png"),
            ("Temperance", "major14_temperance.1.png"),
            ("The Devil", "major15_devil.1.png"),
            ("The Tower", "major16_tower.1.png"),
            ("The Star", "major17_star.1.png"),
            ("The Moon", "major18_moon.1.png"),
            ("The Sun", "major19_sun.1.png"),
            ("Judgement", "major20_judgement.1.png"),
            ("The World", "major21_world.1.png"),

            # Cups
            ("Ace of Cups", "cups1.1.png"),
            ("Two of Cups", "cups2.1.png"),
            ("Three of Cups", "cups3.1.png"),
            ("Four of Cups", "cups4.1.png"),
            ("Five of Cups", "cups5.1.png"),
            ("Six of Cups", "cups6.1.png"),
            ("Seven of Cups", "cups7.1.png"),
            ("Eight of Cups", "cups8.1.png"),
            ("Nine of Cups", "cups9.1.png"),
            ("Ten of Cups", "cups10.1.png"),
            ("Page of Cups", "cupsP.1.png"),
            ("Knight of Cups", "cupsKn.1.png"),
            ("Queen of Cups", "cupsQ.1.png"),
            ("King of Cups", "cupsK.1.png"),

            # Pentacles
            ("Ace of Pentacles", "pentacles1.1.png"),
            ("Two of Pentacles", "pentacles2.1.png"),
            ("Three of Pentacles", "pentacles3.1.png"),
            ("Four of Pentacles", "pentacles4.1.png"),
            ("Five of Pentacles", "pentacles5.1.png"),
            ("Six of Pentacles", "pentacles6.1.png"),
            ("Seven of Pentacles", "pentacles7.1.png"),
            ("Eight of Pentacles", "pentacles8.1.png"),
            ("Nine of Pentacles", "pentacles9.1.png"),
            ("Ten of Pentacles", "pentacles10.1.png"),
            ("Page of Pentacles", "pentaclesP.1.png"),
            ("Knight of Pentacles", "pentaclesKn.1.png"),
            ("Queen of Pentacles", "pentaclesQ.1.png"),
            ("King of Pentacles", "pentaclesK.1.png"),

            # Swords
            ("Ace of Swords", "swords1.1.png"),
            ("Two of Swords", "swords2.1.png"),
            ("Three of Swords", "swords3.1.png"),
            ("Four of Swords", "swords4.1.png"),
            ("Five of Swords", "swords5.1.png"),
            ("Six of Swords", "swords6.1.png"),
            ("Seven of Swords", "swords7.1.png"),
            ("Eight of Swords", "swords8.1.png"),
            ("Nine of Swords", "swords9.1.png"),
            ("Ten of Swords", "swords10.1.png"),
            ("Page of Swords", "swordsP.1.png"),
            ("Knight of Swords", "swordsKn.1.png"),
            ("Queen of Swords", "swordsQ.1.png"),
            ("King of Swords", "swordsK.1.png"),

            # Wands
            ("Ace of Wands", "wands1.1.png"),
            ("Two of Wands", "wands2.1.png"),
            ("Three of Wands", "wands3.1.png"),
            ("Four of Wands", "wands4.1.png"),
            ("Five of Wands", "wands5.1.png"),
            ("Six of Wands", "wands6.1.png"),
            ("Seven of Wands", "wands7.1.png"),
            ("Eight of Wands", "wands8.1.png"),
            ("Nine of Wands", "wands9.1.png"),
            ("Ten of Wands", "wands10.1.png"),
            ("Page of Wands", "wandsP.1.png"),
            ("Knight of Wands", "wandsKn.1.png"),
            ("Queen of Wands", "wandsQ.1.png"),
            ("King of Wands", "wandsK.1.png")
        ]

    def select_random_card(self) -> Tuple[str, str, str]:
        """Select a random card and determine its orientation."""
        card_name, image_file = random.choice(self.cards)
        orientation = random.choice(["Upright", "Reversed"])
        image_path = os.path.join(self.assets_dir, image_file)
        return card_name, orientation, image_path 