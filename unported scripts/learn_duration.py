import my_utils
import numpy as np

def least_squares(t_procs, v_procs):
    lookup = {}#maps a CPT code on to an int
    for proc in t_procs:
        for cpt in proc.get_cpts():
            lookup[cpt] = None
    for i,cpt in enumerate(sorted(lookup.keys())):
        lookup[cpt] = i
    #build the arrays for np.linalg.lstsq
    b = np.zeros(len(t_procs))
    a = np.zeros([len(t_procs),len(lookup)])
    for i,proc in enumerate(t_procs):
        for cpt in proc.get_cpts():
            a[i][lookup[cpt]]=1
        b[i] = my_utils.total_seconds(proc.get_duration())
    soln, residues, rank, s = np.linalg.lstsq(a,b)
    for i,cpt in enumerate(sorted(lookup.keys())):
        print str(cpt) +',' + str(soln[i])

    error_list = []
    skipped_count = 0
    for proc in v_procs:
        vect = np.zeros(len(lookup))
        try:
            for cpt in proc.get_cpts():
                vect[lookup[cpt]] = 1
        except KeyError:
            skipped_count = skipped_count +1
            continue #cpt code appears in validation but not training set. can't make a prediction
        prediction = np.dot(vect, soln)
        reality = my_utils.total_seconds(proc.get_duration())
        error_list.append(abs(prediction-reality))
    error_list.sort()
    print error_list
    print np.median(error_list)
    print "Skipped " + str(skipped_count)

def split_procs(procs, valid_frac = .2):
    """Split the procedures into a
    training and validation set based
    on start time
    """
    procs.sort(key = lambda x: x.get_start_time())
    split_ind = int((1-valid_frac) *len(procs))
    training = procs[:split_ind]
    validation = procs[split_ind:]
    return (training, validation)


def main():
    procs = my_utils.get_procs('bjh')
    has_all_data = lambda x: x.has_syngo() and x.has_events()
    procs = [p for p in procs if has_all_data(p)]
    t_procs, v_procs = split_procs(procs)
    least_squares(t_procs, v_procs)

if __name__ == '__main__':
    main()
    
