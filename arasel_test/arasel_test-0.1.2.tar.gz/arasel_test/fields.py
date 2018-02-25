
import inspect

class Field:

    @classmethod
    def fields(cls):
        """Get list of class attributes"""
        return [value for key, value in cls.__dict__.items() if
                not key.startswith('__') and not inspect.isroutine(value)]

class OrderField(Field):
    customer_id = 'customer_id'
    order_id = 'order_id'
    order_item_id = 'order_item_id'
    num_items = 'num_items'
    revenue = 'revenue'
    created_at_date = 'created_at_date'

    @classmethod
    def get_dtypes(cls):
        return {
            cls.customer_id: str,
            cls.order_id: str,
            cls.order_item_id: str,
            cls.revenue: float
        }


class CustomerField(Field):
    customer_id = 'customer_id'
    predicted_clv = 'predicted_clv'


class ModelField(Field):
    max_num_items = 'max_num_items'
    max_revenue = 'max_revenue'
    total_revenue = 'total_revenue'
    total_orders = 'total_orders'
    days_since_last_order = 'days_since_last_order'
    longest_intervals = 'longest_intervals'
