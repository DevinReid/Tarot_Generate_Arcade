import openai
import random
from datetime import datetime
from typing import Tuple, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class ReadingGenerator:
    def __init__(self):
        self.client = openai.Client(api_key=os.getenv('OPENAI_API_KEY'))
        self.major_arcana = [
            "The Fool", "The Magician", "The High Priestess", "The Empress", "The Emperor",
            "The Hierophant", "The Lovers", "The Chariot", "Strength", "The Hermit",
            "Wheel of Fortune", "Justice", "The Hanged Man", "Death", "Temperance",
            "The Devil", "The Tower", "The Star", "The Moon", "The Sun",
            "Judgement", "The World"
        ]
        self.minor_arcana = {
            "Cups": [f"{i} of Cups" for i in range(1, 11)] + ["Page of Cups", "Knight of Cups", "Queen of Cups", "King of Cups"],
            "Wands": [f"{i} of Wands" for i in range(1, 11)] + ["Page of Wands", "Knight of Wands", "Queen of Wands", "King of Wands"],
            "Swords": [f"{i} of Swords" for i in range(1, 11)] + ["Page of Swords", "Knight of Swords", "Queen of Swords", "King of Swords"],
            "Pentacles": [f"{i} of Pentacles" for i in range(1, 11)] + ["Page of Pentacles", "Knight of Pentacles", "Queen of Pentacles", "King of Pentacles"]
        }

    def draw_card(self) -> Tuple[str, str]:
        """Draw a random card and determine if it's upright or reversed."""
        # 50% chance of major arcana
        if random.random() < 0.5:
            card = random.choice(self.major_arcana)
        else:
            suit = random.choice(list(self.minor_arcana.keys()))
            card = random.choice(self.minor_arcana[suit])
        
        position = "Upright" if random.random() < 0.5 else "Reversed"
        return card, position

    def generate_reading(self, card: str, position: str) -> str:
        """Generate a reading for the drawn card using OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a mystical tarot reader who provides daily guidance.
                        Your readings should be concise, poetic, and insightful.
                        Focus on the card's meaning in the given position (upright or reversed).
                        Keep the reading to 2-3 sentences maximum.
                        Make it feel personal and relevant to daily life."""
                    },
                    {
                        "role": "user",
                        "content": f"Generate a daily reading for {card} in the {position} position."
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating reading: {e}")
            return "The cards are silent today. Try again later."

    def get_daily_reading(self) -> Dict[str, str]:
        """Generate a complete daily reading."""
        card, position = self.draw_card()
        reading = self.generate_reading(card, position)
        
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "card": card,
            "position": position,
            "reading": reading
        } 