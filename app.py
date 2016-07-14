#!/data/project/whichsub/www/python/venv/bin/python
# -*- coding: utf-8 -*-

"""Find which sub-templates contain the given text."""


from os import name as os_name
import re

from flask import Flask
from flask import request
from flask import render_template
import pywikibot as pwb
if os_name == 'posix':
    from flup.server.fcgi import WSGIServer


app = Flask(__name__)


def find_sub_templates(
        lookingfor: str, page: pwb.Page, wholeword: bool, matchcase: bool
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
    pagetitle = args.get('pagetitle', '')
    lookingfor = args.get('lookingfor', '')
    wholeword = bool(args.get('wholeword', False))
    matchcase = bool(args.get('matchcase', False))

    try:
        site = pwb.Site(code, family)
    except pwb.exceptions.UnknownFamily:
        family = 'UnknownFamily'
        templates = None
    except pwb.exceptions.UnknownSite:
        code = 'UnknownSite'
        templates = None
    else:
        try:
            page = pwb.Page(site, pagetitle)
        except ValueError:
            # when not pagetitle
            templates = None
        else:
            try:
                templates = find_sub_templates(
                    lookingfor, page, wholeword, matchcase
                )
            except pwb.exceptions.InvalidTitle:
                pagetitle = 'InvalidTitle'
                templates = None

    return render_template(
        'main.html',
        code=code,
        family=family,
        pagetitle=pagetitle,
        lookingfor=lookingfor,
        templates=templates,
        wholeword=wholeword,
        matchcase=matchcase
    )


if __name__ == '__main__':
    if os_name == 'posix':
        WSGIServer(app).run()
    else:
        app.run(debug=True)
