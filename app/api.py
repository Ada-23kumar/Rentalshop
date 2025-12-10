from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Item, Rental, Payment, User
from werkzeug.utils import secure_filename
from datetime import datetime, date
import os

api_bp = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Item APIs
@api_bp.route('/items', methods=['GET'])
def get_items():
    """Get all available items with optional filters"""
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    owner_id = request.args.get('owner_id', type=int)
    
    query = Item.query.filter_by(is_available=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Item.name.contains(search) | Item.description.contains(search))
    
    if owner_id:
        query = query.filter_by(owner_id=owner_id)
    
    items = query.all()
    
    return jsonify({
        'items': [{
            'id': item.id,
            'name': item.name,
            'description': item.description,
            'category': item.category,
            'daily_rate': item.daily_rate,
            'image_path': item.image_path,
            'location': item.location,
            'owner_id': item.owner_id,
            'owner_name': item.owner.full_name,
            'created_at': item.created_at.isoformat()
        } for item in items]
    }), 200

@api_bp.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """Get a specific item by ID"""
    item = Item.query.get_or_404(item_id)
    
    return jsonify({
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'category': item.category,
        'daily_rate': item.daily_rate,
        'image_path': item.image_path,
        'location': item.location,
        'is_available': item.is_available,
        'owner_id': item.owner_id,
        'owner_name': item.owner.full_name,
        'owner_email': item.owner.email,
        'owner_phone': item.owner.phone,
        'created_at': item.created_at.isoformat()
    }), 200

@api_bp.route('/items', methods=['POST'])
@login_required
def create_item():
    """Create a new item listing"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image file selected'}), 400
    
    name = request.form.get('name')
    description = request.form.get('description', '')
    category = request.form.get('category')
    daily_rate = request.form.get('daily_rate', type=float)
    location = request.form.get('location', '')
    
    if not name or not category or not daily_rate:
        return jsonify({'error': 'Missing required fields'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
        filename = timestamp + filename
        upload_folder = current_app.config['UPLOAD_FOLDER']
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        item = Item(
            name=name,
            description=description,
            category=category,
            daily_rate=daily_rate,
            location=location,
            image_path=filename,
            owner_id=current_user.id
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({
            'message': 'Item created successfully',
            'item': {
                'id': item.id,
                'name': item.name,
                'category': item.category,
                'daily_rate': item.daily_rate
            }
        }), 201
    
    return jsonify({'error': 'Invalid file type'}), 400

@api_bp.route('/items/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    """Update an item (only by owner)"""
    item = Item.query.get_or_404(item_id)
    
    if item.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if 'name' in data:
        item.name = data['name']
    if 'description' in data:
        item.description = data['description']
    if 'category' in data:
        item.category = data['category']
    if 'daily_rate' in data:
        item.daily_rate = data['daily_rate']
    if 'location' in data:
        item.location = data['location']
    if 'is_available' in data:
        item.is_available = data['is_available']
    
    db.session.commit()
    
    return jsonify({'message': 'Item updated successfully'}), 200

@api_bp.route('/items/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """Delete an item (only by owner)"""
    item = Item.query.get_or_404(item_id)
    
    if item.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Delete image file if exists
    if item.image_path:
        try:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            os.remove(os.path.join(upload_folder, item.image_path))
        except:
            pass
    
    db.session.delete(item)
    db.session.commit()
    
    return jsonify({'message': 'Item deleted successfully'}), 200

# Rental APIs
@api_bp.route('/rentals', methods=['POST'])
@login_required
def create_rental():
    """Create a new rental booking"""
    data = request.get_json()
    
    item_id = data.get('item_id')
    start_date_str = data.get('start_date')
    end_date_str = data.get('end_date')
    
    if not item_id or not start_date_str or not end_date_str:
        return jsonify({'error': 'Missing required fields'}), 400
    
    item = Item.query.get_or_404(item_id)
    
    if item.owner_id == current_user.id:
        return jsonify({'error': 'Cannot rent your own item'}), 400
    
    if not item.is_available:
        return jsonify({'error': 'Item is not available'}), 400
    
    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
    
    if start_date >= end_date:
        return jsonify({'error': 'End date must be after start date'}), 400
    
    if start_date < date.today():
        return jsonify({'error': 'Start date cannot be in the past'}), 400
    
    # Check for overlapping rentals
    overlapping = Rental.query.filter(
        Rental.item_id == item_id,
        Rental.status.in_(['pending', 'confirmed']),
        Rental.start_date <= end_date,
        Rental.end_date >= start_date
    ).first()
    
    if overlapping:
        return jsonify({'error': 'Item is already booked for these dates'}), 400
    
    total_days = (end_date - start_date).days
    total_amount = item.daily_rate * total_days
    
    rental = Rental(
        item_id=item_id,
        renter_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        total_days=total_days,
        total_amount=total_amount,
        status='pending'
    )
    
    db.session.add(rental)
    db.session.commit()
    
    return jsonify({
        'message': 'Rental booking created successfully',
        'rental': {
            'id': rental.id,
            'item_id': rental.item_id,
            'item_name': item.name,
            'start_date': rental.start_date.isoformat(),
            'end_date': rental.end_date.isoformat(),
            'total_days': rental.total_days,
            'total_amount': rental.total_amount,
            'status': rental.status
        }
    }), 201

@api_bp.route('/rentals', methods=['GET'])
@login_required
def get_rentals():
    """Get rentals for current user"""
    role = request.args.get('role', 'renter')  # 'renter' or 'owner'
    
    if role == 'owner':
        # Get items owned by user
        owned_items = Item.query.filter_by(owner_id=current_user.id).all()
        owned_item_ids = [item.id for item in owned_items]
        
        if not owned_item_ids:
            return jsonify({'rentals': []}), 200
        
        rentals = Rental.query.filter(Rental.item_id.in_(owned_item_ids)).all()
    else:
        # Get rentals where user is renter
        rentals = Rental.query.filter_by(renter_id=current_user.id).all()
    
    return jsonify({
        'rentals': [{
            'id': rental.id,
            'item_id': rental.item_id,
            'item_name': rental.item.name,
            'renter_id': rental.renter_id,
            'renter_name': rental.renter.full_name,
            'start_date': rental.start_date.isoformat(),
            'end_date': rental.end_date.isoformat(),
            'total_days': rental.total_days,
            'total_amount': rental.total_amount,
            'status': rental.status,
            'created_at': rental.created_at.isoformat()
        } for rental in rentals]
    }), 200

@api_bp.route('/rentals/<int:rental_id>', methods=['GET'])
@login_required
def get_rental(rental_id):
    """Get a specific rental"""
    rental = Rental.query.get_or_404(rental_id)
    
    # Check authorization
    if rental.renter_id != current_user.id and rental.item.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': rental.id,
        'item_id': rental.item_id,
        'item_name': rental.item.name,
        'item_image': rental.item.image_path,
        'renter_id': rental.renter_id,
        'renter_name': rental.renter.full_name,
        'renter_email': rental.renter.email,
        'owner_id': rental.item.owner_id,
        'owner_name': rental.item.owner.full_name,
        'start_date': rental.start_date.isoformat(),
        'end_date': rental.end_date.isoformat(),
        'total_days': rental.total_days,
        'total_amount': rental.total_amount,
        'status': rental.status,
        'created_at': rental.created_at.isoformat()
    }), 200

@api_bp.route('/rentals/<int:rental_id>/status', methods=['PUT'])
@login_required
def update_rental_status(rental_id):
    """Update rental status (owner can confirm/cancel)"""
    rental = Rental.query.get_or_404(rental_id)
    
    # Only owner can update status
    if rental.item.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    new_status = data.get('status')
    
    if new_status not in ['confirmed', 'cancelled', 'completed']:
        return jsonify({'error': 'Invalid status'}), 400
    
    rental.status = new_status
    db.session.commit()
    
    return jsonify({'message': 'Rental status updated successfully'}), 200

# Payment APIs
@api_bp.route('/payments', methods=['POST'])
@login_required
def create_payment():
    """Create a payment placeholder for a rental"""
    data = request.get_json()
    
    rental_id = data.get('rental_id')
    payment_method = data.get('payment_method', 'card')
    
    if not rental_id:
        return jsonify({'error': 'Missing rental_id'}), 400
    
    rental = Rental.query.get_or_404(rental_id)
    
    # Check authorization
    if rental.renter_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if rental.status != 'pending' and rental.status != 'confirmed':
        return jsonify({'error': 'Cannot process payment for this rental'}), 400
    
    # Check if payment already exists
    if rental.payment:
        return jsonify({'error': 'Payment already exists for this rental'}), 400
    
    # Generate placeholder transaction ID
    transaction_id = f'TXN_{datetime.now().strftime("%Y%m%d%H%M%S")}_{rental_id}'
    
    payment = Payment(
        rental_id=rental_id,
        amount=rental.total_amount,
        payment_method=payment_method,
        transaction_id=transaction_id,
        status='completed'  # Placeholder - auto-complete
    )
    
    db.session.add(payment)
    
    # Update rental status to confirmed
    rental.status = 'confirmed'
    
    db.session.commit()
    
    return jsonify({
        'message': 'Payment processed successfully (placeholder)',
        'payment': {
            'id': payment.id,
            'rental_id': payment.rental_id,
            'amount': payment.amount,
            'payment_method': payment.payment_method,
            'transaction_id': payment.transaction_id,
            'status': payment.status
        }
    }), 201

@api_bp.route('/payments/<int:payment_id>', methods=['GET'])
@login_required
def get_payment(payment_id):
    """Get payment details"""
    payment = Payment.query.get_or_404(payment_id)
    
    # Check authorization
    if payment.rental.renter_id != current_user.id or payment.rental.item.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify({
        'id': payment.id,
        'rental_id': payment.rental_id,
        'amount': payment.amount,
        'payment_method': payment.payment_method,
        'transaction_id': payment.transaction_id,
        'status': payment.status,
        'created_at': payment.created_at.isoformat()
    }), 200

# Dashboard APIs
@api_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """Get dashboard statistics for current user"""
    # Items owned
    owned_items = Item.query.filter_by(owner_id=current_user.id).all()
    
    # Rentals as renter
    rentals_as_renter = Rental.query.filter_by(renter_id=current_user.id).all()
    
    # Rentals as owner
    owned_item_ids = [item.id for item in owned_items]
    rentals_as_owner = Rental.query.filter(Rental.item_id.in_(owned_item_ids)).all() if owned_item_ids else []
    
    # Calculate earnings (completed rentals)
    total_earnings = sum([r.total_amount for r in rentals_as_owner if r.status == 'completed'])
    
    # Calculate spending (completed rentals)
    total_spending = sum([r.total_amount for r in rentals_as_renter if r.status == 'completed'])
    
    return jsonify({
        'owned_items_count': len(owned_items),
        'rentals_as_renter_count': len(rentals_as_renter),
        'rentals_as_owner_count': len(rentals_as_owner),
        'total_earnings': total_earnings,
        'total_spending': total_spending,
        'pending_rentals_as_owner': len([r for r in rentals_as_owner if r.status == 'pending']),
        'pending_rentals_as_renter': len([r for r in rentals_as_renter if r.status == 'pending'])
    }), 200

@api_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get list of available categories"""
    categories = db.session.query(Item.category).distinct().all()
    return jsonify({
        'categories': [cat[0] for cat in categories]
    }), 200

