import openai
from typing import Tuple
import os
from dotenv import load_dotenv

load_dotenv()

class ReadingGenerator:
    def __init__(self):
        self.openai_client = openai.Client(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4-turbo-preview"  # Using the same model as fortune_service

    def generate_daily_reading(self, card_name: str, card_orientation: str) -> Tuple[str, int]:
        """Generate a daily tarot reading using OpenAI API."""
        try:
            response = self.openai_client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """
                            You are Mama Nyah, a voodoo practicing witch in New Orleans who provides daily tarot readings.
                            Avoid "Child", "Chile", or "Chil'" in your reading.
                            Your readings should be concise, spooky, and use a bayou witch accent.
                            Keep the reading to 2-3 short paragraphs, with each paragraph being 2-3 sentences maximum.
                            The total reading should be no more than 400 characters.
                            Focus on the daily message and guidance from the card.
                    
                            End with a brief blessing or warning.
                        """
                    },
                    {
                        "role": "user",
                        "content": f"Today's card is the {card_name} in the {card_orientation} position. What message does this card hold for today?"
                    }
                ],
            )

            reading_text = response.choices[0].message.content
            return reading_text, response.usage.total_tokens

        except Exception as e:
            print(f"Error generating reading: {e}")
            raise

    def generate_placeholder_reading(self) -> str:
        """Generate a placeholder reading for testing."""
        return """The spirits whisper of change in the air, child. 
Your path is clear, but the road may twist.
Trust in the cards, they never lie.
Mama Nyah sees blessings coming your way.""" 