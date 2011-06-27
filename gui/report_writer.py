import os.path as path
import jinja2
import mirqi

def _get_report_template():
    TEMPLATE_FOLDER = path.join(mirqi.gui.__path__[0], 'templates')
    TEMPLATE_NAME = 'report.html'
    template_path = path.join(TEMPLATE_FOLDER,TEMPLATE_NAME)
    with open(template_path, 'r') as f:
        temp_string = f.read()
    return jinja2.Template(temp_string)


def write_report(inqs):
    OUTPUT_FOLDER = mirqi.__path__[0]
    OUTPUT_NAME = 'output.html'
    output_path = path.join(OUTPUT_FOLDER, OUTPUT_NAME)
    template = _get_report_template()
    with open(output_path, 'w') as f:
        f.write(template.render(inquiries= inqs))


