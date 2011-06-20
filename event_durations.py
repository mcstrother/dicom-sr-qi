import ReadXML
import my_utils
import csv


def make_table(event_list):
	table = [("Event ID","Duration","Fraction of Events", "Cumulative Exposure", "Pulse Rate")]
	cum_exposure = 0.0
	for i, event in enumerate(event_list):
		event_id = event.Irradiation_Event_UID
		duration = event.get_duration()
		fraction = float(i)/len(event_list)
		cum_exposure = cum_exposure + event.Exposure
		table.append((event_id, duration,fraction,cum_exposure,event.Pulse_Rate))
	return table

def main(bjh_procs, slch_procs):
	bjh_events = []
	for proc in bjh_procs:
		bjh_events = bjh_events + [e for e in proc.events if e.Irradiation_Event_Type == 'Fluoroscopy']
	slch_events = []
	for proc in slch_procs:
		slch_events = slch_events + [e for e in proc.events if e.Irradiation_Event_Type == 'Fluoroscopy']
	
	bjh_events.sort(key=lambda x:x.get_duration())
	slch_events.sort(key=lambda x:x.get_duration())
	
	bjh_table = make_table(bjh_events)
	slch_table = make_table(slch_events)
	
	my_utils.write_csv(bjh_table,'./bjh_out.csv')
	my_utils.write_csv(slch_table,'./slch_out.csv')
	
	return (bjh_events, slch_events)

def proc_frame_rate(bjh_procs):
	table = [("Start Time", "Average FPS")]
	bjh_procs = sorted([p for p in bjh_procs if len(p.events)>0], key = lambda x:x.get_start_time()) #sort and remove entries with no events
	for proc in bjh_procs:
		fps_list = [e.Pulse_Rate for e in proc.events if e.Irradiation_Event_Type == "Fluoroscopy"]
		if len(fps_list) == 0:
			continue
		else:
			average_fps = sum(fps_list)/len(fps_list)
		table.append((proc.get_start_time(), average_fps))
	for i in table:
		print str(i[0]) + ',' + str(i[1])
	
	
if __name__ == '__main__':
	bjh_procs = ReadXML.process_file(my_utils.BJH_XML_FILE, my_utils.BJH_SYNGO_FILES)
	slch_procs = ReadXML.process_file(my_utils.SLCH_XML_FILE, my_utils.SLCH_SYNGO_FILES)
	bjh_events, slch_events = main(bjh_procs, slch_procs)
	#proc_frame_rate(bjh_procs)
	proc_frame_rate(slch_procs)




