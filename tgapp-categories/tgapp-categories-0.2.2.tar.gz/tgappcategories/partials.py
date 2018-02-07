from tg import expose

@expose('tgappcategories.templates.little_partial')
def something(name):
    return dict(name=name)