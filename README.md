# bssg: Basic Static Site Generator

## Description

Generates a simple static blog site, including headers (eg navigation bar to
pages) based on provided HTML templates and posts in Markdown files.

## Setup & Usage

### Requirements

* Python 3.6+ (for [PEP 498-style string formatting](https://www.python.org/dev/peps/pep-0498/))

### Execution

Get requirements via pip

```bash
pip install -r requirements.txt
```

Give it an input directory and an output destination:

```bash
python3 bssg.py <path-to-blog-content> <path-to-output>
```

### Input layout

The provided blog content directory should include the following elements:

```
├── home_content.html
├── posts
│   ├── post1.md
│   ├── post2.md
│   └── post3.md
│     ...
├── projects_content.html  # or other static content pages
├── resources
│   ├── img1.png
│   ├── img2.png
│   └── img3.png
│     ...
└── template_components
    ├── body_template.html
    ├── card_template.html
    ├── custom.css
    ├── header_template.html
    ├── post_list_title_card.html
    └── post_list_card.html
```


## Known Issues

* Risks of duplicating post names/URLs and tag URLs
