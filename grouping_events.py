import my_utils
import matplotlib.pyplot as plt

def pause_histogram(procs):
    """Make a histogram of the pauses between events.
    (Events longer than 15 seconds are excluded)
    """
    out = []
    for proc in procs:
        events = proc.valid_events()
        events.sort(key=lambda x: x.DateTime_Started)#should just be a linear time check 
        for i,e in enumerate(events):
            if i+1 < len(events):
                out.append(events[i+1].DateTime_Started - e.get_end_time())
    h_data = plt.hist([my_utils.total_seconds(t) for t in out], range=(0,15))
    print h_data[1]
    plt.show()

def plot_histo(frames_of_groups,exposure_times_of_groups, durations_of_groups):
    print "=== Frames ==="
    plt.figure(1)
    n, bins, patches = plt.hist(frames_of_groups, range=(0,200))
    plt.title("Number of Frames Per Event Group in SLCH and BJH 812")
    plt.ylabel("Count")
    plt.xlabel("Number of Frames")
    print n
    print bins
    print "=== Durations ==="
    plt.figure(2)
    n, bins, patches = plt.hist([my_utils.total_seconds(d) for d in durations_of_groups])
    print n
    print bins
    plt.title("Durations of Event Groups in SLCH and BJH 812")
    plt.ylabel("Count")
    plt.xlabel("Durations (seconds)")
    print "=== Exposure Times ==="
    plt.figure(3)
    n, bins, patches = plt.hist([my_utils.total_seconds(d) for d in exposure_times_of_groups])
    print n
    print bins
    plt.title("Exposure Times of Event Groups in SLCH and BJH 812")
    plt.ylabel("Count")
    plt.xlabel("Exposure Times (seconds)")
    plt.show()

import datetime
MIN_PAUSE = datetime.timedelta(seconds=4.5)
def grouped_event_histogram(procs):
    """Don't know why this isn't working, but
    it doesn't seem to be.
    """
    #build the list of groups
    groups = []
    total_events = 0
    for proc in procs:        
        events = proc.valid_events()
        total_events = total_events + len(events)
        events.sort(key=lambda x: x.DateTime_Started)#should just be a linear time check 
        group = []
        for e in events:
            if len(group) == 0:
                group.append(e)
            elif (e.DateTime_Started - group[-1].get_end_time()) < MIN_PAUSE:
                group.append(e)
            else:
                groups.append(list(group))
                group = [e]
    print len(groups)
    print total_events
    #extract data of interest
    frames_of_groups = []
    durations_of_groups = []
    for group in groups:
        frames = 0
        duration = datetime.timedelta(0)
        for event in group:
            frames = frames + e.Number_of_Pulses
            duration = duration + e.get_duration()
        frames_of_groups.append(frames)
        durations_of_groups.append(duration)
    print frames_of_groups
    plot_histo(frames_of_groups,durations_of_groups)


    
def grouped_event_histogram2(procs):
    frames_of_groups = []
    exposure_times_of_groups = []
    durations_of_groups = []
    total_events = sum([len(p.events) for p in procs])
    print "Total number of events: " + str(total_events)
    for proc in procs:
        if len(proc.events) == 0:
            continue
        events = proc.valid_events()
        events.sort(key=lambda x: x.DateTime_Started)
        for i,e in enumerate(events):
            if i ==0:
                frames = e.Number_of_Pulses
                exposure_time = e.get_duration()
                start_time = e.DateTime_Started
            elif e.DateTime_Started - events[i-1].get_end_time() < MIN_PAUSE:
                frames = frames + e.Number_of_Pulses
                exposure_time = exposure_time + e.get_duration()#doesn't count duration of pauses
            else:
                frames_of_groups.append(frames)
                exposure_times_of_groups.append(exposure_time)
                duration = events[i-1].get_end_time()-start_time
                if duration < datetime.timedelta(0):
                    print e.Irradiation_Event_UID
                durations_of_groups.append(events[i-1].get_end_time()-start_time)
                start_time = e.DateTime_Started
                frames = e.Number_of_Pulses
                exposure_time = e.get_duration()
        duration = events[i].get_end_time()-start_time
        if duration < datetime.timedelta(0):
            print e.Irradiation_Event_UID
        durations_of_groups.append(duration)
        frames_of_groups.append(frames)
        exposure_times_of_groups.append(exposure_time)
    print "Total number of groups: " + str(len(frames_of_groups))
    return(frames_of_groups, exposure_times_of_groups, durations_of_groups)
    #plot_histo(frames_of_groups, exposure_times_of_groups, durations_of_groups)
    


    
        
if __name__ == '__main__':
    procs = my_utils.get_procs('all')
    procs = [p for p in procs if p.is_valid()]
    #pause_histogram(procs)
    histo_data = grouped_event_histogram2(procs)
    plot_histo(*histo_data)
    
