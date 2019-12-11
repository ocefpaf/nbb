import textwrap

import pytest

from nbb.nbb import _beautify_cell, _nbcell_black, _nbcell_isort


@pytest.fixture
def cell():
    yield textwrap.dedent(
        """
    from nbb import _nbcell_isort
    import numpy as np
    import sys

    print('This is just a test.')
    """
    )


def test__nbcell_isort(cell):
    expected = textwrap.dedent(
        """
    import sys

    import numpy as np
    from nbb import _nbcell_isort

    print('This is just a test.')
    """
    )
    res = _nbcell_isort(cell)
    assert expected == res


def test__nbcell_black(cell):
    expected = textwrap.dedent(
        """
    from nbb import _nbcell_isort
    import numpy as np
    import sys

    print("This is just a test.")
    """
    ).strip()
    res = _nbcell_black(cell)
    assert expected == res


def test__beautify_cell(cell):
    expected = textwrap.dedent(
        """
    import sys

    import numpy as np
    from nbb import _nbcell_isort

    print("This is just a test.")
    """
    ).strip()
    res = _beautify_cell(cell)
    assert expected == res
