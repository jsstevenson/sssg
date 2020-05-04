import argparse
import datetime
import os
import re
import mistune
from collections import defaultdict

class Tag:
    """
    Simple tag class. Name should be a string.
    """
    def __init__(self, name, members=[]):
        self.name = remove_unsafe_chars(name)
        self.members = []


class Post:
    def __init__(self, title="", tags=[], date=None, preview="", body=""):
        self.title = title
        self.tags = tags
        self.date = date
        self.preview = preview
        self.body = body


def extract_meta(line):
    '''
    Remove meta marks and extract info from blog post md files
    '''
    if len(line) > 2:
        return line[2:]
    else:
        raise Exception("Expected to find data and didn't")


def remove_unsafe_chars(string):
    """
    Check every char in input string to verify that it's not an unsafe
    character requiring extra encoding (because who needs that noise)
    Returns a string with all unsafe chars either replaced or removed.
    """
    pattern = re.compile("[a-zA-Z0-9\-_\.\+!\*'\()],,")
    fixed = ""
    for c in string:
        if pattern.match(c):
            fixed += c
        elif c is ' ':
            fixed += '-'
    return fixed.lower()


def add_post(fpath, posts_list, tags_dict):
    infile = open(fpath)

    # get meta
    title = extract_meta(infile.readline())
    tags = extract_meta(infile.readline()).split(',')
    tags = [remove_unsafe_chars(tag) for tag in tags]
    fmt = "%Y/%m/%d"
    date = datetime.datetime.strptime(extract_meta(infile.readline()), fmt)
    preview = extract_meta(infile.readline())

    # get body
    body = infile.read()
    close(infile)

    # generate objects
    post = Post(title, tags, date, body)
    posts_list.append(post)
    for tag in tags:
        if tag in tags_dict.keys():
            tags_dict[tag].members.append(post)
        else:
            tags_dict[tag] = Tag(tag, [post])
    return


def make_header(posts):
    """
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
    end_pattern = re.compile("<!--/monthlist-->")
    line = header_template_html.readline()
    while not pattern.search(line):
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
    t_file = open(os.path.join(input_dir, 'template_components/body_template.html', 'r'))
    template_html = ""
    pattern = re.compile("<!--navbar-->")
    line = t_file.readline()
    while not pattern.search(line):
        template_html += line
        line = t_file.readline()



def make_post(post, template):



def main():
    parser = argeparse.ArgumentParser()
    #TODO clean up parser setup
    parser.add_argument('In', metavar='in', type=str, help='path to input dir')
    parser.add_argument('Out', metavar='out', type=str, help='path to output dir')
    args = parser.parse_args()
    input_dir = args.In
    output_dir = args.Out

    posts_list = []
    tags_dict = {}

    # open blog posts directory, read each post into internal listings
    for entry in os.listdir(input_dir):
        if os.path.isfile(os.path.join(input_dir, entry)):
            add_post(os.path.join(input_dir, entry), posts_list, tags_dict)

    # generate page headers for templates
    header_html = make_header(posts_list)

    # generate post pages

    # generate tag pages
    # generate month pages
    # generate "recent" page
    # generate project pages
    # update
    return

if __name__ == '__main__':
    main()
