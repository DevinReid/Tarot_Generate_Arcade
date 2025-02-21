import requests
import secrets
import hashlib

from text_utility import wrap_text_paragraphs
from compiled_details import RELEVANT_HASH

debug_mode = False

def has_internet_connection():
    try:
        response = requests.get("https://health.aws.amazon.com/health/status", timeout=3)
        if debug_mode:
            print("Internet: Connected")
        return response.status_code == 200
    except requests.exceptions.RequestException:
        if debug_mode:
            print("Internet: Not Connected")
        return False

def has_server_connection():
    try:
        response = requests.get("https://tarot-generate-arcade.onrender.com/health", timeout=6)
        if debug_mode:
            print("Server: Connected")
        return response.status_code == 200
    except:
        if debug_mode:
            print("Server: NOT Connected")
        return False



def generate_auth_headers():
    """
    Generates Token and Hash headers for secure API request.
    """
    token = secrets.token_urlsafe(16)
    secret_hash = RELEVANT_HASH

    hasher = hashlib.sha256()
    hasher.update(f"{token}{secret_hash}".encode('utf-8'))
    request_hash = hasher.hexdigest()

    return {
        "Token": token,
        "Hash": request_hash,
        "Content-Type": "application/json"
}
    
def get_fortune(game, cards, intention):
    """Send cards and intention to the Flask server to get a fortune"""
    game.check_connectivity()
    headers = generate_auth_headers()
    card_names = [card.name for card in cards]
    if game.internet_connected and game.server_connected:
        game.connection_popup_open = False
        try:
            response = requests.post(
                f"{game.request_url}fortune",
                headers=headers,
                json={"cards": card_names, "intention": intention}
            )

            if response.status_code == 200:
                data = response.json()
                game.fortune = data['fortune']

                if debug_mode:# # Optional: If you want to display token usage in the console
                    print(f"Tokens Used: {data['tokens_used']}")

            else:
                # Handle the error if the server returns an error response
                game.fortune = f"Error: {response.status_code} - {response.text}"

        except Exception as e:
            # Handle network errors or other unexpected exceptions
            game.fortune = f"API Call Failed: {str(e)}"
            if debug_mode:

                print(game.fortune)
    else:
        game.connection_popup_open = True
    # Let the game know the API call is done, even if it failed
    game.api_call_complete = True

    # Wrap paragraphs if a valid fortune is returned
    game.fortune = wrap_text_paragraphs(game.fortune)


