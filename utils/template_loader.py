from string import Template


def load_template(template_name):
    """Load a template file from the templates directory."""
    with open(f"templates/{template_name}.html", "r", encoding="utf-8") as f:
        return f.read()


def render_template(template_name, **context):
    """Render a template with $-style placeholders."""
    template = Template(load_template(template_name))
    return template.safe_substitute(**context)
