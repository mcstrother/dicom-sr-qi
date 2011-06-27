import my_utils


class Report(object):
    def __init__(self, inquiries):
        self.inqs = inquiries


class Inquiry(object):
    def __init__(self, procs, context = None):
        self.run(procs, context)

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

        """
        raise NotImplementedError()

    def get_name(self):
        """ Return a name as a unicode object
        """
        raise NotImplementedError()








    
        
        
