import csv
from datetime import datetime

import numpy
import pandas as pd

from arasel_test.fields import OrderField, ModelField, CustomerField
from arasel_test.utils import longest_dates_interval



class AraselETL:

    def __init__(self, csv_path, prediction_model):
        self.csv_path = csv_path
        self.prediction_model = prediction_model
        self._clvs = None

    @property
    def customer_clvs(self):
        """
        Calculates based on customer orders and predition model, the Customer Lifetime Value

        :return: dictionary of customer_id: Customer Lifetime Value
        """
        if self._clvs is not None:
            return self._clvs

        dtype_dict = OrderField.get_dtypes()
        df = pd.read_csv(self.csv_path, dtype=dtype_dict, parse_dates=[OrderField.created_at_date])

        grouped_df = df.groupby(OrderField.customer_id)

        max_num_items = grouped_df[OrderField.num_items].max()
        max_revenue = grouped_df[OrderField.revenue].max()
        total_revenue = grouped_df[OrderField.revenue].sum()
        total_orders = grouped_df[OrderField.order_id].count()

        until_date = datetime(2017, 10, 17)
        days_since_last_order = grouped_df[OrderField.created_at_date].max().apply(lambda x: (until_date - x).days)

        customer_order_dates = grouped_df[OrderField.created_at_date].apply(list)
        longest_intervals = customer_order_dates.apply(longest_dates_interval)

        transformed_df = pd.concat(
            [max_num_items, max_revenue, total_revenue, total_orders, days_since_last_order, longest_intervals],
            axis=1,
            keys=[ModelField.max_num_items, ModelField.max_revenue, ModelField.total_revenue,
                  ModelField.total_orders, ModelField.days_since_last_order,
                  ModelField.longest_intervals]
        )

        # NaN values in longest_intervals are the ones with only one order date (no possible interval)
        avg_longest_interval = longest_intervals.mean()
        transformed_df[ModelField.longest_intervals]\
            .fillna(transformed_df[ModelField.days_since_last_order] + avg_longest_interval)

        clvs = self.prediction_model.predict(transformed_df.values)

        self._clvs = {customer_id: clv for customer_id, clv in zip(transformed_df.index, clvs)}

        return self._clvs

    def to_csv(self, path):
        """Outputs CSL's to CSV file"""
        clvs = self.customer_clvs

        try:
            with open(path, 'w') as f:
                writer = csv.DictWriter(f, fieldnames=[CustomerField.customer_id, CustomerField.predicted_clv])
                writer.writeheader()

                for customer_id, clv in clvs.items():
                    row = {
                        CustomerField.customer_id: customer_id,
                        CustomerField.predicted_clv: clv
                    }
                    writer.writerow(row)

        except OSError:
            print("Cannot open file to write: {}".format(path))
