class DataMissingError(Exception):
    """Raised when an attempt is made to
    access missing data. A subset of "NoDataError"
    but isn't (yet) actually a subclass
    """
    pass

class DataMismatchError(Exception):
    """Thrown when an attempt is made to group
    data in an invalid way. For example, thrown by
    Procedure.set_syngo if the Syngo_Procedure_Data
    object that is passed in does not seem to correspond
    to the procedure object.
    """
    pass


class BadInquiryError(Exception):
    """Thrown when someone has made a mistake while
    writing an inquiry.
    """

class UnmetRequirementError(Exception):
    """Raised when attempting to run an inquiry with insufficient data
    """

class AbsentDataTypeError(UnmetRequirementError):
    """Raised when atempting to run an inquiry without inputting any of a required data type (e.g. sr Procedures, Syngo data, etc)
    """

    def __init__(self, data_class, *args):
        self.data_class = data_class
        message = "Inquiry requires " + str(data_class) + "procedure data in order to run."
        UnmetRequirementError.__init__(self, message) 


