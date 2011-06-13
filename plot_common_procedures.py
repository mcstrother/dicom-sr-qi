import ReadXML
import my_utils


def build_table(procs):
    """ Return table[cpt_codes][attending]
    """
    table = {}
    for proc in procs:
        cpt_string = proc.get_cpts()
        if not cpt_string in table:
            table[cpt_string] ={}
        if not proc.get_syngo().RAD1 in table[cpt_string]:
            table[cpt_string][proc.get_syngo().RAD1] = []
        table[cpt_string][proc.get_syngo().RAD1].append(proc)
    return table

def sorted_cpts(table):
    """Return a list of cpt codes sorted by frequency
    so output[0] is the most common cpt code combination
    """
    cpts = table.keys()
    freq_table = {}
    for cpt_string, attending_table in table.iteritems():
        freq = 0
        for p_list in attending_table.values():
            freq = freq + len(p_list)
        freq_table[cpt_string] = freq
    print sorted(freq_table.values())
    sorted(cpts, key = lambda x: freq_table[x], reverse = True)
    return cpts

import matplotlib.pyplot as plt
def plot_cpts(table, cpt_list):
    """Make box plots of the numbe of frames
    used in each procedure by each attending
    """
    for i, cpt in enumerate(cpt_list):
       plt.figure(i)
       plt.title(cpt)
       plt.xlabel('Attending')
       plt.ylabel('Number of Frames')
       data = []
       for attending in sorted(table[cpt].keys()):
           procs = table[cpt][attending]
           data.append([proc.get_number_of_pulses() for proc in procs])
    plt.boxplot(data)
    plt.setp(plt.gca(),'xticklabels',sorted(table[cpt].keys()))
    plt.show()

def main():
    procs = my_utils.get_procs('bjh')
    procs = [x for x in procs if x.has_syngo()]
    table = build_table(procs)
    cpts = sorted_cpts(table)
    plot_cpts(table, [u'36556,76937,77001'])
    

if __name__ == '__main__':
    main()
