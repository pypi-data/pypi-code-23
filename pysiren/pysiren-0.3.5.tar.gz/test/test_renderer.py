from pysiren import *
from pysiren.renderer import to_renderable


def test_siren_render():
    entity = Entity(['class1', 'class2'])
    expected = {'class': ['class1', 'class2']}
    assert(to_renderable(entity).render() == expected)


def test_siren_render_full():
    entity = Entity(['className'],
                         title='entityTitle',
                         links=[
                             Link([PredefRelValue.NEXT], "next/link",
                                       title="Link to next",
                                       type=MediaType("application/json"),
                                       classes=["c1", "c2"])
                         ],
                         properties={
                            'bool': True,
                            'bool2': False,
                            'int': 1,
                            'text': 'gfdgd',
                            'float': 0.232,
                            'empty': []
                         },
                         actions=[
                             Action("add-item",
                                         href="http://api.com/add",
                                         title="Add Item",
                                         method=Method.POST,
                                         type=MediaType('application/x-www-form-urlencoded'),
                                         fields=[
                                             Field("orderNumber", type=FieldType.HIDDEN, value=42),
                                             Field("productCode", type=FieldType.TEXT),
                                             Field("quantity", type=FieldType.NUMBER),
                                             Field("list", type=FieldType.RADIO, value=[
                                                 FieldValueObject('val1', title="Value 1", selected=True),
                                                 FieldValueObject('val2', title="Value 2", selected=False)
                                             ])
                                         ])
                         ]
    )

    expected = {
        'class': ['className'],
        'title': 'entityTitle',
        'links': [
            {'rel': ["next"], 'href': 'next/link', 'title':'Link to next', 'type': 'application/json', 'class': ['c1', 'c2']}
        ],
        'properties': {
            'bool': True,
            'bool2': False,
            'int': 1,
            'text': 'gfdgd',
            'float': 0.232,
            'empty': []
        },
        "actions": [
            {
                "name": "add-item",
                "title": "Add Item",
                "method": "POST",
                "href": "http://api.com/add",
                "type": "application/x-www-form-urlencoded",
                "fields": [
                    {"name": "orderNumber", "type": "hidden", "value": 42},
                    {"name": "productCode", "type": "text"},
                    {"name": "quantity", "type": "number"},
                    {"name": "list", "type": "radio", "value": [
                        {"title": "Value 1", "value": "val1", "selected": True},
                        {"title": "Value 2", "value": "val2", "selected": False}
                    ]}
                ]
            }
        ],
    }

    result = to_renderable(entity).render()
    import json
    print(json.dumps(result))
    print(json.dumps(expected))

    assert(expected == result)
