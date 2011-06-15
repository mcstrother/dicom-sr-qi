"""Create a heat map of room usage by day of the week.
Divides the day up into chunks of RESOLUTION seconds
"""
import my_utils
import my_exceptions
import csv

def add_period(table,weekday, start_seconds,end_seconds):
    """table[weekday][block]
    start_seconds and end_seconds are ints
    """
    first_block = int(start_seconds/RESOLUTION)
    last_block = int((end_seconds-1)/RESOLUTION)
    for block in range(first_block, last_block+1):
        table[weekday][block] = table[weekday][block] +1


# divide the day into blocks of RESOLUTION seconds
RESOLUTION = 600 
num_blocks = 24*60*60 / RESOLUTION # if day isn't evenly divisible, last block will be slightly longer
table = []#might switch this to numpy array if it turns out to be slow
for i in range(7):
    table.append([0]*num_blocks)
#table[weekday][block]
procs = my_utils.get_procs('bjh')
for proc in procs:
    try:
        start_time= proc.get_start_time()
    except my_exceptions.DataMissingError:
        continue
    start_seconds = (start_time.hour * 60 + start_time.minute)*60
    end_time = proc.get_end_time()
    end_seconds = (end_time.hour * 60 + end_time.minute)*60
    if start_time.weekday() == end_time.weekday():
        add_period(table,start_time.weekday(), start_seconds,end_seconds)
    elif (start_time.weekday()+1)%7 == end_time.weekday():
        add_period(table,start_time.weekday(),start_seconds,86400)#86400= number of seconds in a day
        add_period(table,end_time.weekday(),0,end_seconds)
    else:
        raise RuntimeError("This should not have happened")


import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import datetime

a = np.array(table)
my_utils.write_csv(my_utils.transposed(table))
fig = plt.figure()
ax = fig.add_subplot(111)
cax = ax.matshow(a.transpose(), cmap=cm.get_cmap('gray_r'), aspect='auto')
max_count = a.max()
cbar = fig.colorbar(cax, ticks = [0,int(max_count/3), int((max_count*2)/3), max_count])
cbar.set_label("Number of Procedures")
plt.grid(False)
"""
#TODO: Figure out how to make time labels for different resolutions
new_labels = [0]
for t in range(8):
    s = t*num_blocks/8
    seconds = s*RESOLUTION
    hours = int(seconds/3600)
    minutes = int((seconds -hours*3600)/60)
    seconds = int(seconds - (hours*60+minutes)*60)
    new_labels.append(str(datetime.time(hour=hours,minute=minutes,second=seconds)))"""

#TODO: Figure out this labeling thing at all. This isn't working
old_labels = [0,0,20,40,60,80,100,120,140]
new_labels = []
for x in old_labels:
        seconds = x*RESOLUTION
        hours = int(seconds/3600)
        minutes = int((seconds -hours*3600)/60)
        seconds = int(seconds - (hours*60+minutes)*60)
        new_labels.append(str(datetime.time(hour = hours, minute = minutes, second=seconds)))
plt.gca().set_yticklabels(new_labels)
plt.gca().set_xticklabels(['','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
plt.title("Usage of BJH Room 812")
plt.xlabel("Day of week (Monday - Sunday)")
plt.ylabel("Time of Day (block number)")
plt.show()
