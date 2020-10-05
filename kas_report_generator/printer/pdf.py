import os
from typing import Dict, Any
from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from jinja2 import Template
from . import TEMPLATE_DIR

def read_template(name: str) -> Template:
    fpath = str(TEMPLATE_DIR.joinpath(name))
    with open(fpath, 'r') as fp:
        return Template(fp.read())

class PDF(object):

    def __init__(self, variables: Dict[str, Any]):
        self.html_template: Template = read_template('template.html') 
        self.css_template: Template = read_template('styler.css') 
        self.variables: Dict[str, Any] = variables

    @property
    def html(self) -> str:
        return self.html_template.render(**self.variables)

    @property
    def css(self) -> str:
        return self.css_template.render(**self.variables)

    def write_pdf(self, name):
        font_config = FontConfiguration()
        html = HTML(string=self.html)
        css = CSS(string=self.css, font_config=font_config)

        html.write_pdf(name, stylesheets=[css],
                       font_config=font_config)

    @classmethod
    def write(cls, path: str, vars: Dict[str, Any] = {}):
        pdf = cls(vars)
        pdf.write_pdf(path)