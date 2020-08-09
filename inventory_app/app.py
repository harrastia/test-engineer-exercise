import os
import sys
from flask import Flask
from flask import request
from flask import send_file
from tinydb import TinyDB, Query
import requests
import json

app = Flask(__name__)

APP_PATH = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.environ.get('DB_PATH', os.path.join(APP_PATH, 'db.json'))
CUSTOMER_ID = os.environ['CUSTOMER_ID']

db = TinyDB(DB_PATH)
items_table = db.table('items')
Item = Query()

@app.route('/', methods=['GET'])
def index():
    """
    Serve the index.html at the root
    """
    return send_file('static/index.html')

@app.route('/merchant-name/', methods=['GET'])
def merchant_name():
    """
    Get the merchant name
    """
    return os.environ.get('MERCHANT_NAME')

@app.route('/inventory/', methods=['GET'])
def inventory_list():
    """
    Get the list of products and their details
    """
    return (json.dumps(items_table.all()), 200)

@app.route('/inventory/<string:item_id>/order/', methods=['POST'])
def inventory_item_order(item_id):
    """
    Place an order to the provider
    """
    try:
        quantity = int(request.form['quantity'])
    except KeyError:
        return ({'error': 'INVALID_PARAMETERS'}, 400)

    it = items_table.get(Item.id == item_id)

    response = requests.post('http://provider_app:5000/orders/receive_order/',{
        'customer': CUSTOMER_ID,
        'product': item_id,
        'quantity': quantity,
    })
    if response.ok:
        items_table.update({'ordered': it.get('ordered', 0) + quantity}, doc_ids=[it.doc_id])
        return items_table.get(Item.id == item_id), 201
    else:
        return {'error': 'ERROR_PLACING_ORDER', 'response': response.text}, 400


@app.route('/inventory/<string:item_id>/receive_delivery/', methods=['POST'])
def inventory_item_receive_delivery(item_id):
    """
    Recive a delivery from the provider
    """
    try:
        quantity = int(request.form['quantity'])
    except KeyError:
        return ({'error': 'INVALID_PARAMETERS'}, 400)

    it = items_table.get(Item.id == item_id)
    ordered = it.get('ordered', 0)
    stock = it.get('stock', 0)

    if quantity > ordered:
        return ({'error': 'TOO_MANY_DELIVERED'}, 400)
    else:
        ordered = ordered - quantity
        stock = stock + quantity

    items_table.update({'ordered': ordered, 'stock': stock}, doc_ids=[it.doc_id])

    return items_table.get(Item.id == item_id), 201