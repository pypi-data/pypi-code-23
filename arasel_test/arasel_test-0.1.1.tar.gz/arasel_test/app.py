import os
import numpy

from flask import jsonify

from arasel_test.config import config
from arasel_test import create_app, db, load_db
from arasel_test.models import Customer

env = os.getenv('ARASEL_ENV', 'dev')
conf = config[env]

app = create_app(env)
app.secret_key = 'SGnwognWNWdwgjwHwrgjvSgjaAJgwjgnI2262h'

@app.route('/customers/<customer_id>')
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return jsonify({
        'customer_id': customer.customer_id,
        'clv': customer.clv
    })

@app.errorhandler(404)
def error_404(e):
    return "Try: /customers/<i>customer_id</i>", 404

if __name__ == '__main__':
    load_db(app, db)
    app.run(host='0.0.0.0', port=8080)
