import argparse
import datetime
import os
import re
import mistune
from collections import defaultdict


MAX_URL_LEN = 14


class Tag:
    """
    Simple tag class.
    @name: String (init sanitizes)
    @members: List (empty or otherwise) of Post objects
    """
    def __init__(self, name, members=[]):
        self.name = remove_unsafe_chars(name)
        self.members = members


class Post:
    """
    Simple post class. Maintains a list of strings that are names of Tag
    objects.
    @title: String
    @url: String containing the HTML doc name minus extension (not full URL)
    @tags: List of Strings where each corresponds to the name field of a Tag
    @date: Datetime.Datetime
    @preview: String containing short preview text
    """
    def __init__(self, title="", url="", tags=[], date=None, preview="",
                 body=""):
        self.title = title
        self.url = url
        self.tags = tags
        self.date = date
        self.preview = preview
        self.body = body


def extract_meta(line):
    """
    Remove meta marks and extract info from blog post md files
    @line: String
    """
    if line[:2] == "# ":
        return line[2:]
    else:
        raise Exception("Data invalid or non-existant")


def remove_unsafe_chars(string):
    """
    Check every char in input @string to verify that it's not an unsafe
    character requiring extra encoding (because who needs that noise)
    Returns a string with all unsafe chars either replaced or removed.
    """
    pattern = re.compile("[a-zA-Z0-9\-_\.\+!\*'\()]")
    fixed = ""
    for c in string:
        if pattern.search(c):
            fixed += c
        elif c is ' ':
            fixed += '-'
    return fixed.lower()


def add_post(fpath, posts_list, tags_dict):
    """
    Add file located at fpath to the stored collection of posts and tags.
    @fpath: String, path to find file to add
    @posts_list: List of Post objects
    @tags_dict: dict where keys are tag name Strings and values are
    Set of Post objects
    """
    infile = open(fpath)

    # get meta
    title = extract_meta(infile.readline())
    url = remove_unsafe_chars(title)[:MAX_URL_LEN]
    while not url[-1].isalnum() and len(url) > 1:
        url = url[:-1]
    tags = extract_meta(infile.readline()).split(',')
    tags = [remove_unsafe_chars(tag) for tag in tags]
    date = datetime.datetime.strptime(extract_meta(infile.readline()),
                                                   "%Y/%m/%d")
    preview = extract_meta(infile.readline())


    # get body
    body = infile.read()
    infile.close()

    # clean up newlines
    while body[0] == '\n':
        body = body[1:]
    while body[-1] == '\n':
        body = body[:-1]

    # generate objects
    post = Post(title, url, tags, date, body)
    posts_list.append(post)
    for tag in tags:
        if tag in tags_dict.keys():
            tags_dict[tag].members.append(post)
        else:
            tags_dict[tag] = Tag(tag, [post])
    return post


def make_header(posts):
    """
    @posts: List of Post objects
    Create header HTML, including links to all posts
    Read from hardcoded template file
    TODO: more hardcoding of list border tags
    """
    listings = defaultdict(set)
    header_html = ""
    for post in posts:
        listings[post.year].add(post.strftime("%B"))
    header_template_html = open("template_components/header_template.html")
    start_pattern = re.compile("<!--monthlist-->")
    line = header_template_html.readline()
    while not start_pattern.search(line):
        header_html += line
        line = header_template_html.readline()
    header_html += line
    for year in listings.keys():
        for month in listings[year]:
            header_html += f'<a class="dropdown-item" href="https://jsstevenson.github.io/blog/{year}/{month}.html">{month} {year}</a>'
    header_template_html.readline()
    while line:
        header_html += line
        line = header_template_html.readline()
    return header_html


def make_template(input_dir, header_html):
    """
    Create HTML template for all pages. Takes the generated Header HTML and
    plugs it into the appropriate place on the page found at input_dir, and
    returns the full template as a string.
    """
    t_file = open(os.path.join(input_dir,
                               'template_components/body_template.html', 'r'))
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
    return template_html


def make_post(post, template, output_dir):
    """
    Assemble individual post and write to output directory.
    Template should be a string but really it's the full HTML template.
    Will save as a completed HTML file under the directory corresponding to
    the post's date.
    """
    post_html = template[:]
    post_html = post_html.replace("<title>template</title>",
                                  f"<title>{post.title}</title>")
    post_html = post_html.replace("<!--main page-->\n<!--/main page-->",
                                  post.body)
    out_path = os.path.join(output_dir, f"blog/{post.date.year}/" +
                            "{post.date.month}/{post.url}.html")
    out_file = open(out_path, "w")
    out_file.write(post_html)
    out_file.close()
    return post_html


def make_card(post):
    """
    @param title: String
    @param date: datetime.datetime
    @param preview: String
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
    """
    @tag: Tag object to generate page for
    @template: string containing page HTML template
    @output_dir: string containing path to output directory
    Returns completed page_html and saves page to appropriate directory
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
    out_path = os.path.join(output_dir, f"blog/tag/{tag.name}.html")
    out_file = open(out_path, "w")
    out_file.write(page_html)
    out_file.close()
    return page_html


def make_month(month, posts, template_html, output_dir):
    """
    @month: tuple pair of Strings indicating (month, year)
    @posts: List of Post objects under that month/year
    @template_html: string containing page template html
    @output_dir: string containing path to output directory
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
    out_path = os.path.join(output_dir, f"blog/{month[1]}/{month[0]}.html")
    out_file = open(out_path, "w")
    out_file.write(page_html)
    out_file.close()
    return page_html


def make_recent(posts, template_html, output_dir):
    """
    @posts_list: List of all Post objects
    @template_html: string containing page template html
    @output_dir: string containing path to output directory
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
    out_path = os.path.join(output_dir, "blog/recent.html")
    out_file = open(out_path, "w")
    out_file.write(page_html)
    out_file.close()
    return page_html
    return


def make_core_pages(template_html, input_dir, output_dir):
    """
    @template_html: string containing page template html
    @input_dir: string containing path to input directory. Should include
    premade HTML to generate "home" and "projects" pages.
    @output_dir: string containing path to output directory
    """
    home_path = os.path.join(input_dir, "home_content.html")
    home_file = open(home_path, "r")
    home_html = template_html[:]
    home_html = home_html.replace("<title>template</title>",
                                  "<title>james stevenson</title>")
    home_html = home_html.replace("<!--main page-->\n<!--/main page-->",
                                  home_file.read())
    home_file.close()

    projects_path = os.path.join(input_dir, "projects_content.html")
    projects_file = open(projects_path, "r")
    projects_html = template_html[:]
    projects_html = projects_html.replace("<title>template</title>",
                                          "<title>projects</title>")
    projects_html = projects_html.replace("<!--main page-->\n<!--/main page-->",
                                          projects_file.read())
    projects_file.close()
    return


def main():
    parser = argparse.ArgumentParser()
    # TODO clean up parser setup
    parser.add_argument('In', metavar='in', type=str,
                        help='path to input dir')
    parser.add_argument('Out', metavar='out', type=str,
                        help='path to output dir')
    args = parser.parse_args()
    input_dir = args.In
    output_dir = args.Out

    posts_list = [] # list of Post objects
    tags_dict = {} # key is tag name, value is Tag object

    # open blog posts directory, read each post into internal listings
    for entry in os.listdir(input_dir):
        if os.path.isfile(os.path.join(input_dir, entry)):
            add_post(os.path.join(input_dir, entry), posts_list, tags_dict)

    # generate template
    header_html = make_header(posts_list)
    template_html = make_template(input_dir, header_html)

    # generate pages from template
    for post in posts_list:
        make_post(post, template_html, output_dir)
    for tag in tags_dict.keys():
        make_tag(tag, tags_dict[tag], template_html, output_dir)

    months = defaultdict(list)
    for post in posts_list:
        m_y = (post.date.strftime("%B"), str(post.date.year))
        months[m_y].append(post)
    for month, posts in months:
        make_month(month, posts, template_html, output_dir)

    make_recent(posts_list, template_html, output_dir)

    make_core_pages(template_html, input_dir, output_dir)


if __name__ == '__main__':
    main()
