import argparse
import datetime
import os
import shutil
import re
import mistune
from collections import defaultdict
import pathlib


MAX_URL_LEN = 18  # max length of a tag or post file (not counting .html)


class Tag:
    """Class representing tags associated with blog posts

    The tag-to-post relationship is many-to-many.

    Attributes:
        name (String): name of the tag. __init__() will sanitize it.
        members (List): contains Post objects tagged w/ this tag
    """

    def __init__(self, name, members=[]):
        """Default constructor builds tag with given name and empty members"""
        self.name = remove_unsafe_chars(name)
        self.members = members


class Post:
    """Class representing a blog post

    Attributes:
        title (String): post title
        tags (List): list of Tag objects associated with the post
        date (datetime.datetime): date post published
        preview (String): Preview text to display in post card
        body (String): HTML containing blog post substance
    """

    def __init__(self, title, date, tags=[], preview="",
                 body=""):
        self.title = title
        self.tags = tags
        self.date = date
        self.preview = preview
        self.body = body


def extract_meta(line):
    """Remove meta marks and extract info from blog post md files

    Args:
        line (String): line to pull info from

    Returns:
        line without leading '# ' and ending newline

    Raises:
        Exception: String is formatted incorrectly
    """
    if (line[:2] == "# ") and (line[-1] == '\n'):
        return line[2:-1]
    else:
        raise Exception("Data invalid or non-existant")


def remove_unsafe_chars(string):
    """Remove URL-unsafe characters

    Args:
        string (String): to be sanitized

    Returns:
        given string without any URL-unsafe characters (and spaces replaced
        with dashes)
    """
    pattern = re.compile("[a-zA-Z0-9-_.+!*'()]")
    fixed = ""
    for c in string:
        if pattern.search(c):
            fixed += c
        elif c is ' ':
            fixed += '-'
    return fixed.lower()


def add_post(fpath, posts_list, tags_dict):
    """Create Post (and any necessary Tags) and add them to tracking lists

    Args:
        fpath (String): path to raw post file (should be .md)
        posts_list (List): possibly-empty list of Posts; will be modified
        tags_dict (Dictionary): key is tag name, value is Tag object

    returns:
        created Post object. Also modifies posts_list and tags_dict to contain
        any newly created objects where needed
    """
    print(f"reading post from {fpath}")
    infile = open(fpath)

    # get meta
    title = extract_meta(infile.readline())
    url = remove_unsafe_chars(title[:MAX_URL_LEN])
    while not url[-1].isalnum() and len(url) > 1:
        url = url[:-1]
    tags = extract_meta(infile.readline()).split(',')
    tags = [remove_unsafe_chars(tag) for tag in tags]
    date = datetime.datetime.strptime(extract_meta(infile.readline()),"%Y/%m/%d")
    preview = extract_meta(infile.readline())

    # get body
    body = mistune.markdown(infile.read())
    infile.close()

    # clean up newlines
    while body[0] == '\n':
        body = body[1:]
    while body[-1] == '\n':
        body = body[:-1]

    # generate objects
    post = Post(title, date, tags, preview, body)
    posts_list.append(post)
    for tag in tags:
        if tag in tags_dict.keys():
            tags_dict[tag].members.append(post)
        else:
            tags_dict[tag] = Tag(tag, [post])
    print(f"Added post from {fpath}")
    return post


def make_header(posts, in_path):
    """
    Make page header with correct links and appropriate relative paths

    Args:
        posts (List): List of Post objects
        in_path (String): path to provided input directory

    Returns:
        complete HTML for header, as a String
    TODO: more hardcoding of list border tags
    """
    listings = defaultdict(set)
    header_html = ""
    for post in posts:
        listings[post.date.year].add(post.date.strftime("%B"))
    header_template_html = open(os.path.join(in_path, "template_components/header_template.html"))
    start_pattern = re.compile("<!--monthlist-->")
    line = header_template_html.readline()
    while not start_pattern.search(line):
        header_html += line
        line = header_template_html.readline()
    header_html += line
    for year in listings.keys():
        for month in listings[year]:
            header_html += f'<a class="dropdown-item" href="<!replace_with_path>blog/{year}/{month}.html">{month} {year}</a>\n'
    header_template_html.readline()
    while line:
        header_html += line
        line = header_template_html.readline()
    print("Header generation successful")
    return header_html


def make_template(input_dir, header_html):
    """Create full HTML template for all pages

    Gets generated header HTML and plugs it into the given body template HTML.
    Will still need to add relative paths to all hyperlinks.

    Args:
        input_dir (String): path to provided input directory
        header_html (String): HTML for header/navbar/etc

    Returns:
        a String containing the full HTML template for all pages
    """
    t_file = open(os.path.join(input_dir,
                               'template_components/body_template.html'), 'r')
    template_html = ""
    pattern = re.compile("<!--navbar-->")
    line = t_file.readline()
    while not pattern.search(line):
        template_html += line
        line = t_file.readline()
    template_html += header_html
    t_file.readline()
    line = t_file.readline()
    while line:
        template_html += line
        line = t_file.readline()
    print("Template generation successful")
    return template_html


def make_post(post, template, output_dir):
    """Assemble individual post HTML and write to output directory.

    Args:
        post (Post): Post object to generate page for
        template (String): page HTML body template
        output_dir (String): path to output directory

    Returns:
        HTML for generated post page
        Also writes post to corresponding directory under output_dir
    """
    post_html = template[:]
    post_html = post_html.replace("<title>template</title>",
                                  f"<title>{post.title}</title>")
    post_html = post_html.replace("<!--main page-->\n<!--/main page-->",
                                  post.body)
    post_html = post_html.replace("<!replace_with_path>","../../../")
    out_path = os.path.join(output_dir, "blog")
    pathlib.Path(out_path).mkdir(exist_ok=True)
    out_path = os.path.join(out_path, str(post.date.year))
    pathlib.Path(out_path).mkdir(exist_ok=True)
    out_path = os.path.join(out_path, post.date.strftime("%B"))
    pathlib.Path(out_path).mkdir(exist_ok=True)
    out_path = os.path.join(out_path,
            f"{remove_unsafe_chars(post.title[:MAX_URL_LEN])}.html")
    out_file = open(out_path, "w")
    out_file.write(post_html)
    out_file.close()
    print(f"Successfully wrote post: {post.title}")
    return post_html


def make_card(post):
    """Generate HTML for post card in post index pages

    Args:
        post (Post): Post object to make card for

    Returns:
        HTML for generated card
    """
    return f"""
    <div class="card" style="margin-top: 1em">
      <div class="card-body">
        <h5 class="card-title">{post.title}</h5>
        <h6 class="card-subtitle mb-2 text-muted">{post.date.strftime("%B %d %Y")}</h6>
        <p class="card-text">{post.preview}</p>
      </div>
    </div>
    """


def make_tag(tag, template, output_dir):
    """Generate page for tag

    Args:
        tag (Tag): tag to make page for
        template (String): HTML (header/body) template
        output_dir (String): path to output directory

    Returns:
        HTML for generated tag page
        Also saves tag page to corresponding directory under output_dir
    """
    tag.members.sort(key=lambda x: x.date, reverse=True)
    post_cards = ""
    for post in tag.members:
        post_cards += make_card(post)
    page_html = template[:]
    page_html = page_html.replace("<title>template</title>",
                                  f"<title>Tag: {tag.name}</title>")
    page_html = page_html.replace("<!--main page-->\n<!--/main page-->",
                                  post_cards)
    page_html = page_html.replace("<!replace_with_path>", "../../")
    out_path = os.path.join(output_dir, "blog")
    pathlib.Path(out_path).mkdir(exist_ok=True)
    out_path = os.path.join(out_path, "tag")
    pathlib.Path(out_path).mkdir(exist_ok=True)
    out_path = os.path.join(out_path, f"{tag.name}.html")
    out_file = open(out_path, "w")
    out_file.write(page_html)
    out_file.close()
    print(f"Successfully created page for tag: {tag.name}")
    return page_html


def make_month(month, posts, template_html, output_dir):
    """Generate index page for a given month/year

    Args:
        month (Tuple): pair of Strings indicating (month, year)
        posts (List): of Post objects
        template_html (String): template HTML to fill in (page header/etc)
        output_dir (String): path to output directory

    Returns:
        HTML for generated month page
        Also writes month page to corresponding directory under output_dir
    """
    posts.sort(key=lambda x: x.date, reverse=True)
    post_cards = ""
    for post in posts:
        post_cards += make_card(post)
    page_html = template_html[:]
    page_html = page_html.replace("<title>template</title>",
                                  f"<title>{month[0]} {month[1]}</title>")
    page_html = page_html.replace("<!--main page-->\n<!--/main page-->",
                                  post_cards)
    page_html = page_html.replace("<!replace_with_path>", "../../")
    out_path = os.path.join(output_dir, "blog")
    pathlib.Path(out_path).mkdir(exist_ok=True)
    out_path = os.path.join(out_path, month[1])
    pathlib.Path(out_path).mkdir(exist_ok=True)
    out_path = os.path.join(out_path, f"{month[0]}.html")
    out_file = open(out_path, "w")
    out_file.write(page_html)
    out_file.close()
    print(f"Successfully created page for month: {month[0]} {month[1]}")
    return page_html


def make_recent(posts, template_html, output_dir):
    """Generate page for Recent Posts

    Args:
        posts_list (List): List of all Post objects
        template_html (String): string containing page template html
        output_dir (String): string containing path to output directory

    Returns:
        HTML for generated Recent page
        Also writes Recent page under corresponding directory in output_dir
    """
    posts.sort(key=lambda x: x.date, reverse=True)
    post_cards = ""
    for post in posts[:10]:
        post_cards += make_card(post)
    page_html = template_html[:]
    page_html = page_html.replace("<title>template</title>",
                                  "<title>recent posts</title>")
    page_html = page_html.replace("<!--main page-->\n<!--/main page-->",
                                  post_cards)
    page_html = page_html.replace("<!replace_with_path>", "../")
    out_path = os.path.join(output_dir, "blog")
    pathlib.Path(out_path).mkdir(exist_ok=True)
    out_path = os.path.join(out_path, "recent.html")
    out_file = open(out_path, "w")
    out_file.write(page_html)
    out_file.close()
    print("Successfully generated page for recent posts")
    return page_html


def make_core_pages(template_html, input_dir, output_dir):
    """Generate core site pages

    Args:
        template_html (String): string containing page template html
        input_dir (string): string containing path to input directory. Should
        include premade HTML to generate "home" and "projects" pages.
        output_dir (String): string containing path to output directoryA

    Returns:
        Nothing, but writes HTML to files under output_dir
    """
    template_html = template_html.replace("<!replace_with_path>", "")
    home_in_path = os.path.join(input_dir, "home_content.html")
    home_in_file = open(home_in_path, "r")
    home_html = template_html[:]
    home_html = home_html.replace("<title>template</title>",
                                  "<title>james stevenson</title>")
    home_html = home_html.replace("<!--main page-->\n<!--/main page-->",
                                  home_in_file.read())
    home_in_file.close()
    home_out_path = os.path.join(output_dir, "index.html")
    home_out_file = open(home_out_path, "w")
    home_out_file.write(home_html)
    home_out_file.close()

    projects_in_path = os.path.join(input_dir, "projects_content.html")
    projects_in_file = open(projects_in_path, "r")
    projects_html = template_html[:]
    projects_html = projects_html.replace("<title>template</title>",
                                          "<title>projects</title>")
    projects_html = projects_html.replace("<!--main page-->\n<!--/main page-->",
                                          projects_in_file.read())
    projects_in_file.close()
    projects_out_path = os.path.join(output_dir, "projects.html")
    projects_out_file = open(projects_out_path, "w")
    projects_out_file.write(projects_html)
    projects_out_file.close()

    print("Successfully generated core pages")
    return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('in_path', metavar='in_path', type=str,
                        help='path to input dir')
    parser.add_argument('out_path', metavar='out_path', type=str,
                        help='path to output dir')
    args = parser.parse_args()
    input_dir = args.in_path
    output_dir = args.out_path

    posts_list = [] # list of Post objects
    tags_dict = {} # key is tag name, value is Tag object

    # open blog posts directory, read each post into internal listings
    posts_path = os.path.join(input_dir, "posts")
    for entry in os.listdir(posts_path):
        post_path = os.path.join(posts_path, entry)
        if os.path.isfile(post_path):
            add_post(post_path, posts_list, tags_dict)

    # generate template
    header_html = make_header(posts_list, input_dir)
    template_html = make_template(input_dir, header_html)

    # generate pages from template
    pathlib.Path(output_dir).mkdir(exist_ok=True)
    pathlib.Path(os.path.join(output_dir, "css")).mkdir(exist_ok=True)
    shutil.copy(os.path.join(input_dir, "template_components/custom.css"),
                os.path.join(output_dir, "css/"))
    for post in posts_list:
        make_post(post, template_html, output_dir)
    for tag in tags_dict.values():
        make_tag(tag, template_html, output_dir)

    months = defaultdict(list)
    for post in posts_list:
        m_y = (post.date.strftime("%B"), str(post.date.year))
        months[m_y].append(post)
    for month in months.keys():
        make_month(month, months[month], template_html, output_dir)

    make_recent(posts_list, template_html, output_dir)

    make_core_pages(template_html, input_dir, output_dir)


if __name__ == '__main__':
    main()
