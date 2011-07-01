"""
This module provides methods for anonymizing DICOM-SR data
while attempting to preserve enough of the structure that it
remains useful for demo purposes.

== Usage ==

As a command-line script: python anonymize.py [path to input xml file] [path to output xml file]

From within another python program, simply use the "anonymize_sr" function.

"""

import xml.dom.minidom
import random
import datetime
import my_utils

class _Date_Randomizer(object):
    
    def __init__(self, first_date, last_date):
        day_change = datetime.timedelta(days=random.randint(-1000,1000))
        date_options = []
        one_day = datetime.timedelta(days =1)
        current_date = first_date + day_change
        last_date = last_date + day_change
        while current_date <= last_date:
            date_options.append(current_date)
            current_date += one_day
        self.date_options = date_options

    def get_date(self):
        """Pick a random date from the date optoins
        """
        return random.choice(self.date_options)

    def get_last_possible(self):
        return self.date_options[-1]

def _get_random_timeshift():
    """Return a random timedelta in [0, 24 hours].
    Randomized to seconds level
    """
    seconds = random.randrange(0, 86400) # 86400 = # of seconds in a day
    return datetime.timedelta(seconds = seconds)
    

def _anonymize_observer_context(element, new_serial_number,
                                new_Device_Observer_UID):
    element.setAttribute("Serial_Number", new_serial_number)
    element.setAttribute("Device_Observer_UID", new_Device_Observer_UID)
    element.setAttribute("Device_Observer_Name", "mirqi_anon")

def _get_new_Irradiation_Event_UID(acquisition_number, new_SeriesInstanceUID):
    c = int(new_SeriesInstanceUID[-5:])
    c = c + acquisition_number+1
    return new_SeriesInstanceUID[:-5] + str(c)

def _get_anonymized_comment(c_string, new_dts):
    dom = xml.dom.minidom.parseString(c_string)
    time = dom.getElementsByTagName("Time")[0]
    time.setAttribute("SRData", new_dts.strftime("%d-%b-%y %H:%M:%S"))#like 01-Jul-11 10:22:43
    return dom.toxml()

def _anonymize_ct_aquisition(element, acquisition_number,
                             new_SeriesInstanceUID,
                             timeshift, new_date):
    #Irradiation_Event_UID, Comment-->Time, DateTime_Started
    new_IEU = _get_new_Irradiation_Event_UID(acquisition_number, new_SeriesInstanceUID)
    element.setAttribute("Irradiation_Event_UID", new_IEU)
    #DateTime_Started
    dts = element.getAttribute("DateTime_Started")
    dts = my_utils.care_datetime_to_python_datetime(dts)
    dts = datetime.datetime.combine(new_date, dts.time())
    dts = dts + timeshift
    dts_str = my_utils.python_datetime_to_care_datetime(dts)
    element.setAttribute("DateTime_Started", dts_str)
    anon_comment = _get_anonymized_comment(element.getAttribute("Comment"), dts)
    element.setAttribute("Comment", anon_comment)
    

def _get_new_SeriesInstanceUID(new_device_observer_uid,
                              new_care_date):
    out = new_device_observer_uid + "500000" + str(new_care_date)
    out = out + "29364839485" + str(random.randrange(10000,99999))
    return out
    
def _get_new_StudyInstanceUID(new_care_date):
    arbitrary_beginning = "2.1.392.112344.212.09793965"
    arbitrary_ending = str(random.randrange(100000,999999))
    return arbitrary_beginning + new_care_date + arbitrary_ending

def _get_new_Device_Observer_UID(serial_number):
    arbitrary_beginning = "2.4.10.7.1008.6.2.6." # couldn't decode how these numbers were originally generated
    return arbitrary_beginning + str(serial_number)
 
def _anonymize_dose_info(element, date_randomizer):
    new_date = date_randomizer.get_date()
    new_care_date = my_utils.python_date_to_care_date(new_date)
    timeshift = _get_random_timeshift()
    new_patient_id = random.randrange(1000000,9999999)
    new_Serial_Number = "999999"
    new_Device_Observer_UID = _get_new_Device_Observer_UID(new_Serial_Number)
    new_SeriesInstanceUID = _get_new_SeriesInstanceUID(new_Device_Observer_UID,
                                                       new_care_date)
    new_StudyInstanceUID = _get_new_StudyInstanceUID(new_care_date)
    observer_context_element = element.getElementsByTagName("Observer_Context")[0]
    element.setAttribute("SeriesDate", new_care_date)
    element.setAttribute("StudyDate", new_care_date)
    #TODO: Probably want to set these times more intelligently
    element.setAttribute("SeriesTime","999999.999999")
    element.setAttribute("StudyTime","999999.999999")
    element.setAttribute("PatientID", unicode(new_patient_id))
    element.setAttribute("Gender", random.choice(["M","F"]))
    element.setAttribute("SeriesInstanceUID", new_SeriesInstanceUID)
    element.setAttribute("StudyInstanceUID", new_StudyInstanceUID)
    element.setAttribute("StudyDescription", "Redacted")
    element.setAttribute("Performing_Physician", "XX")
    _anonymize_observer_context(observer_context_element,
                                new_Serial_Number,
                                new_Device_Observer_UID)
    i = 0
    for element in element.getElementsByTagName("CT_Acquisition"):
        _anonymize_ct_aquisition(element, i, new_SeriesInstanceUID, timeshift, new_date)
        i +=1    
    
    
def anonymize_sr(xml_path, out_path):
    """
    Args:
        xml_path : path to a non-anonymized DICOM-SR file
        out_path : path to file where the output should be written
    """
    dom = xml.dom.minidom.parse(xml_path)
    query_criteria = dom.getElementsByTagName("Query_Criteria")
    dose_infos = dom.getElementsByTagName("DoseInfo")
    study_dates = [my_utils.care_date_to_python_date(e.getAttribute("StudyDate")) for e in dose_infos]
    first_date = min(study_dates)
    last_date = max(study_dates)
    date_randomizer = _Date_Randomizer(first_date, last_date)
    for element in dom.getElementsByTagName("Query_Criteria"):
        date_to = element.getAttribute("Query_Date_To")
        date_to = my_utils.care_date_to_python_date(date_to.replace('-',''))
        date_to += datetime.timedelta(days=2)
        element.setAttribute("Query_Date_To", date_to.strftime("%Y-%m-%d"))
    for element in dose_infos:
        _anonymize_dose_info(element, date_randomizer)

    
    with open(out_path, 'w') as out_file:
        out_str = dom.toxml("UTF-8")
        out_file.write(out_str)

import os
import sys
if __name__ == "__main__":
    in_path = os.path.abspath(sys.argv[1])
    out_path = os.path.abspath(sys.argv[2])
    anonymize_sr(in_path, out_path)

