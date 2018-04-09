from flask import Flask, jsonify, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import *


db_file = 'store.db'
engine = create_engine('sqlite:///{}'.format(db_file), convert_unicode=True)
Session = sessionmaker(bind=engine)
session = Session()

app = Flask(__name__)

@app.teardown_appcontext
def shutdown_session(exception=None):
    '''Clean-up when the the app context is torn down'''
    session.close()

@app.errorhandler(404)
def not_found(error):
    response = jsonify({'code': 404, 'message': 'Not found!'})
    response.status_code = 404
    return response

@app.route('/api/stores', methods=['GET'])
def get_stores():
    '''Return all stores'''
    stores = session.query(Store).all()
    return jsonify([{'id': s.id, 'name': s.name} for s in stores])

@app.route('/api/brands', methods=['GET'])
def get_brands():
    '''Return all brands'''
    brands = session.query(Brand).all()
    return jsonify([{'id': b.id, 'name': b.name} for b in brands])

@app.route('/api/products/<int:brand_id>', methods=['GET'])
@app.route('/api/products/<int:brand_id>/<int:offset>', methods=['GET'])
@app.route('/api/products/<int:brand_id>/<int:offset>/<int:limit>', methods=['GET'])
def get_products_of_brand(brand_id, offset=0, limit=5):
    '''Return all products given a brand'''
    try:
        brand = session.query(Brand).filter(Brand.id == brand_id).first()
    except:
        abort(404)

    return jsonify([
        {'id': p.id, 
        'name': p.name, 
        'store': {
            'id': p.stores.id,
            'name': p.stores.name
        }
    } for p in brand.products[offset:limit]])

@app.route('/api/product/<int:product_id>/<int:store_id>', methods=['GET'])
def get_product_details(product_id, store_id):
    '''Return product information given a product and brand'''
    try:
        product = session.query(Product).filter(Product.id == product_id).filter(Product.store_id == store_id).one()
    except:
        abort(404)

    return jsonify({
        'id': product.id,
        'name': product.name,
        'type': product.type,
        'price': float(product.price),
        'position': product.page_position,
        'page': product.page_number,
        'category': {
            'id': product.categories.id,
            'name': product.categories.name,
        },
        'brand': {
            'id': product.brands.id,
            'name': product.brands.name,
        }
    })

if __name__ == '__main__':
    app.run(debug=True)