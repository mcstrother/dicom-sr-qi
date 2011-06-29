import mirqi.core.my_utils as my_utils
import os

class Report(object):
    def __init__(self, inquiries):
        self.inqs = inquiries

class Inquiry_Parameter(object):
    def __init__(self, default_value, label, description = ''):
        self.value = default_value
        self.label = label
        self.description = description

class Inquiry(object):
    def __init__(self, procs, context = None):
        """Initializer

        Should not be overridden in sublcasses
        """
        self.run(procs, context)

    @classmethod
    def get_parameters(cls):
        parameters = []
        for attr_name in dir(cls):
            if not attr_name[0] == '_'\
               and not hasattr(getattr(cls, attr_name), '__call__')\
               and not attr_name == "NAME":
                parameters.append(getattr(cls, attr_name))
        return parameters
        

    def run(self, procs, context):
        """Do all the necessary work with the data
        and save the stuff you need for the other methods
        """
        raise NotImplementedError()

    def get_table(self):
        """Return a list of lists which, when output as a table would
        be sufficient to allow someone to remake the figure returned
        by get_figure

        Ideally, this should be formatted so someone would be able
        to remake the figure almost instantly in excel
        """
        raise NotImplementedError()

    def get_figure(self):
        """Return a matplotlib figure

        This should only be called by self.get_figure_path, so
        if you would like to use some plotting library
        other than matplotlib, do not override this method.
        Just override get_figure_path
        """
        raise NotImplementedError()

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
        fig.savefig(fig_path)
        return fig_path
            
        








    
        
        
