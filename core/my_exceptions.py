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


