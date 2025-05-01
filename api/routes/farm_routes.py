"""
Farm API routes for the AgriFinance mobile app.
Provides endpoints for farm registration, management, and monitoring.
"""
from flask import Blueprint, request, jsonify
import logging
from datetime import datetime

from api.models import Farm, CropType, Farmer
from api import db

# Configure logging
logger = logging.getLogger('agrifinance_api.farm')

# Create blueprint
farm_api = Blueprint('farm_api', __name__)

@farm_api.route('/', methods=['GET'])
def get_farms():
    """Get all farms or filter by query parameters"""
    try:
        # Support filtering by various parameters
        farmer_id = request.args.get('farmer_id', type=int)
        crop_type = request.args.get('crop_type')
        location = request.args.get('location')
        
        query = db.session.query(Farm)
        
        if farmer_id:
            query = query.filter(Farm.farmer_id == farmer_id)
        
        if crop_type:
            try:
                crop_type_enum = CropType(crop_type)
                query = query.filter(
                    (Farm.primary_crop == crop_type_enum) | 
                    (Farm.secondary_crop == crop_type_enum)
                )
            except ValueError:
                return jsonify({"error": f"Invalid crop type: {crop_type}"}), 400
        
        if location:
            query = query.filter(Farm.location.like(f"%{location}%"))
        
        farms = query.all()
        return jsonify([farm.to_dict() for farm in farms])
        
    except Exception as e:
        logger.error(f"Error getting farms: {str(e)}")
        return jsonify({"error": str(e)}), 500

@farm_api.route('/<int:farm_id>', methods=['GET'])
def get_farm(farm_id):
    """Get a specific farm by ID"""
    try:
        farm = db.session.get(Farm, farm_id)
        if not farm:
            return jsonify({"error": "Farm not found"}), 404
            
        return jsonify(farm.to_dict())
        
    except Exception as e:
        logger.error(f"Error getting farm {farm_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@farm_api.route('/', methods=['POST'])
def create_farm():
    """Create a new farm"""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['farmer_id', 'name', 'size_hectares', 'primary_crop', 'location']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Check if farmer exists
        farmer = db.session.get(Farmer, data['farmer_id'])
        if not farmer:
            return jsonify({"error": f"Farmer with ID {data['farmer_id']} not found"}), 404
        
        # Parse crop types
        try:
            primary_crop = CropType(data['primary_crop'])
        except ValueError:
            return jsonify({"error": f"Invalid primary crop type: {data['primary_crop']}"}), 400
        
        secondary_crop = None
        if 'secondary_crop' in data and data['secondary_crop']:
            try:
                secondary_crop = CropType(data['secondary_crop'])
            except ValueError:
                return jsonify({"error": f"Invalid secondary crop type: {data['secondary_crop']}"}), 400
        
        # Create new farm
        farm = Farm(
            farmer_id=data['farmer_id'],
            name=data['name'],
            size_hectares=data['size_hectares'],
            primary_crop=primary_crop,
            secondary_crop=secondary_crop,
            location=data['location'],
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            registration_date=datetime.utcnow(),
            last_ndvi_value=data.get('last_ndvi_value'),
            last_ndvi_date=datetime.utcnow() if data.get('last_ndvi_value') else None
        )
        
        db.session.add(farm)
        db.session.commit()
        
        return jsonify(farm.to_dict()), 201
        
    except Exception as e:
        logger.error(f"Error creating farm: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@farm_api.route('/<int:farm_id>', methods=['PUT'])
def update_farm(farm_id):
    """Update an existing farm"""
    try:
        farm = db.session.get(Farm, farm_id)
        if not farm:
            return jsonify({"error": "Farm not found"}), 404
            
        data = request.json
        
        # Update fields if provided
        if 'name' in data:
            farm.name = data['name']
            
        if 'size_hectares' in data:
            farm.size_hectares = data['size_hectares']
            
        if 'primary_crop' in data:
            try:
                farm.primary_crop = CropType(data['primary_crop'])
            except ValueError:
                return jsonify({"error": f"Invalid primary crop type: {data['primary_crop']}"}), 400
                
        if 'secondary_crop' in data:
            if data['secondary_crop']:
                try:
                    farm.secondary_crop = CropType(data['secondary_crop'])
                except ValueError:
                    return jsonify({"error": f"Invalid secondary crop type: {data['secondary_crop']}"}), 400
            else:
                farm.secondary_crop = None
                
        if 'location' in data:
            farm.location = data['location']
            
        if 'latitude' in data:
            farm.latitude = data['latitude']
            
        if 'longitude' in data:
            farm.longitude = data['longitude']
            
        if 'last_ndvi_value' in data:
            farm.last_ndvi_value = data['last_ndvi_value']
            farm.last_ndvi_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(farm.to_dict())
        
    except Exception as e:
        logger.error(f"Error updating farm {farm_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@farm_api.route('/<int:farm_id>', methods=['DELETE'])
def delete_farm(farm_id):
    """Delete a farm"""
    try:
        farm = db.session.get(Farm, farm_id)
        if not farm:
            return jsonify({"error": "Farm not found"}), 404
            
        db.session.delete(farm)
        db.session.commit()
        
        return jsonify({"message": f"Farm {farm_id} deleted successfully"})
        
    except Exception as e:
        logger.error(f"Error deleting farm {farm_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@farm_api.route('/<int:farm_id>/update-ndvi', methods=['POST'])
def update_farm_ndvi(farm_id):
    """Update NDVI data for a farm"""
    try:
        farm = db.session.get(Farm, farm_id)
        if not farm:
            return jsonify({"error": "Farm not found"}), 404
            
        data = request.json
        
        if 'ndvi_value' not in data:
            return jsonify({"error": "Missing required field: ndvi_value"}), 400
            
        farm.last_ndvi_value = data['ndvi_value']
        farm.last_ndvi_date = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            "farm_id": farm.id,
            "ndvi_value": farm.last_ndvi_value,
            "ndvi_date": farm.last_ndvi_date.isoformat() if farm.last_ndvi_date else None,
            "health_status": farm._calculate_health_status()
        })
        
    except Exception as e:
        logger.error(f"Error updating NDVI for farm {farm_id}: {str(e)}")
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@farm_api.route('/farmer/<int:farmer_id>/summary', methods=['GET'])
def get_farmer_farms_summary(farmer_id):
    """Get a summary of all farms for a farmer"""
    try:
        # Check if farmer exists
        farmer = db.session.get(Farmer, farmer_id)
        if not farmer:
            return jsonify({"error": f"Farmer with ID {farmer_id} not found"}), 404
            
        farms = db.session.query(Farm).filter(Farm.farmer_id == farmer_id).all()
        
        # Calculate summary statistics
        total_farms = len(farms)
        total_area = sum(farm.size_hectares for farm in farms)
        
        # Count crops
        crop_counts = {}
        for farm in farms:
            primary = farm.primary_crop.value
            crop_counts[primary] = crop_counts.get(primary, 0) + 1
            
            if farm.secondary_crop:
                secondary = farm.secondary_crop.value
                crop_counts[secondary] = crop_counts.get(secondary, 0) + 1
        
        # Calculate average NDVI if available
        farms_with_ndvi = [farm for farm in farms if farm.last_ndvi_value is not None]
        avg_ndvi = sum(farm.last_ndvi_value for farm in farms_with_ndvi) / len(farms_with_ndvi) if farms_with_ndvi else None
        
        # Get health status distribution
        health_status = {}
        for farm in farms_with_ndvi:
            status = farm._calculate_health_status()
            health_status[status] = health_status.get(status, 0) + 1
        
        return jsonify({
            "farmer_id": farmer_id,
            "total_farms": total_farms,
            "total_area_hectares": total_area,
            "crops": [{"name": crop, "count": count} for crop, count in crop_counts.items()],
            "average_ndvi": avg_ndvi,
            "health_status_distribution": [{"status": status, "count": count} for status, count in health_status.items()],
            "farms": [farm.to_dict() for farm in farms]
        })
        
    except Exception as e:
        logger.error(f"Error getting farms summary for farmer {farmer_id}: {str(e)}")
        return jsonify({"error": str(e)}), 500
