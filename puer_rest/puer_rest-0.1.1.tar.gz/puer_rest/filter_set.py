from marshmallow import Schema, post_load


__all__ = ["FilterSetSchema"]


class FilterSetSchema(Schema):
    def dotter(self, d, key, dots):
        if isinstance(d, dict):
            for k in d:
                self.dotter(d[k], key + '.' + k if key else k, dots)
        else:
            dots.update({key: d})
        return dots

    @post_load
    def mongo_filter(self, item):
        return self.dotter(item, '', {})