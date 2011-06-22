import my_utils
import csv
import my_exceptions

DAYS_PER_PERIOD = 7

def build_table():
    procs = my_utils.get_procs()
    procs = [x for x in procs if len(x.events)>0]

    first_time = min(procs, key = lambda x: x.get_start_time()).get_start_time()
    last_start_time = max(procs, key = lambda x: x.get_start_time()).get_start_time()
    num_periods = int((last_start_time - first_time).days/DAYS_PER_PERIOD)

    attending_table = {}
    for proc in procs:
        try:
            proc.get_syngo()
        except my_exceptions.DataMissingError:
            continue
        attending = proc.get_syngo().RAD1.replace(',','')
        if not attending in attending_table:
                attending_table[attending] = {}
        period_number = int((proc.get_start_time() - first_time).days/DAYS_PER_PERIOD)
        if not period_number in attending_table[attending]:
            attending_table[attending][period_number] =[]
        for event in proc.events:
            if event.Irradiation_Event_Type == "Fluoroscopy":
                attending_table[attending][period_number].append(event)
    return (attending_table, num_periods)

def write_csv(attending_table, num_periods):
    num_attendings = len(attending_table.keys())

    heading = ['']
    heading = heading + [attending for attending in sorted(attending_table.keys())]
    out =[heading]
    event_counts = [heading]
    for w in range(num_periods):
        row = [w]
        event_row = [w]
        for a,attending in enumerate(sorted(attending_table.keys())):
            if w in attending_table[attending]:
                row.append(my_utils.average_fps(attending_table[attending][w]))
                event_row.append(len(attending_table[attending][w]))
            else:
                row.append('')
                event_row.append(0)
        out.append(row)
    with open('temp.csv','wb') as f:
        csv.writer(f).writerows(out)

def remove_attendings(table,num_periods):
    """Remove attendings for whom we don't
    have enough data
    """
    """
    #Remove attendings who have less than half of the number
    #of events of the attending with the most events
    most_events = 0
    for attending in table.keys():
        event_num = 0
        for period in table[attending].keys():
            event_num = event_num + len(table[attending][period])
        if event_num > most_events:
            most_events = event_num
    for attending in table.keys():
        event_num = 0
        for period in table[attending].keys():
            event_num = event_num + len(table[attending][period])
        if event_num <most_events/2:
            del table[attending]
            """
    
    for attending in table.keys():
        if len(table[attending].keys()) < num_periods/2: #must work at least every other period
            del table[attending]        
    

import matplotlib.pyplot as plt
def plot(table,num_periods):
    num_attendings = len(table.keys())
    for a,attending in enumerate(sorted(table.keys())):
        plt.subplot(num_attendings, 1, a)
        plt.axis([0,num_periods,5,15])
        plt.xlabel('Period Number')
        plt.ylabel('Average FPS')
        plt.title(attending)
        x = []
        y = []
        s = []
        for period,events in table[attending].iteritems():
            x.append(period)
            y.append(my_utils.average_fps(events))
            s.append(len(events))
        plt.scatter(x,y,s=s, label=attending)
        plt.plot(x,y, color='red')
    plt.show()



if __name__ == '__main__':
    table, num_periods = build_table()
    remove_attendings(table, num_periods)
    write_csv(table, num_periods)
    plot(table,num_periods)
    



