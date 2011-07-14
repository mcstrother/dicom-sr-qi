import unittest
from mirqi.core import my_utils

class TestReadXML(unittest.TestCase):

    def setUp(self):
        self.procs, self.extra_procs = my_utils.get_procs('test')

    def test_attrs(self):
        self.assertEqual(self.procs[1].get_events()[0].Number_of_Pulses,31)

    def test_get_event_groups(self):
        proc = self.procs[1]
        event_groups = proc.get_event_groups(5)
        self.assertEqual(len(proc.get_events()), sum([len(x) for x in event_groups]),\
                         "proc.get_event_groups changes total number of events")
        expected_uids = [[u'0050'], [u'0051'], [u'0052', u'0053', u'0054'],\
                         [u'0055'], [u'0057'], [u'0058'], [u'0059', u'0060'],\
                         [u'0063'], [u'0066'], [u'0067'], [u'0070'], [u'0071'],\
                         [u'0072'], [u'0073'], [u'0076'], [u'0077'],\
                         [u'0078', u'0079', u'0080'], [u'0081'], [u'0082'],\
                         [u'0083', u'0084'], [u'0085', u'0086'], [u'0089'],\
                         [u'0090'], [u'0091'], [u'0092'], [u'0093'], [u'0094'],\
                         [u'0095'], [u'0098', u'0099'], [u'0102'], [u'0103'],\
                         [u'0106'], [u'0107'], [u'0108'],\
                         [u'0109', u'0110', u'0111', u'0112'], [u'0113'], \
                         [u'0114', u'0115'], [u'0116'], [u'0117'], [u'0118'],\
                         [u'0119'], [u'0122'], [u'0123'], [u'0126'], [u'0127'],\
                         [u'0128'], [u'0131'], [u'0132'], [u'0137', u'0138'],\
                         [u'0141'], [u'0142'], [u'0143'], [u'0144'], [u'0146'],\
                         [u'0147'], [u'0148', u'0149'], [u'0150'], [u'0153'],\
                         [u'0154'], [u'0155', u'0156'], [u'0157'],\
                         [u'0158', u'0159'], [u'0160'], [u'0161'], [u'0162'],\
                         [u'0163'], [u'0164'], [u'0165'], [u'0168'], [u'0171'],\
                         [u'0172'], [u'0173'], [u'0176'], [u'0179'],\
                         [u'0181', u'0182', u'0183'], [u'0185'], [u'0188']]
        for i, group in enumerate(event_groups):
            for j, event in enumerate(group):
                self.assertEqual(event.Irradiation_Event_UID[-4:],expected_uids[i][j])
        """expected = []
        for group in event_groups:
            uids = [e.Irradiation_Event_UID[-4:] for e in group]
            expected.append(uids)
        print repr(expected)"""
            
        """
        
        for group in event_groups:
            print "****"
            if len(group) == 1:
                print "Start time: " + str(group[0].DateTime_Started) + " End Time: " + str(group[0].get_end_time())
                continue
            for i, e in enumerate(group):
                if i == 0:
                    print "Begin: " + str(e.DateTime_Started)
                if not i > len(group)-2:
                    print "End : " + str(e.get_end_time()) + " Begin:" + str(group[i+1].DateTime_Started)
                if i == len(group)-1:
                    print "End: " +str(e.get_end_time())"""


