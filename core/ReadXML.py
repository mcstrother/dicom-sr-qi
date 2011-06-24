"""Given xml data from CARE, create Procedure and Event
python objects for further processing.
"""
from xml.dom import minidom
import datetime
import my_utils
import numbers
import my_exceptions


class Event(object):
        FLOAT_ATTRS = ['Positioner_Primary_Angle',
                       'Pulse_Rate',
                       'Number_of_Pulses',
                       'Positioner_Secondary_Angle'] #attrs that are pure floats in the xml and will be used as such
        STRING_ATTRS = ['Acquisition_Protocol',
                        'Irradiation_Event_UID',
                        'Target_Region',
                        'Fluoro_Mode',
                        'Acquisition_Plane_in_Irradiation_Event',
                        'Irradiation_Event_Type'] #attrs that are pure strings
        SPLIT_FLOAT_ATTRS = ['Exposure_Time',
                             'Table_Lateral_Position',
                             'Pulse_Width',
                             'Table_Height_Position',
                             'Exposure','Focal_Spot_Size',
                             'Dose_Area_Product',
                             'Dose_RP',
                             'Distance_Source_to_Detector',
                             'KVP',
                             'Distance_Source_to_Isocenter',
                             'X-Ray_Tube_Current',
                             'Table_Longitudinal_Position'] #attrs that are stored in the xml as a float value, then a space, then a unit of measurement
        OTHER_ATTRS = ['Reference_Point_Definition',
                       'Comment',
                       'DateTime_Started']
        
        
        def __init__(self, aquisition_element, syngo=None):
                self.syngo = syngo
                ae = aquisition_element
                #store DateTime_Started as python datetime
                started_str = ae.attributes['DateTime_Started'].value
                self.DateTime_Started = my_utils.care_datetime_to_python_datetime(started_str) #datetime(int(started_str[:4]),int(started_str[4:6]),int(started_str[6:8]),int(started_str[8:10]),int(started_str[10:12]), int(started_str[12:14]))
                #init attrs from the xml
                for attr in self.STRING_ATTRS:
                        try:
                                setattr(self, attr, ae.attributes[attr].value)
                        except KeyError:
                                setattr(self, attr, None)
                for attr in self.FLOAT_ATTRS:
                        setattr(self, attr, float(ae.attributes[attr].value))
                for attr in self.SPLIT_FLOAT_ATTRS:
                        value, unit = ae.attributes[attr].value.split(' ')
                        value = float(value)
                        setattr(self, attr.replace('-','_'), value)
                        setattr(self, attr.replace('-','_')+"_units", unit)
                self._parse_comment(ae.attributes["Comment"].value)
                if self.is_valid(): #if not, self._get_number_of_pulses tends to fail due to bad data
                        old_pulses = self.Number_of_Pulses
                        self.Number_of_Pulses = self._get_number_of_pulses()
        
        def _parse_comment(self, comment):
                """Get data hidden within the "Comment" attribute of the
                CT_Aquisition element
                """
                dom = minidom.parseString(comment)
                iiDiameter_element = dom.getElementsByTagName("iiDiameter")[0]
                self.iiDiameter = float(iiDiameter_element.attributes['SRData'].value)
                
        
        def get_duration(self):
                if self.Number_of_Pulses == 1:
                        return datetime.timedelta(0)
                else:
                        seconds =(self.Number_of_Pulses -1)/self.Pulse_Rate
                        return datetime.timedelta(seconds= seconds)
        
        def _check_number_of_pulses(self):
                if not self.Number_of_Pulses == 512:
                        if not int(self.Number_of_Pulses) == self._get_number_of_pulses():
                                print 'Problem:' + str(self.Number_of_Pulses) +',' +str(self._get_number_of_pulses())
                                print self.Irradiation_Event_UID
                                return False
                return True
        
        def _get_number_of_pulses(self):
                """Compute the number of pulses as Exposure_Time/Pulse_Width.
                Used because the DICOM-SR reports as of time of writing max out
                the reported number of pulses at 512.
                
                Used to correct self.Number_of_Pulses on initialization
                and usually not afterwards.
                """
                if not self.Exposure_Time_units == self.Pulse_Width_units:
                        raise NotImplementedError("Expected Exposure Time and Pulse Width unites to be the same. Need to implement unit converstion.")
                num_pulses = self.Exposure_Time / self.Pulse_Width
                return int(round(num_pulses))
        
        def is_valid(self):
                """Does several sanity checks on the event. Returns
                False if data in the event appears nonsensical (e.g.
                negative values for things that can't possibly be
                negative).

                Method is a work in progress, so it isn't guaranteed
                to return False if the event is invalid in a way
                that isn't being checked for yet.
                """
                out = True
                out = out and (self.Number_of_Pulses >=0)
                out = out and (self.Exposure >0)
                out = out and (self.Pulse_Width >= 0)
                if not out: #have to check if we can terminate yet, since the next checks require the previous checks to have passed, or else they will throw exceptions
                        return False
                return out
        
        def get_end_time(self):
                return self.DateTime_Started + self.get_duration()

        def get_start_time(self):
                return self.DateTime_Started
                        
class Procedure(object):
        DATE_ATTRS = ['SeriesDate', 'StudyDate']
        OTHER_ATTRS = ['SeriesTime','StudyTime', 'PatientID']
        FLOAT_ATTRS = []
        STRING_ATTRS = ['Gender',
                        'SeriesInstanceUID',
                        'StudyInstanceUID',
                        'Scope_of_Accumulation',
                        'SeriesDescription',
                        'StudyDescription',
                        'Performing_Physician']
        
        IVRFU_CPT = "-99999"
        
        
        def __init__(self, dose_info_element, syngo =None):
                die = dose_info_element
                self._events = [Event(aquisition_element) for aquisition_element in dose_info_element.getElementsByTagName('CT_Acquisition')]
                #store PatientID as an int unless it absolutely needs to be a string
                try:
                        self.PatientID = int(die.attributes['PatientID'].value)
                except ValueError as ve:
                        self.PatientID = str(die.attributes['PatientID'].value)
                for attr in self.DATE_ATTRS:
                        setattr(self, attr, my_utils.care_date_to_python_date(die.attributes[attr].value))
                for attr in self.FLOAT_ATTRS:
                        setattr(self, attr, float(die.attributes[attr].value))
                for attr in self.STRING_ATTRS:
                        try:
                                setattr(self, attr, die.attributes[attr].value)
                        except KeyError:
                                setattr(self, attr, None)
                self._syngo = None
                if syngo:
                        self.add_syngo(syngo)

        def get_events(self, valid = True):
                """Return the radiation events in the procedure

                By default, only returns valid events.
                Guaranteed to run in contant time, except for the first
                run through, which is linear
                """
                if not hasattr(self, '_valid_events_cache'):
                        self._valid_events_cache = [e for e in self._events if e.is_valid()]
                return self._valid_events_cache
                
        
        def valid_events(self):
                """DEPRECATED"""
                return [e for e in self._events if e.is_valid()]
                
        def get_duration(self):
                """Returns a python datetime.timedelta of
                the duration of the procedure
                """
                return self.get_end_time() - self.get_start_time()
        
        def get_start_time(self):
                """Returns a python datetime of the start
                of the first event of in the procedure
                """
                if len(self._events) == 0:
                        raise my_exceptions.DataMissingError("Procedure has no radiation events.")
                first_event = min(self._events, key = lambda x:x.DateTime_Started)
                return first_event.DateTime_Started
        
        def get_end_time(self):
                """Returns a python datetime of the end
                of the last event in the procedure
                """
                if len(self._events) == 0:
                        raise my_exceptions.DataMissingError("Procedure has no radiation events.")
                last_event = max(self._events, key = lambda x:x.DateTime_Started)
                return last_event.get_end_time()
        
        def get_cpts(self):
                """Returns cpts as a string with codes
                separated by commas
                """
                if self._syngo == None:
                        raise my_exceptions.DataMissingError("Procedure object has no syngo data")
                else:
                        return self._syngo.cpts
        
        def is_valid(self):
                """Does several sanity checks on the procedure. Returns
                False if data in the event appears nonsensical (e.g.
                negative values for things that can't possibly be
                negative)"""
                return True
        
        def is_real(self):
                """Returns whether the data likely represents
                a real procedure, as opposed to a test run or broken data
                """
                out = True
                out = out and (self.Gender in ['M','F'])
                out = out and isinstance(self.PatientID, numbers.Integral)
                out = out and self.is_valid()
                return out
                
        def set_syngo(self,syngo =None):
                """Stores the syngo after checking
                to make sure it really corresponds. Raises
                DataMismatchError if self and syngo
                do not correspond.
                """
                if not syngo:
                        self._syngo = None
                        return
                if not self.PatientID == syngo.mpi:
                        raise my_exceptions.DataMismatchError("Procedure and Syngo_Procedure_Data have different patient ids")
                if not self.StudyDate == syngo.dos_start:
                        raise my_exceptions.DataMismatchError("Procedure and Syngo_Procedure_Data have different study dates")
                try:
                        #check that there isn't more than an hour dispairity between start times
                        if my_utils.total_seconds(abs(self.get_end_time() - syngo.get_end())) > 7200:
                                raise my_exceptions.DataMismatchError("Procedure and Syngo_Procedure_data end times differ by more than two hours")
                except my_exceptions.DataMissingError as dme:
                        pass #if you can't do the check, you can't do the check
                self._syngo = syngo

        def get_syngo(self):
                if not self._syngo:
                        raise my_exceptions.DataMissingError("Procedure object has no syngo data")
                return self._syngo

        def has_syngo(self):
                return not self._syngo is None
        
        def get_number_of_pulses(self):
                """Return the total number of pulses (aka frames)
                of radiation used in the procedure. (Includes
                non-fluoro events
                """
                return sum([e.Number_of_Pulses for e in self.get_events()])

        def get_event_groups(self, separation):
                """Gets a list of events grouped by their timing.

                Gets a list of events groups. The end of the ith
                event in each group occurs no more than `separation`
                seconds before the beginning of the (i+1)th event
                Args:
                        separation: maximum number of seconds by which events
                                in a group may be separated.
                Returns:
                        A list of tuples of events.
                """
                out = []
                group = []
                for e in self.get_events():
                        if len(group) == 0:
                                group.append(e)
                        elif my_utils.total_seconds(e.DateTime_Started - group[-1].get_end_time())<= separation:
                                group.append(e)
                        else:
                                out.append(tuple(group))
                                group = [e]
                out.append(tuple(group))
                return out

        def is_pure(self):
                """Test if procedure has all data and seems real

                Use this for when you just want a program to run and you
                don't much care about catching odd looking procedures
                """
                out = self.has_syngo() and self.is_real() and len(self.get_events()) >0
                return out

def add_syngo_to_procedures(procs, syngo_procs):
        """Matches procedure information from DICOM-SR (procs)
        to procedure information from Syngo files (syngo_procs)
        according to the patient ID number and the start date
        of the procedure
        """
        lookup = {}
        for sproc in syngo_procs:
                if not (sproc.mpi, sproc.dos_start) in lookup:
                        lookup[(sproc.mpi, sproc.dos_start)] = []
                lookup[(sproc.mpi, sproc.dos_start)].append(sproc)
        for proc in procs:
                try:
                        sproc_list = lookup[(proc.PatientID,proc.StudyDate)]
                except KeyError: #can't find the procedure in the lookup
                        proc.set_syngo(None)
                        continue
                for sproc in sproc_list:
                        try:
                                proc.set_syngo(sproc)
                        except my_exceptions.DataMismatchError as dme:
                                #print "Rejected match for " + str(sproc.MPI) + ', ' + str(sproc.get_end()) +". Doesn't match " + str(proc.get_end_time()) 
                                continue#TODO: currently justs checks for "good enough" match. can change this to look for "best match" in sproc_list
                
        
                
import Parse_Syngo
                
def process_file(xml_file_name, cpt_file_names):
        """Use xml file to generate Procedure and Event objects.
        
        """
        xmldoc = minidom.parse(xml_file_name)
        procedures = [Procedure(dose_info_element) for dose_info_element in xmldoc.getElementsByTagName('DoseInfo')]
        syngo_procs = Parse_Syngo.parse_syngo_files(cpt_file_names)
        add_syngo_to_procedures(procedures, syngo_procs)
        return [proc for proc in procedures if proc.is_real()] 
                
        
