from flask import Blueprint, jsonify
from datetime import datetime

bp = Blueprint('health', __name__)

def register_routes(app):
    app.register_blueprint(bp)

@bp.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'resume-parser-api'
    }), 200
