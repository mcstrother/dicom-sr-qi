import my_utils
import my_exceptions

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

out = []
for row in table:
    out = out + [row]*30
plt.imshow(my_utils.transposed(out),interpolation='nearest')
plt.grid(True)
plt.title("Usage of BJH Room 812")
plt.xlabel("Day of week (Monday - Sunday)")
plt.ylabel("Time of Day (block number)")
plt.show()
