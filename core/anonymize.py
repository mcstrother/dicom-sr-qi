"""
This module provides methods for anonymizing DICOM-SR data
while attempting to preserve enough of the structure that it
remains useful for demo purposes.
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
    
 
def _anonymize_dose_info(element, date_randomizer):
    new_care_date = my_utils.python_date_to_care_date(date_randomizer.get_date())
    element.setAttribute("SeriesDate", new_care_date)
    element.setAttribute("StudyDate", new_care_date)
    timeshift = _get_random_timeshift()
    #TODO: Deal with SeriesTime and StudyTime
    new_patient_id = random.randrange(1000000,9999999)
    element.setAttribute("PatientID", unicode(new_patient_id))
    element.setAttribute("Gender", random.choice(["M","F"]))
    element.setAttribute("Performing_Physician", "XX")
    #TODO: Deal with SeriesInstanceUID, StudyInstanceUID
    
    
def anonymize_sr(xml_path, out_path):
    dom = parse(xml_path)
    query_criteria = dom.getElementsByTagName("Query_Criteria")
    dose_infos = dom.getElementsByTagName("DoseInfo")
    study_dates = [my_utils.care_date_to_python_date(e.getAttribute("StudyDate")) for e in dose_infos]
    first_date = min(study_dates)
    last_date = max(study_dates)
    date_randomizer = _Date_Randomizer(first_date, last_date)
    for element in dom.getElementsByTagName("Query_Criteria"):
        date_to = element.getAttribute("Query_Date_To")
        date_to = my_utils.care_date_to_python_date(date_to)
        date_to += datetime.timedelta(days=1)
        element.setAttribute("Query_Date_To", date_to)
    for element in dose_infos:
        _anonymize_dose_info(element, date_randomizer)

    
    with open(out_path, 'w') as out_file:
    dom.writexml(out_file)



