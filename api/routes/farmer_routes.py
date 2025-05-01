"""
Farmer API routes for the AgriFinance mobile app.
Provides endpoints for farmer registration, profile management, and data access.
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

from api.models import Farmer, FarmerType
from api import db

# Configure logging
logger = logging.getLogger('agrifinance_api.farmer')

# Create blueprint
farmer_api = Blueprint('farmer_api', __name__)

@farmer_api.route('/', methods=['GET'])
def get_farmers():
    """Get all farmers or filter by query parameters"""
    try:
        # Support filtering by various parameters
        farmer_type = request.args.get('type')
        location = request.args.get('location')
        
        query = db.session.query(Farmer)
        
        if farmer_type:
            try:
                farmer_type_enum = FarmerType(farmer_type)
                query = query.filter(Farmer.farmer_type == farmer_type_enum)
            except ValueError:
                return jsonify({"error": f"Invalid farmer type: {farmer_type}"}), 400
        
        if location:
            query = query.filter(Farmer.location.like(f"%{location}%"))
        
        farmers = query.all()
        return jsonify([farmer.to_dict() for farmer in farmers])
        
    except Exception as e:
        logger.error(f"Error getting farmers: {str(e)}")
        return jsonify({"error": str(e)}), 500

@farmer_api.route('/<int:farmer_id>', methods=['GET'])
def get_farmer(farmer_id):
    """Get a specific farmer by ID"""
    try:
        farmer = db.session.get(Farmer, farmer_id)
        if not farmer:
            return jsonify({"error": "Farmer not found"}), 404
            
        return jsonify(farmer.to_dict())
        
    except Exception as e:
        logger.error(f"Error getting farmer {farmer_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@farmer_api.route('/', methods=['POST'])
def create_farmer():
    """Create a new farmer"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'phone_number', 'location']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check for existing farmer with same phone number
        existing_farmer = db.session.query(Farmer).filter(
            Farmer.phone_number == data['phone_number']
        ).first()
        
        if existing_farmer:
            return jsonify({"error": "A farmer with this phone number already exists"}), 409
        
        # Parse farmer type
        farmer_type = FarmerType.INDIVIDUAL
        if 'farmer_type' in data:
            try:
                farmer_type = FarmerType(data['farmer_type'])
            except ValueError:
                return jsonify({"error": f"Invalid farmer type: {data['farmer_type']}"}), 400
        
        # Create new farmer
        farmer = Farmer(
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=data['phone_number'],
            location=data['location'],
            farmer_type=farmer_type,
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            registration_date=datetime.utcnow()
        )
        
        db.session.add(farmer)
        db.session.commit()
        
        return jsonify(farmer.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating farmer: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@farmer_api.route('/<int:farmer_id>', methods=['PUT'])
def update_farmer(farmer_id):
    """Update an existing farmer"""
    try:
        farmer = db.session.get(Farmer, farmer_id)
        if not farmer:
            return jsonify({"error": "Farmer not found"}), 404
            
        data = request.json
        
        # Update fields if provided
        if 'first_name' in data:
            farmer.first_name = data['first_name']
            
        if 'last_name' in data:
            farmer.last_name = data['last_name']
            
        if 'phone_number' in data:
            # Check if phone number already exists for another farmer
            existing_farmer = db.session.query(Farmer).filter(
                Farmer.phone_number == data['phone_number'],
                Farmer.id != farmer_id
            ).first()
            
            if existing_farmer:
                return jsonify({"error": "A different farmer with this phone number already exists"}), 409
                
            farmer.phone_number = data['phone_number']
            
        if 'location' in data:
            farmer.location = data['location']
            
        if 'farmer_type' in data:
            try:
                farmer.farmer_type = FarmerType(data['farmer_type'])
            except ValueError:
                return jsonify({"error": f"Invalid farmer type: {data['farmer_type']}"}), 400
                
        if 'latitude' in data:
            farmer.latitude = data['latitude']
            
        if 'longitude' in data:
            farmer.longitude = data['longitude']
        
        db.session.commit()
        
        return jsonify(farmer.to_dict())
        
    except Exception as e:
        logger.error(f"Error updating farmer {farmer_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@farmer_api.route('/<int:farmer_id>', methods=['DELETE'])
def delete_farmer(farmer_id):
    """Delete a farmer"""
    try:
        farmer = db.session.get(Farmer, farmer_id)
        if not farmer:
            return jsonify({"error": "Farmer not found"}), 404
            
        db.session.delete(farmer)
        db.session.commit()
        
        return jsonify({"message": f"Farmer {farmer_id} deleted successfully"})
        
    except Exception as e:
        logger.error(f"Error deleting farmer {farmer_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@farmer_api.route('/search', methods=['GET'])
def search_farmers():
    """Search for farmers by name or phone number"""
    try:
        query = request.args.get('q')
        if not query:
            return jsonify({"error": "Search query is required"}), 400
            
        # Search by name or phone number
        farmers = db.session.query(Farmer).filter(
            (Farmer.first_name.like(f"%{query}%")) |
            (Farmer.last_name.like(f"%{query}%")) |
            (Farmer.phone_number.like(f"%{query}%"))
        ).all()
        
        return jsonify([farmer.to_dict() for farmer in farmers])
        
    except Exception as e:
        logger.error(f"Error searching farmers: {str(e)}")
        return jsonify({"error": str(e)}), 500
