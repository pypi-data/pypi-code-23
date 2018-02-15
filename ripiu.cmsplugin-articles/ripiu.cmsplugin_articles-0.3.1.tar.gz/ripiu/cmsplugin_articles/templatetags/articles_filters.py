from django import template

register = template.Library()


@register.filter(name='split_parts')
def split_parts(children):
    head = None
    main = None
    leftover = []
    if children:
        for child in children:
            print('child: %s' % child.plugin_type)
            if child.plugin_type == 'HeaderPlugin':
                head = child
            elif child.plugin_type == 'MainPlugin':
                main = child
            else:
                leftover.append(child)
    return {
        'head': head,
        'main': main,
        'leftover': leftover,
    }
