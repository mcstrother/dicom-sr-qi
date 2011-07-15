from srqi.core import my_utils
from srqi.gui import report_writer
import os
import matplotlib.pyplot as plt

class Inquiry_Parameter(object):
    def __init__(self, default_value, label, description = ''):
        self.value = default_value
        self.label = label
        self.description = description

    def set_value(self, new_value):
        self.value = new_value

import datetime
def get_standard_parameter(param_name):
    if param_name == "DATE_RANGE_START":
        return Inquiry_Parameter(datetime.date.today()-datetime.timedelta(days=365),
                                     "Date Range Start")
    elif param_name == "DATE_RANGE_END":
        return Inquiry_Parameter(datetime.date.today(), "Date Range End")
    else:
        raise ValueError("No such standard parameter " + param_name)

class Inquiry(object):
    description = "No description entered."
    
    def __init__(self, sr_procs, context = None, extra_procs = None):
        """Initializer

        Should not be overridden in sublcasses
        """
        if hasattr(self, 'DATE_RANGE_START'):
            sr_procs = [p for p in sr_procs if p.StudyDate >= self.DATE_RANGE_START.value]
            extra_procs = [p for p in extra_procs if p.get_start_date() >= self.DATE_RANGE_START.value]
        if hasattr(self, 'DATE_RANGE_END'):
            sr_procs = [p for p in sr_procs if p.StudyDate < self.DATE_RANGE_END.value]
            extra_procs = [p for p in extra_procs if p.get_start_date() < self.DATE_RANGE_END.value]
        self.run(sr_procs, context, extra_procs)

    @classmethod
    def get_parameters(cls):
        return [getattr(cls, name) for name in cls.get_parameter_names()]

    @classmethod
    def get_parameter_names(cls):
        """Get the names of all of the class attributes of type Inquiry_Parameter
        """
        names = []
        for attr_name in dir(cls):
            if type(getattr(cls, attr_name)) == Inquiry_Parameter:
                names.append(attr_name)
        return names

    def run(self, sr_procs, context, extra_procs):
        """Do all the necessary work with the data
        and save the stuff you need for the other methods

        Parameters:
            sr_procs - a list of ReadXML.Procedure objects representing sr
                reports for single procedures.
            context - a Context object. doesn't currently do anything, but
                is a placeholder for when we will need to pass context
                information from a broader database without giving it all the
                data from all the individual procedures in the national database
            extra_procs - a list of other types of objects (e.g.
                Syngo_Procedures) representing procedures that could not be
                associated with any of the sr procedures.
        """
        raise NotImplementedError("Inquiry.run must be overridden in implementing class")

    def get_tables(self):
        """Return an iterable of "tables", when output as a table would
        be sufficient to allow someone to remake the figure returned
        by get_figure

        A "table" is any iterable of iterables. So the return value of this
        function will most likely be a list of lists of lists of the form
        tables[table_number][row_number][column_number]

        Ideally, this should be formatted so someone would be able
        to remake the figure almost instantly in excel
        """
        return None

    def get_figures(self):
        """Return a matplotlib figure

        Note that many Inquries are expected to use matplotlib.pyplot,
        so when overriding this method one should be careful to avoid
        conflicts by doing one's plots in a new figure. In other words,
        the first line should almost always be fig = plt.figure().

        This should only be called by self.get_figure_path, so
        if you would like to use some plotting library
        other than matplotlib, do not override this method.
        Just override get_figure_path.
        """
        return None

    @classmethod
    def get_name(cls):
        """ Return cls.NAME if set, or a default otherwise.
        
        Defaults to cls.__name__ if there is no
        class attribute NAME specified in the subclass
        """
        if hasattr(Inquiry, 'NAME'):
            return unicode(cls.NAME)
        else:
            return unicode(cls.__name__)

    def get_figure_paths(self):
        """Save a figure and return its
        location

        Only override this method if you would like
        to use some plotting library other than matplotlib
        """
        figs = self.get_figures()
        if figs is None:
            return []
        paths = []
        for i, f in enumerate(figs):
            fig_name = unicode(self.__class__.__name__ + str(i) +'.png')
            fig_path = os.path.join(my_utils.get_output_directory(), fig_name)
            paths.append(fig_path)
            f.savefig(fig_path, dpi =100)
        return paths
            
        
    def get_text(self):
        """Return a text description of the inquiry results

        Returns None if not overwritten
        """
        return None

    @classmethod
    def get_description(cls):
        """Return a text description of the inquiry, the requirements
        to run it, the output, etc.
        """
        return cls.description

    @classmethod
    def get_parameter_text(cls):
        """Return a text description of the values of the parameters of the run
        """
        out = ''
        param_names = cls.get_parameter_names()
        for name in param_names:
            param = getattr(cls, name)
            out += param.label + ': ' + str(param.value) +'\n'
        return out
            
        

def inquiry_main(inq_cls, proc_set = 'test'):
    procs, extra_procs = my_utils.get_procs(proc_set)
    inq = inq_cls(procs, extra_procs = extra_procs)
    report_writer.write_report([inq])


    
        
        
