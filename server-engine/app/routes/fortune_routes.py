from flask import Blueprint, jsonify, request, abort
from app.services.fortune_service import FortuneService
from app.utils.logger import log_request, log_error
from app.utils.db import DatabaseManager
from app.config.config import Config
import hashlib
import json

fortune_bp = Blueprint('fortune', __name__)
fortune_service = FortuneService()

def verify_authentication():
    """Verify request authentication."""
    if Config.DEPLOY_MODE == 'dev':
        return True
    
    try:
        secret = Config.SECRET_HASH
        request_token = request.headers.get('Token')
        request_hash = request.headers.get('Hash')

        if not request_token or not request_hash:
            abort(401, "Missing authentication headers")

        hasher = hashlib.sha256()
        hasher.update(f'{request_token}{secret}'.encode('utf-8'))
        secret_hash = hasher.hexdigest()

        if secret_hash != request_hash:
            abort(403, "Invalid authentication")
        
        return True
    except Exception as e:
        log_error(e, {"context": "Authentication failed"})
        abort(403, "Authentication failed")

@fortune_bp.route('/fortune', methods=['POST'])
@log_request
def fortune():
    """Generate a fortune based on cards and intention."""
    verify_authentication()
    
    try:
        data = request.get_json()
        if not data:
            abort(400, "No JSON data provided")

        cards = data.get('cards')
        intention = data.get('intention')

        if not cards or not intention:
            abort(400, "Missing cards or intention")

        if not isinstance(cards, list) or len(cards) != 3:
            abort(400, "Cards must be a list of exactly 3 cards")

        fortune_text, tokens_used = fortune_service.generate_fortune(cards, intention)

        # Log the request
        with DatabaseManager.get_cursor() as cur:
            cur.execute('''
                INSERT INTO user_requests 
                (ip_address, user_agent, request_path, request_method, request_payload, tokens_used)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                request.remote_addr,
                request.headers.get('User-Agent'),
                request.path,
                request.method,
                json.dumps(data),
                tokens_used
            ))

        return jsonify({
            "fortune": fortune_text,
            "tokens_used": tokens_used
        })

    except Exception as e:
        log_error(e, {"context": "Fortune generation failed"})
        abort(500, "Failed to generate fortune")

@fortune_bp.route('/token_status', methods=['GET'])
@log_request
def token_status():
    """Get current token usage status."""
    verify_authentication()
    
    try:
        total_cost = fortune_service.get_token_status()
        return jsonify({"total_cost": total_cost})
    except Exception as e:
        log_error(e, {"context": "Failed to get token status"})
        abort(500, "Failed to get token status")

@fortune_bp.route('/reset_tokens', methods=['POST'])
@log_request
def reset_tokens():
    """Reset token tracking."""
    verify_authentication()
    
    try:
        fortune_service.reset_token_tracking()
        return jsonify({"message": "Token tracking reset successfully"})
    except Exception as e:
        log_error(e, {"context": "Failed to reset token tracking"})
        abort(500, "Failed to reset token tracking")

@fortune_bp.route("/health", methods=["GET"])
@log_request
def health():
    """Health check endpoint."""
    return jsonify({"status": "OK"}) 