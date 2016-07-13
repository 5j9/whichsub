#!/data/project/whichsub/www/python/venv/bin/python
# -*- coding: utf-8 -*-

"""Find which subtemplates contain the given text."""


from os import name as os_name

from flask import Flask
from flask import request
from flask import render_template
import pywikibot as pwb
if os_name == 'posix':
    from flup.server.fcgi import WSGIServer


app = Flask(__name__)


def find_sub_templates(lookingfor: str, page: pwb.Page):
    found_templates = []
    if page.isRedirectPage():
        page = page.getRedirectTarget()
    if lookingfor in page.text:
        found_templates.append(page)

    for sub_template in page.templates(content=True):
        if sub_template.isRedirectPage():
            sub_template = sub_template.getRedirectTarget()
        if lookingfor in sub_template.text:
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
            # if not pagetitle:
            templates = None
        else:
            try:
                templates = find_sub_templates(lookingfor, page)
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
    )


if __name__ == '__main__':
    if os_name == 'posix':
        WSGIServer(app).run()
    else:
        app.run(debug=True)
