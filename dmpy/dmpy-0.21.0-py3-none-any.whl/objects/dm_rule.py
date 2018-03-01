import attr


def stringify(val):
    return str(val)


def convert_to_list(val):
    if val is None:
        return []
    if isinstance(val, str):
        return [val]
    try:
        iter(val)
    except TypeError:
        return [str(val)]
    if None in val:
        raise ValueError('deps may not include None type: {}'.format(val))
    val = [str(v) for v in val]
    return list(val)


@attr.s(slots=True)
class DMRule(object):
    """Stores all info for writing a makefile rule

    # dependencies may be a string or an iterable of objects listifyable to string
    >>> DMRule("target", "dep", "recipe").deps
    ['dep']
    >>> DMRule("target", ["dep"], "recipe").deps
    ['dep']
    >>> DMRule("target", [("dep",)], "recipe")
    DMRule(target='target', deps=["('dep',)"], recipe=['recipe'])
    >>> DMRule("target", None, "recipe")
    DMRule(target='target', deps=[], recipe=['recipe'])
    >>> # Path objects are converted to string
    >>> from pathlib import Path
    >>> DMRule(Path("target"), [Path("dep")], "recipe")
    DMRule(target='target', deps=['dep'], recipe=['recipe'])
    >>> DMRule(Path("target"), Path("dep"), "recipe")
    DMRule(target='target', deps=['dep'], recipe=['recipe'])

    """
    target = attr.ib(convert=stringify)
    deps = attr.ib(attr.Factory(list), convert=convert_to_list)
    recipe = attr.ib(attr.Factory(list), convert=convert_to_list)

    @target.validator
    def not_none(self, attribute, value):
        if value is None:
            raise ValueError("target may not be None type")

    @property
    def name(self):
        return self.recipe[0].lstrip().partition(' ')[0]
