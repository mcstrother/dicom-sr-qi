import ReadXML
import my_utils
import datetime

def main():
	bjh_procs = ReadXML.process_file(my_utils.BJH_XML_FILE, my_utils.BJH_SYNGO_FILES)
	slch_procs = ReadXML.process_file(my_utils.SLCH_XML_FILE, my_utils.SLCH_SYNGO_FILES)
	procs = bjh_procs #+ slch_procs
	
	events_by_rad = {}
	for proc in procs:
		if proc.syngo == None:
			continue
		rad = proc.syngo.RAD1
		if not rad in events_by_rad:
			events_by_rad[rad] = []
		for event in proc.events:
			events_by_rad[rad].append(event)
	print "Last Name,First Initial,Average FPS,Average Duration,Total # of Events"
	for rad, events in events_by_rad.iteritems():
		fluoro_events = [e for e in events if e.Irradiation_Event_Type =="Fluoroscopy"]
		total_fluoro_time = sum([e.get_duration() for e in fluoro_events],datetime.timedelta(0) )
		average_fps = my_utils.total_seconds(sum([my_utils.multiply_timedelta(e.get_duration(),e.Pulse_Rate) for e in fluoro_events], datetime.timedelta(0)))/my_utils.total_seconds(total_fluoro_time)
		average_duration = sum([e.get_duration() for e in fluoro_events],datetime.timedelta(0))/len(fluoro_events)
		print rad + ',' + str(average_fps) +',' +str(average_duration) +','+ str(len(fluoro_events))
	
	print "*******"
	for rad, events in events_by_rad.iteritems():
		fluoro_events = [e for e in events if e.Irradiation_Event_Type == "Fluoroscopy"]
		
		number_max = len([e for e in fluoro_events if e.Number_of_Pulses == 512])
		print rad + ',' + str(average_duration) + ',' + str(number_max) + ',' + str(len(fluoro_events))


if __name__ == '__main__':
	main()