import os
from flask import Flask
from flask import request
from flask import send_file
from tinydb import TinyDB, Query
from tinydb.table import Document

import json
import requests

app = Flask(__name__)

APP_PATH = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.environ.get('DB_PATH', os.path.join(APP_PATH, 'db.json'))

db = TinyDB(DB_PATH)

customers_table = db.table('customers')
products_table = db.table('products')
orders_table = db.table('orders')

def extend_order(order):
    """
    Fetch related data for an order to a new dict
    """
    extended_order = dict(**order)
    extended_order['customer'] = customers_table.get(doc_id=order['customer'])
    extended_order['product'] = products_table.get(doc_id=order['product'])
    extended_order['id'] = order.doc_id
    return extended_order


def get_orders(include_processed=False):
    """
    Returns the list of unprocessed orders with extended data, processed can be
    added via a param
    """
    Order = Query()
    orders = db.table('orders').all() if include_processed else db.table('orders').search(~(Order.processed.exists()) | (Order.processed != True))
    return list(map(extend_order, orders))


@app.route('/', methods=['GET'])
def index():
    """
    Serve the webapp at index.html
    """
    return send_file('static/index.html')


@app.route('/orders/', methods=['GET'])
def order_list():
    """
    API endpoint with returning the list of orders (unprocessed)
    """
    return (json.dumps(get_orders()), 200)


@app.route('/products/', methods=['GET'])
def product_list():
    """
    API endpoint with returning the list of products and their details
    """
    return (json.dumps(products_table.all()), 200)


@app.route('/orders/receive_order/', methods=['POST'])
def inventory_item_receive_order():
    """
    API endpoint which receives an order from a customer and registers that for
    later processing
    """
    Product = Query()
    Customer = Query()
    try:
        product = request.form['product']
        customer = int(request.form['customer'])
        quantity = int(request.form['quantity'])
    except KeyError:
        return ({'error': 'INVALID_PARAMETERS'}, 400)

    product = products_table.get(Product.id == product)
    if not product:
        return ({'error': 'INVALID_PRODUCT'}, 400)
    customer = customers_table.get(doc_id=customer)

    if not customer:
        return ({'error': 'INVALID_CUSTOMER'}, 400)

    order_id = db.table('orders').insert({
        "product": product.doc_id,
        "customer": customer.doc_id,
        "quantity": quantity,
        "processed": False,
    })

    ret = db.table('orders').get(doc_id=order_id)
    ret['id'] = order_id

    return ret

@app.route('/orders/<int:order_id>/deliver_order/', methods=['POST'])
def inventory_item_deliver_order(order_id):
    """
    API endpoint which contacts the customer to send a delivery and update the
    warehouse stock.
    """
    order = db.table('orders').get(doc_id=order_id)
    if order is None:
        return {'detail': 'Not found'}, 404

    order = extend_order(order)

    if order.get('processed', False) is True:
        return {'error': 'ALREADY_PROCESSED'}, 400

    response = requests.post('{}/inventory/{}/receive_delivery/'.format(
        order['customer']['base_url'],
        order['product']['id']),
        {'quantity': order['quantity']}
    )
    if response.ok:
        db.table('orders').update({'processed': True}, doc_ids=[order_id])
        products_table.update({'stock': order['product']['stock'] - order['quantity']}, doc_ids=[order['product'].doc_id])
        return '', 204
    else:
        return {'detail': 'DELIVER_ERROR'}, 400