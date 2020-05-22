# bssg: Basic Static Site Generator

## Description

Generates a simple static blog site, including headers (eg navigation bar to
pages) based on provided HTML templates and posts in Markdown files.

## Setup & Usage

### Requirements:

* Python 3.6+ (for [PEP 498-style string formatting](https://www.python.org/dev/peps/pep-0498/))

### Execution

Get requirements via pip

```bash
pip install -r requirements.txt
```

Give it an input directory and an output destination:

```bash
python3 blog_generate.py <path-to-blog-content> <path-to-output>
```
