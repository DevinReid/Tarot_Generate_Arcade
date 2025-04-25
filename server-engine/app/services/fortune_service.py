import openai
from app.config.config import Config
from app.utils.logger import log_info, log_error
from app.utils.db import DatabaseManager

class FortuneService:
    def __init__(self):
        self.openai_client = openai.Client(api_key=Config.OPENAI_API_KEY)
        self.input_rate = 0.15 / 1000000
        self.cached_input_rate = 0.075 / 1000000
        self.output_rate = 0.6 / 1000000

    def generate_fortune(self, cards, intention):
        """Generate a fortune using OpenAI API."""
        try:
            response = self.openai_client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": """
                            You are a voodoo practicing witch in New Orleans who provides customers fortunes using a traditional tarot card deck.
                            The customer will tell you what type of information they are seeking and will set an intention with you. 
                            They will then pull three tarot cards, one representing the past, one the present, and the last the message of the future.
                            You will provide back a concise, spooky, and extreme fortune using a bayou witch accent.
                            You will break down each card reading into separate 3-4 sentence paragraphs, and add a final paragraph summarizing the reading and how the cards relate to each other.
                            Generate the fortune as plain paragraphs with no titles or headers, there should only be four line breaks.
                            There will be 5 Paragraphs.
                            Paragraph 1 should be a 2-sentence introduction or overview, ideally mentioning the intention.
                            Paragraph 2-4 should be the readings for each card.
                            Paragraph 5 should be the summarization of the reading and should be no more than 360 characters long.
                        """
                    },
                    {
                        "role": "user",
                        "content": f"My intention is {intention} and the three cards I drew were {cards[0]}, {cards[1]}, and {cards[2]}."
                    }
                ],
            )

            fortune_text = response.choices[0].message.content
            self._calculate_and_log_costs(response.usage)
            
            return fortune_text, response.usage.total_tokens

        except Exception as e:
            log_error(e, {"context": "Failed to generate fortune"})
            raise

    def _calculate_and_log_costs(self, usage):
        """Calculate and log token costs."""
        try:
            cached_tokens = usage.prompt_tokens_details.cached_tokens if hasattr(usage, 'prompt_tokens_details') else 0
            input_cost = (usage.prompt_tokens - cached_tokens) * self.input_rate
            cached_input_cost = cached_tokens * self.cached_input_rate
            output_cost = usage.completion_tokens * self.output_rate
            total_cost = cached_input_cost + input_cost + output_cost

            log_info("Token Usage", {
                "prompt_tokens": usage.prompt_tokens,
                "cached_tokens": cached_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens,
                "total_cost": total_cost
            })

            self._update_token_tracking(total_cost)

        except Exception as e:
            log_error(e, {"context": "Failed to calculate token costs"})
            raise

    def _update_token_tracking(self, cost):
        """Update token tracking in database."""
        try:
            with DatabaseManager.get_cursor() as cur:
                cur.execute("""
                    UPDATE token_tracking
                    SET request_count = request_count + 1,
                        total_cost = total_cost + %s
                    WHERE id = 1;
                """, (cost,))
        except Exception as e:
            log_error(e, {"context": "Failed to update token tracking"})
            raise

    def get_token_status(self):
        """Get current token usage status."""
        try:
            with DatabaseManager.get_cursor() as cur:
                cur.execute("SELECT total_cost FROM token_tracking WHERE id = 1;")
                total_cost = cur.fetchone()[0]
                return float(total_cost)
        except Exception as e:
            log_error(e, {"context": "Failed to get token status"})
            raise

    def reset_token_tracking(self):
        """Reset token tracking in database."""
        try:
            with DatabaseManager.get_cursor() as cur:
                cur.execute("""
                    UPDATE token_tracking
                    SET total_cost = 0
                    WHERE id = 1;
                """)
        except Exception as e:
            log_error(e, {"context": "Failed to reset token tracking"})
            raise 