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
    if lookingfor in page.text:
        found_templates.append(page)
    for sub_template in page.templates(content=True):
        if lookingfor in sub_template.text:
            found_templates.append(sub_template)
    return found_templates


@app.route('/' if os_name != 'posix' else '/whichsub/')
def main():
    code = request.args.get('code', 'en')
    family = request.args.get('family', 'wikipedia')
    pagetitle = request.args.get('pagetitle', '')
    lookingfor = request.args.get('lookingfor', '')
    site = pwb.Site(code, family)
    try:
        page = pwb.Page(site, pagetitle)
        templates = find_sub_templates(lookingfor, page)
    except ValueError:
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
