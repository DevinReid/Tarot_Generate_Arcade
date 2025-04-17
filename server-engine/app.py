import os
from flask import Flask, jsonify, request, json, abort
from verify_request import verify_input 
import hashlib
import psycopg2
from dotenv import load_dotenv
import openai
import json

app = Flask(__name__)

load_dotenv() 

def verify_authentication():
    mode = os.environ.get('DEPLOY_MODE')
    print(f"DEPLOY_MODE is: {mode}")

    if mode == 'dev':
        return True
    
    try: 
        print("not in dev mode!")
        secret = os.environ.get('SECRET_HASH')

        request_token = request.headers['Token']
        request_hash =  request.headers['Hash']

        hasher = hashlib.sha256()
        hasher.update(f'{request_token}{secret}'.encode('utf-8'))
        secret_hash = hasher.hexdigest()


        if secret_hash != request_hash:
            abort(403)
        else:
            print(("YOUR IN!"))
            return True
    except: 
        abort(403)

def get_db_connection():
    DB_CONNECTION_URL = os.environ.get('DB_CONNECTION_URL')
    conn = psycopg2.connect(DB_CONNECTION_URL)
    return conn

@app.route('/fortune', methods=['POST'])
def fortune():
    
    verify_authentication()

    data = request.get_json()
    cards = data.get('cards')
    intention = data.get('intention')

    if not cards or not intention:
        abort(400, "Missing cards or intention.")

    if not verify_input(cards, intention):
        abort(422, "Parameters are not valid")

    try:
        # === 1. CALL OPENAI API ===
        openai_client = openai.Client(api_key=os.getenv('OPENAI_API_KEY'))
        resp = openai_client.chat.completions.create(
            model="gpt-4o-mini",
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

        fortune_text = resp.choices[0].message.content

        # === 2. TOKEN USAGE DATA ===
        input_rate = 0.15 / 1000000
        cached_input_rate = 0.075 / 1000000
        output_rate = 0.6 / 1000000

        cached_tokens = resp.usage.prompt_tokens_details.cached_tokens if hasattr(resp.usage, 'prompt_tokens_details') else 0
        input_cost = (resp.usage.prompt_tokens - cached_tokens) * input_rate
        cached_input_cost = cached_tokens * cached_input_rate
        output_cost = resp.usage.completion_tokens * output_rate
        total_cost = cached_input_cost + input_cost + output_cost

        update_token_tracking(total_cost)

        # === SERVER TERMINAL LOGGING ===
        print("\n🔮 Token Usage for This Reading:")
        print(f"Prompt tokens: {resp.usage.prompt_tokens}")
        print(f"Cached Prompt tokens: {cached_tokens}")
        print(f"Completion tokens: {resp.usage.completion_tokens}")
        print(f"Total tokens: {resp.usage.total_tokens}")
        print(f"💰 Token Costs: ${total_cost:.6f}")

        # === 3. UPDATE USER REQUEST LOG ===
        log_user_request(
            ip=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            path=request.path,
            method=request.method,
            payload={'cards': cards, 'intention': intention},
            tokens_used=resp.usage.total_tokens,
            cost=total_cost
        )


        # === RETURN DATA TO GAME ===
        return jsonify({
            "fortune": fortune_text,
            "tokens_used": resp.usage.total_tokens,
            "cost": total_cost
        })

    except Exception as e:
        print(f"OpenAI API Call Failed: {e}")
        return jsonify({"error": f"OpenAI API Call Failed: {str(e)}"}), 50
    
def update_token_tracking(cost):
    """Increment request_count and add cost to total_cost in token_tracking table."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("""
            UPDATE token_tracking
            SET request_count = request_count + 1,
                total_cost = total_cost + %s
            WHERE id = 1;
        """, (cost,))

        conn.commit()
        cur.close()
        conn.close()

        print(f"✅ Updated token_tracking table: +1 request, +${cost:.6f}")

    except Exception as e:
        print(f"❌ Database update failed: {e}")


def log_user_request(ip, user_agent, path, method, payload, tokens_used, cost):
    """
    Inserts a new user request record into the user_requests table.

    Args:
        ip (str): IP address of the user.
        user_agent (str): User-Agent string.
        path (str): Request path (e.g., "/fortune").
        method (str): HTTP method (e.g., "POST").
        payload (dict): JSON payload from the request.
        tokens_used (int): Number of tokens used in the API call.
        cost (float): Cost of the API call in dollars.
    """
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''
            INSERT INTO user_requests (ip_address, user_agent, request_path, request_method, request_payload, tokens_used, request_cost)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (
            ip,
            user_agent,
            path,
            method,
            json.dumps(payload),  # Store the payload as a JSON string
            tokens_used,
            cost
        ))

        conn.commit()
        cur.close()
        conn.close()

        print(f"✅ Logged user request: {ip}, {tokens_used} tokens, ${cost:.6f}")

    except Exception as e:
        print(f"❌ Failed to log user request: {e}")



@app.route('/reset_tokens')
def reset_tokens():
    verify_authentication()
    conn = get_db_connection()
    cur = conn.cursor()
    query = """
        UPDATE token_tracking
        SET total_cost = 0
        WHERE id = 1; 
    """
    cur.execute(query)
    conn.commit()
    cur.close()
    conn.close()
    return "This endpoint will reset the monthly token count", 200

@app.route('/token_status', methods=['GET'])
def token_status():
    """
    Return the current total_cost from the token_tracking table.
    """
    verify_authentication() 

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute("SELECT total_cost FROM token_tracking WHERE id = 1;")
        total_cost = cur.fetchone()[0]

        cur.close()
        conn.close()

        return jsonify({"total_cost": float(total_cost)}), 200

    except Exception as e:
        print(f"❌ Failed to fetch token status: {e}")
        return jsonify({"error": "Failed to retrieve token status"}), 500
    
@app.route("/")
def hello_world():
    print(request.remote_addr)
    return "<p>Hello, World!</p>"

@app.route("/health", methods=["GET"])
def health():    
    return "OK", 200