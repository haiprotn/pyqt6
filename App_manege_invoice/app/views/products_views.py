# products_views.py
from flask import Blueprint, jsonify, request
from App_manege_invoice.create_database import Product

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([product.__dict__ for product in products])

@products_bp.route('/products', methods=['POST'])
def add_product():
    data = request.get_json()
    new_product = Product(name=data['name'], unit=data['unit'], price=data['price'], quantity=data.get('quantity', 0), note=data.get('note', ''))
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'status': 'success'}), 201
