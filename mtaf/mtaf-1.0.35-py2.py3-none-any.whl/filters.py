import six


def get_filter(method, *args, **kwargs):

    def by_text_start(elem):
        return elem.text[:len(args[0])] == kwargs['text']

    def by_text_all(elem):
        return elem.text == kwargs['text']

    def by_within_frame(elem):
        e = elem
        f = kwargs['frame']
        try:
            f_loc = f.location
        except AttributeError:
            six.print_("f_loc = f.location: %s" % e)
            return True
        f_size = f.size
        f_x1 = f_loc['x']
        f_x2 = f_loc['x'] + f_size['width']
        f_y1 = f_loc['y']
        f_y2 = f_loc['y'] + f_size['height']
        try:
            e_loc = e.location
        except AttributeError:
            six.print_("e_loc = e.location: %s" % e)
            return True
        e_size = e.size
        e_x1 = e_loc['x']
        e_x2 = e_loc['x'] + e_size['width']
        e_y1 = e_loc['y']
        e_y2 = e_loc['y'] + e_size['height']
        return e_x1 >= f_x1 and e_x2 <= f_x2 and e_y1 >= f_y1 and e_y2 <= f_y2

    if method == 'text_start':
        return by_text_start
    elif method == 'text_all':
        return by_text_all
    elif method == 'within_frame':
        return by_within_frame
