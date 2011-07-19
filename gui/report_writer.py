import os.path as path
import jinja2
import srqi
from srqi.core import my_utils
from srqi.core import srdata


def _get_report_template():
    TEMPLATE_FOLDER = path.join(srqi.gui.__path__[0], 'templates')
    TEMPLATE_NAME = 'report.html'
    template_path = path.join(TEMPLATE_FOLDER,TEMPLATE_NAME)
    with open(template_path, 'r') as f:
        temp_string = f.read()
    return jinja2.Template(temp_string)


def write_report(inqs):
    OUTPUT_FOLDER = srqi.core.my_utils.get_output_directory()
    OUTPUT_NAME = 'output.html'
    output_path = path.join(OUTPUT_FOLDER, OUTPUT_NAME)
    template = _get_report_template()
    with open(output_path, 'w') as f:
        f.write(template.render(inquiries= inqs))

import os

class Report_Writer(object):
    _default_out_dir = srqi.core.my_utils.get_output_directory()
    _default_out_path = path.join(_default_out_dir,
                                 'output.html')
    _default_template_folder = path.join(srqi.gui.__path__[0], 'templates')
    _default_template_path = path.join(_default_template_folder,'report.html')

    def __init__(self, data_paths, inquiry_classes):
        self.data_paths = data_paths
        self.procs, self.extra_procs = my_utils.get_procs_from_files(data_paths)
        self.inqs = [cls(self.procs, extra_procs = self.extra_procs) for cls in inquiry_classes]

    def _update_data(self, data_paths):
        """Make self.procs reflect the data in data_paths

        If data_paths is None or if data_paths is the same as
        self.data_paths then no update is needed so nothing is done.

        returns True if an update was actually needed
        """
        if data_paths and not my_utils.same_contents(self.data_paths, data_paths):
            #new data paths
            self.data_paths = data_paths
            self.procs, self.extra_procs = my_utils.get_procs_from_files(data_paths)
            return True
        else:
            return False
        
    def _update_inquiry_objects(self, inquiry_classes, data_changed):
        """Rebuild self.inqs from inquiry_classes

        TODO: if not data_changed, find some way to look for overlap
        between the inquries that will be generated and the inquiries
        that we have already generated to avoid repeating analyses
        """
        self.inqs = [cls(self.procs, extra_procs = self.extra_procs) for cls in inquiry_classes]

    def update(self, data_paths = None, inquiry_classes = None):
        data_changed = self._update_data(data_paths)
        self._update_inquiry_objects(inquiry_classes, data_changed)
                 

    def _get_template(self, template_path):
        with open(template_path, 'r') as f:
            temp_string = f.read()
        return jinja2.Template(temp_string)

    def write(self, template_path = _default_template_path,
              output_path = _default_out_path):
        template = self._get_template(template_path)
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path))
        with open(output_path, 'w') as f:
            f.write(template.render(inquiries= self.inqs))
        
        



