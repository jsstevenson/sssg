import blog_generate as bg
import pytest
import datetime as dt

def test_extract_meta():
    line = "# meta-info\n"
    assert bg.extract_meta(line) == line[2:-1]
    bad_line = "meta-info\n"
    with pytest.raises(Exception):
        bg.extract_meta(bad_line)


def test_remove_unsafe_chars():
    title1 = "AStringWithNoUnsafeChars"
    assert bg.remove_unsafe_chars(title1) == "astringwithnounsafechars"
    title2 = "A String With Spaces"
    assert bg.remove_unsafe_chars(title2) == "a-string-with-spaces"
    title3 = "Lotta $$ unsafe [] % chars # here"
    assert bg.remove_unsafe_chars(title3) == "lotta--unsafe---chars--here"


def test_add_post():
    """
    Using the template material from docs/post_template.md and
    docs/post_template_verbose.md
    """
    # test minimal post
    post_path = "docs/post_template.md"
    posts_list = []
    tags_dict = {}
    post = bg.add_post(post_path, posts_list, tags_dict)
    assert len(posts_list) == 1
    assert len(tags_dict) == 3
    assert type(post) is bg.Post
    assert post is posts_list[0]
    assert post.title == 'TITLE TITLE TITLE'
    assert post.url == 'title-title-title'
    for tag_name in tags_dict.keys():
        assert type(tags_dict[tag_name]) is bg.Tag
        assert post in tags_dict[tag_name].members
    assert "comma" in tags_dict.keys()
    assert "separated" in tags_dict.keys()
    assert "tags" in tags_dict.keys()
    assert post.date == dt.datetime(2020, 5, 8)
    assert post.preview == 'preview sentence...'
    # assert post.body == '<p>Just some words.</p>'

    # test verbose post
    verbose_post_path = "docs/post_template_verbose.md"
    post = bg.add_post(verbose_post_path, posts_list, tags_dict)
    assert len(posts_list) == 2
    assert len(tags_dict) == 5
    assert type(post) is bg.Post
    assert post is posts_list[1]
    assert post.title == 'Title of More Verbose Template'
    assert post.url == 'title-of-more-verb'
    for tag_name in ['several', 'tags', 'comma', 'etc']:
        assert type(tags_dict[tag_name]) is bg.Tag
        assert post in tags_dict[tag_name].members
    assert "several" in tags_dict.keys()
    assert "tags" in tags_dict.keys()
    assert "etc" in tags_dict.keys()
    assert "comma" in tags_dict.keys()
    assert post.date == dt.datetime(2020, 9, 14)
    assert post.preview == 'longer preview longer preview longer preview'
    body = """
    <h2>This is the first line in the doc.</h2>\n<p>Lorem ipsum. <em>Italic text.</em> Lorem ipsum. <strong>Bold text.</strong></p>\n<h2>header 2</h2>\n<p>Unordered list.</p>\n<ul>\n<li>Item 1.</li>\n<li>Item 2. Taking lots of lines. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text. Long text.</li>\n<li>Item 3.</li>\n</ul>\n<h2>header 2</h2>\n<p><code>code\ncode code code\ncode</code></p>\n<hr>\n<h2>header 2</h2>'
    """
    # assert post.body == body
