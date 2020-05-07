import blog_generate as bg
import pytest

def test_extract_meta():
    line = "# meta-info"
    assert bg.extract_meta(line) == line[2:]
    bad_line = "meta-info"
    with pytest.raises(Exception):
        bg.extract_meta(bad_line)
