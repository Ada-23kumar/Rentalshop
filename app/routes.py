from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, current_app
from flask_login import login_required, current_user
from app import db
from app.models import Item, Rental, Payment, User
from werkzeug.utils import secure_filename
from datetime import datetime, date
import os

main_bp = Blueprint('main', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@main_bp.route('/')
def index():
    items = Item.query.filter_by(is_available=True).limit(12).all()
    return render_template('index.html', items=items)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Items owned by current user
    owned_items = Item.query.filter_by(owner_id=current_user.id).all()
    
    # Rentals where user is the renter
    rentals_as_renter = Rental.query.filter_by(renter_id=current_user.id).all()
    
    # Rentals for items owned by current user
    owned_item_ids = [item.id for item in owned_items]
    rentals_as_owner = Rental.query.filter(Rental.item_id.in_(owned_item_ids)).all() if owned_item_ids else []
    
    return render_template('dashboard.html', 
                         owned_items=owned_items,
                         rentals_as_renter=rentals_as_renter,
                         rentals_as_owner=rentals_as_owner)

@main_bp.route('/items')
def items():
    category = request.args.get('category', '')
    search = request.args.get('search', '')
    
    query = Item.query.filter_by(is_available=True)
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Item.name.contains(search) | Item.description.contains(search))
    
    items = query.all()
    return render_template('items.html', items=items, category=category, search=search)

@main_bp.route('/items/<int:item_id>')
def item_detail(item_id):
    item = Item.query.get_or_404(item_id)
    return render_template('item_detail.html', item=item)

@main_bp.route('/uploads/<filename>')
def uploaded_file(filename):
    upload_folder = current_app.config['UPLOAD_FOLDER']
    return send_from_directory(upload_folder, filename)

