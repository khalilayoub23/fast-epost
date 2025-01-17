from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from app.models.package import Package
from app.models.package_history import PackageHistory
from datetime import datetime, timedelta

bp = Blueprint('tracking', __name__)

@bp.route('/monitor', methods=['GET', 'POST'])
@jwt_required()
@limiter.limit("10 per minute")
@cache.cached(timeout=60)
def monitor_packages():
    packages = Package.query.filter_by(status='in_warehouse').all()
    alerts = []
    
    for package in packages:
        time_in_warehouse = datetime.utcnow() - package.timestamp
        
        if time_in_warehouse > timedelta(hours=72):
            alerts.append({
                'package_id': package.id,
                'description': package.description,
                'alert_type': 'critical',
                'message': 'Package exceeded 72 hours in warehouse'
            })
        elif time_in_warehouse > timedelta(hours=60):
            alerts.append({
                'package_id': package.id,
                'description': package.description,
                'alert_type': 'warning',
                'message': 'Package nearing 72-hour limit'
            })
    
    if request.method == 'POST':
        # Handle POST request logic here
        return jsonify({'message': 'POST request received'}), 201

@bp.route('/package/<int:package_id>/history', methods=['GET'])
@jwt_required()
def get_package_history(package_id):
    history = PackageHistory.query.filter_by(package_id=package_id).order_by(PackageHistory.timestamp.desc()).all()
    
    return jsonify({
        'history': [{
            'status': h.status,
            'location': h.location,
            'timestamp': h.timestamp.isoformat(),
            'notes': h.notes
        } for h in history]
    })
