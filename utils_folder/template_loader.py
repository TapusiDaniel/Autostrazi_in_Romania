def load_template(template_name):
    """Load a template file from the templates directory."""
    with open(f'templates/{template_name}.html', 'r', encoding='utf-8') as f:
        return f.read()