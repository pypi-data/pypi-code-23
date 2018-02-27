
from modelx import *

import pytest


@pytest.mark.parametrize("cells, values", [
    (['Scalar1'], [1]),
    (['Scalar1', 'Scalar2'], [1, 2])
])
def test_space_to_dataframe_scalarcells(cells, values):

    space = new_model().new_space()
    for c in cells:
        space.new_cells(c)

    print(space.frame.index.names)