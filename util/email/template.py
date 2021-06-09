import os
from pathlib import Path


BASE_DIR=Path(__file__).resolve().parent.parent.parent
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")


class Template:
    template_file = ""
    context = None

    def __init__(self, template_file=None, context = None, *args, **kwargs):
        self.template_file = template_file
        self.context = context
    def get_template(self):
        template_path = os.path.join(TEMPLATE_DIR, self.template_file)
        if not os.path.exists(template_path):
            raise Exception("This path does not exist")
        template_str= ""
        with open(template_path, 'r') as f:
            template_str = f.read()
        return template_str

    def render(self, context=None):
        render_context = context
        if self.context != None:
            render_context = self.context
        if not isinstance(render_context, dict):
            render_context = {}
        if not render_context:
            raise Exception("No context to render")
        template_string = self.get_template()
        return template_string.format(**render_context)
