"""Extracts  pairs of procedures from Syngo files.

The original motivation for this script is searching for
placments and removals of central lines. In this context,
a "pair" of procedures is a placement and a removal. 

Takes at least 3 input files:
 - "code_pairs.xls" - gives cpt codes defining the first and second member
     of each code pair
 - "reasons_lookup.xls" - a table of accession numbers and "reasons" for the
    second member of each pair (e.g. a central line was removed due to
    infection or due to the line no longer being needed)
 - any number of input files from Syngo

When extracting pairs, this script assumes that all "placements" must
be followed by a removal before another placement can occur (i.e. a patient
can only have one of a single line type in at a time) and that
we may be missing data from procedures that occurred off site. Thus if the
input file has the following pattern of procedures for a single
patient over time (p-placement, r-removal): R1 P1 P2 R2 R3 P3, only
one pair will be extracted, P2-R2. It is assumed that we are missing
a placement before R1, a removal after P1, a placement before R3, and
the final removal (or the patient still has a line in).

"""
#allow imports of standard srqi modules
import os, sys
srqi_containing_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.getcwd())))
sys.path.append(srqi_containing_dir)
from srqi.core import my_utils, Parse_Syngo
import xlrd, xlwt
import datetime

PAIR_FILE_NAME = "code_pairs.xls"
REASON_FILE_NAME = "reasons_lookup.xls"
EXCUSIVE_CODE = -99

def get_code_pairs(in_file_name):
    code_pairs_wb = xlrd.open_workbook(in_file_name)
    code_pairs = {}
    for sheet in code_pairs_wb.sheets():
        code_pairs[sheet.name] = {}
        code_pairs[sheet.name]['separation'] = datetime.timedelta(days = float(sheet.cell(0,1).value))
        code_pairs[sheet.name]['combo1'] = [my_utils.standard_cpt(x.value) for x in sheet.row(1)[1:] if x.value ==0 or x.value]
        code_pairs[sheet.name]['combo2'] = [my_utils.standard_cpt(x.value) for x in sheet.row(2)[1:] if x.value==0 or x.value]
    return code_pairs

import os
def get_syngo_file_names():
    files = os.listdir('.')
    out = []
    for f in files:
        split = f.split('.')
        if split[-1] =='xls' and not f == PAIR_FILE_NAME and not f == REASON_FILE_NAME and not f =='output.xls':
            out.append(f)
    return out

def get_reasons_lookup():
    reason_wb = xlrd.open_workbook(REASON_FILE_NAME)
    reasons_lookup = {}
    for sheet in reason_wb.sheets():
        for r in range(1,sheet.nrows):
            if sheet.cell(r,0).value:
                accession = int(sheet.cell(r,0).value)
            else:
                accession = None
            reason = str(sheet.cell(r,1).value)
            reasons_lookup[accession] = reason
    reasons_lookup[None] = ''
    return reasons_lookup

import xlwt
def write_out(sdict, reasons_lookup):
    file_name = "output.xls"
    wb = xlwt.Workbook()
    date_xf = xlwt.easyxf(num_format_str='MM/DD/YYYY')
    time_xf = xlwt.easyxf(num_format_str='HH:MM:SS')
    datetime_xf = xlwt.easyxf(num_format_str='MM/DD/YYYY HH:MM:SS')
    for sheet_name, slist in sdict.iteritems():
            sheet = wb.add_sheet(sheet_name)
            if len(slist) ==0:
                    continue
            for i,heading in enumerate(slist[0].get_heading_list() + ["Line Days","Removal reason"]):
                    sheet.write(0,i,heading)
            for r,syngo in enumerate(slist):
                    for c,data in enumerate(syngo.get_data_list()):
                            xf=None
                            if isinstance(data, datetime.date):
                                    xf = date_xf
                            elif isinstance(data, datetime.time):
                                    xf = time_xf
                            elif isinstance(data, datetime.datetime):
                                    xf = datetime_xf
                            if xf:
                                    sheet.write(r+1,c,data, xf)
                            else:
                                    sheet.write(r+1,c,data)
                    #take on the line days
                    c = c+1
                    if r %2 == 1: # row represents the removal part of a pair
                        line_days = (syngo.dos_start - slist[r-1].dos_start).days
                        sheet.write(r+1,c,line_days)
                    #tack on the removal reason
                    c=c+1
                    if syngo.acc in reasons_lookup:
                        reason = reasons_lookup[syngo.acc]
                    else:
                        reason = ''
                    sheet.write(r+1,c,reason)
    wb.save(file_name)

def dos_time_sort_comparator(c1, c2, s, s2):
    """Used in main() as a key to sort syngo
    procedures by dos_time, without choking
    on procedures where dos_time is None and putting
    c2s before c1s if they ocurred within 2 hours of
    each other
    """
    date_delta = s.dos_start - s2.dos_start
    if date_delta == datetime.timedelta(0):
        # if either lacks a time or if the times are close to each other
        # return so that the c2 match occurs before the c1 match
        if s.dos_time and s2.dos_time:
            time_diff = my_utils.subtract_times(s.dos_time, s2.dos_time)
            if abs(time_diff) > datetime.timedelta(hours = 2):
                return int(my_utils.total_seconds(time_diff))
        # if you're here, either one time is missing or the times are within
        # 2 hours of each other on the same day, so use the cpt codes to
        # break the tie
        if my_utils.matches(c2,s.cpts):
            return -1
        elif my_utils.matches(c2, s2.cpts):
            return 1
        else:
            return 0
    else:
        return int(date_delta.days)

def main():
    procs = Parse_Syngo.parse_syngo_files(get_syngo_file_names())
    procs.sort(key= lambda x:x.dos_start)#sort procs by start time
    cps = get_code_pairs(PAIR_FILE_NAME)
    reasons_lookup = get_reasons_lookup()
    out = {}
    for sheet_name, spec in cps.iteritems():
        c1 = spec['combo1']#shorthand
        c2 = spec['combo2']
        #keep only procs that match either c2 or c1
        matches = [x for x in procs if my_utils.matches(spec['combo1'],x.cpts)\
                   or my_utils.matches(spec['combo2'],x.cpts)]
        lookup = my_utils.organize(matches, lambda x:x.mpi)
        pairs = []
        for mpi, matches in lookup.iteritems():
            matches.sort(cmp = lambda x,y: dos_time_sort_comparator(spec['combo1'], spec['combo2'],x,y))
            c1_match = None # a "placement" is a c1 match, just easier to think of as a placement
            for p in matches:
                if my_utils.matches(c1, p.cpts):
                    c1_match = p
                elif c1_match:
                    if (p.dos_start-c1_match.dos_start) > spec['separation']: # too far
                        c1_match = None
                    elif c1_match and my_utils.matches(c2,p.cpts): # found a match
                        pairs.append((c1_match, p))
                        c1_match =None
        out[sheet_name] = pairs

    #order the pairs so the ones without reasons come last
    for sheet_name in out.keys():
        has_reason = []
        no_reason = []
        for pair in out[sheet_name]:
            if pair[1].acc in reasons_lookup:
                has_reason.append(pair)
            else:
                no_reason.append(pair)
        out[sheet_name] = has_reason+no_reason

    #flatten the pair lists for the purposes of writing
    for key,pairs in out.iteritems():
        out[key] = sum([list(pair) for pair in pairs],[])

    write_out(out, reasons_lookup)                   

if __name__ == '__main__':
    main()
    
