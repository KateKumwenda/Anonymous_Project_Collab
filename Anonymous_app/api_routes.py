# api_routes.py

from flask import Blueprint, request, jsonify
from models.tip import Tip
from utils.encryption import encrypt_data, decrypt_data
from datetime import datetime
from models import db  # make sure db is initialized globally

api = Blueprint('api', __name__)

# Submit a tip
@api.route('/api/tips', methods=['POST'])
def submit_tip_api():
    data = request.get_json()

    required = ['text', 'category']
    if not all(key in data for key in required):
        return jsonify({'error': 'Missing fields'}), 400

    encrypted_text = encrypt_data(data['text'])

    tip = Tip(
        text=encrypted_text,
        category=data.get('category'),
        latitude=data.get('latitude'),
        longitude=data.get('longitude'),
        timestamp=datetime.utcnow()
    )

    db.session.add(tip)
    db.session.commit()

    return jsonify({'message': 'Tip submitted successfully'}), 201


# Get all tips (admin view)
@api.route('/api/tips', methods=['GET'])
def get_all_tips():
    tips = Tip.query.order_by(Tip.timestamp.desc()).all()
    return jsonify([
        {
            'id': tip.id,
            'text': decrypt_data(tip.text),
            'category': tip.category,
            'latitude': tip.latitude,
            'longitude': tip.longitude,
            'timestamp': tip.timestamp.strftime('%Y-%m-%d %H:%M')
        }
        for tip in tips
    ])


# Get single tip by ID
@api.route('/api/tips/<int:tip_id>', methods=['GET'])
def get_tip(tip_id):
    tip = Tip.query.get_or_404(tip_id)
    return jsonify({
        'id': tip.id,
        'text': decrypt_data(tip.text),
        'category': tip.category,
        'latitude': tip.latitude,
        'longitude': tip.longitude,
        'timestamp': tip.timestamp.strftime('%Y-%m-%d %H:%M')
    })


# Optional: Delete tip
@api.route('/api/tips/<int:tip_id>', methods=['DELETE'])
def delete_tip(tip_id):
    tip = Tip.query.get_or_404(tip_id)
    db.session.delete(tip)
    db.session.commit()
    return jsonify({'message': 'Tip deleted'}), 200
