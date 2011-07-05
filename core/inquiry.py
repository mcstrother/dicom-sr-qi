from mirqi.core import my_utils
from mirqi.gui import report_writer
import os
import matplotlib.pyplot as plt

class Report(object):
    def __init__(self, inquiries):
        self.inqs = inquiries

class Inquiry_Parameter(object):
    def __init__(self, default_value, label, description = ''):
        self.value = default_value
        self.label = label
        self.description = description

    def set_value(self, new_value):
        self.value = new_value

class Inquiry(object):
    def __init__(self, sr_procs, context = None, extra_procs = None):
        """Initializer

        Should not be overridden in sublcasses
        """
        self.run(sr_procs, context, extra_procs)

    @classmethod
    def get_parameters(cls):
        return [getattr(cls, name) for name in cls.get_parameter_names()]

    @classmethod
    def get_parameter_names(cls):
        names = []
        for attr_name in dir(cls):
            if not attr_name[0] == '_'\
               and not hasattr(getattr(cls, attr_name), '__call__')\
               and not attr_name == "NAME":
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

    def get_table(self):
        """Return a list of lists which, when output as a table would
        be sufficient to allow someone to remake the figure returned
        by get_figure

        Ideally, this should be formatted so someone would be able
        to remake the figure almost instantly in excel
        """
        raise None

    def get_figure(self):
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
        raise None

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

    def get_figure_path(self):
        """Save a figure and return its
        location

        Only override this method if you would like
        to use some plotting library other than matplotlib
        """
        fig = self.get_figure()
        fig_name = unicode(self.__class__.__name__ + '.png')
        fig_path = os.path.join(my_utils.get_output_directory(), fig_name)
        fig.savefig(fig_path, dpi =100)
        return fig_path
            
        
    def get_text(self):
        """Return a text description of the inquiry results

        Returns None if not overwritten
        """
        return None


def inquiry_main(inq_cls, proc_set = 'test'):
    procs, extra_procs = my_utils.get_procs('slch')
    inq = inq_cls(procs, extra_procs = extra_procs)
    report_writer.write_report([inq])




    
        
        
