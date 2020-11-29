
from notebooks.common.utils import replace_path


def test_replace_path():
    assert replace_path('/tmp/hej.zip', '/data') == '/data/hej.zip'
    assert replace_path('hej.zip', '/data') == '/data/hej.zip'
    assert replace_path('hej.zip', 'data') == 'data/hej.zip'
