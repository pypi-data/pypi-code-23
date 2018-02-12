from pysiren import *
from pysiren.renderer import *
import copy
import time


def entity():
    return Entity(
        ['className'],
        title='entityTitle',
        links=[
            Link(
                [PredefRelValue.NEXT],
                "next/link",
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
            'empty': [],
            'dict': {
                'bool': True,
                'bool2': False,
                'int': 1,
                'text': 'gfdgd',
                'float': 0.232,
            }
        },
        actions=[
            Action(
                "add-item",
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
                ]
            )
        ]
    )


def make_data(entity):
    base = copy.copy(entity())
    sub_entities = [copy.copy(entity()) for i in list(range(1, 20))]

    base.entities = sub_entities
    return base


def time_renderer(data):
    start = time.clock()
    for i in range(1, 10):
        for x in range(1, 100):
            temp = to_renderable(data).render()

    end = time.clock()
    return (end-start)


# Crude test to make sure it does not get slower
# def test_performance():
#     data = make_data(entity)
#     time = time_renderer(data)
#     assert (time < 3.0)
