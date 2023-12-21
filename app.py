#!/data/project/whichsub/www/python/venv/bin/python
# -*- coding: utf-8 -*-

"""Find which sub-templates contain the given text."""

import re

from flask import Flask, render_template, request
from pywikibot import Page, Site
from pywikibot.exceptions import (
    InvalidTitleError,
    UnknownFamilyError,
    UnknownSiteError,
)

app = Flask(__name__)


def find_sub_templates(
    lookingfor: str, page: Page, wholeword: bool, matchcase: bool
):
    found_templates = []
    if page.isRedirectPage():
        page = page.getRedirectTarget()
    pagetext = page.text
    if not matchcase:
        pagetext = pagetext.lower()
        lookingfor = lookingfor.lower()
    if wholeword:
        pattern = re.compile(r'\b' + re.escape(lookingfor) + r'\b')
        if pattern.search(pagetext):
            found_templates.append(page)
    elif lookingfor in pagetext:
        found_templates.append(page)

    for sub_template in page.templates(content=True):
        if sub_template.isRedirectPage():
            sub_template = sub_template.getRedirectTarget()
        text = sub_template.text if matchcase else sub_template.text.lower()
        if wholeword:
            # noinspection PyUnboundLocalVariable
            if pattern.search(text):
                found_templates.append(sub_template)
        elif lookingfor in text:
            found_templates.append(sub_template)

    # Remove duplicate templates
    return {f.title(): f for f in found_templates}.values()


@app.route('/')
def main():
    args = request.args
    code = args.get('code', 'en')
    family = args.get('family', 'wikipedia')
    lookingfor = args.get('lookingfor') or ''
    pagetitle = args.get('pagetitle') or ''
    wholeword = bool(args.get('wholeword', False))
    matchcase = bool(args.get('matchcase', True))

    try:
        site = Site(code, family)
    except UnknownFamilyError:
        family = 'UnknownFamily'
        templates = None
    except UnknownSiteError:
        code = 'UnknownSite'
        templates = None
    else:
        if lookingfor and pagetitle:
            try:
                page = Page(site, pagetitle)
            except ValueError:
                templates = None
            else:
                try:
                    templates = find_sub_templates(
                        lookingfor, page, wholeword, matchcase
                    )
                except InvalidTitleError:
                    pagetitle = 'InvalidTitle'
                    templates = None
        else:
            templates = None

    return render_template(
        'main.html',
        code=code,
        family=family,
        pagetitle=pagetitle,
        lookingfor=lookingfor,
        templates=templates,
        wholeword=wholeword,
        matchcase=matchcase,
    )


if __name__ == '__main__':
    try:
        from flup.server.fcgi import WSGIServer

        WSGIServer(app).run()
    except ImportError:
        app.run(debug=True)
