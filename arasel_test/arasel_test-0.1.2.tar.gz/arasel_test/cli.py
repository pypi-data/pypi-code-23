# -*- coding: utf-8 -*-

"""Console script for arasel_test."""
import numpy

import click
import dill
dill.settings['recurse']=True

from arasel_test import AraselETL, Customer


@click.command()
@click.option('--orders', help='Path to Order\'s CSV file', type=click.Path(exists=True))
@click.option('--modelpath', help='Path to model.dill file', type=click.Path(exists=True))
@click.option('--output', help='Path to output CSV file with CLV predictions', type=click.Path())
@click.option('--port', help='Port for Flask Application', type=click.INT)
def main(orders, modelpath, output, port):
    """Console script for arasel_test."""
    from arasel_test.app import app, db
    with app.app_context():
        if not orders:
            orders = app.config['ORDERS_CSV']
        if not modelpath:
            modelpath = app.config['MODEL_PATH']
        if not port:
            port = 8080

        with open(modelpath, 'rb') as f:
            model = dill.dill.load(f)

        etl = AraselETL(orders, model)

        try:
            customer_clvs = etl.customer_clvs

            for customer_id, clv in customer_clvs.items():
                customer = Customer(customer_id=customer_id, clv=clv)
                db.session.merge(customer)

            db.session.commit()

            if output:
                etl.to_csv(output)

            app.run(host='0.0.0.0', port=port)

        except NameError:
            print("Error in model. import numpy inside your model to proceed successfully")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
