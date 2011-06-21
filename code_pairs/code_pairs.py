import my_utils
import Parse_Syngo
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
        code_pairs[sheet.name]['combo1'] = [my_utils.standard_cpt(x.value) for x in sheet.row(1)[1:]]
        code_pairs[sheet.name]['combo2'] = [my_utils.standard_cpt(x.value) for x in sheet.row(2)[1:]]
    return code_pairs

import os
def get_syngo_file_names():
    files = os.listdir('.')
    out = []
    for f in files:
        split = f.split('.')
        if split[-1] =='xls' and not f == PAIR_FILE_NAME and not f == REASON_FILE_NAME:
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
            for i,heading in enumerate(slist[0].get_heading_list() + ["Removal reason"]):
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
                    #tack on the removal reason
                    if syngo.acc in reasons_lookup:
                        reason = reasons_lookup[syngo.acc]
                    else:
                        reason = ''
                    sheet.write(r+1,c+1,reason)
    wb.save(file_name)


procs = Parse_Syngo.parse_syngo_files(get_syngo_file_names())
procs.sort(key= lambda x:x.dos_start)#sort procs by start time
cps = get_code_pairs(PAIR_FILE_NAME)
reasons_lookup = get_reasons_lookup()

out = {}
for sheet_name, spec in cps.iteritems():
    c1 = spec['combo1']#shorthand
    c2 = spec['combo2']
    matches = [x for x in procs if my_utils.matches(spec['combo1'],x.cpts)\
               or my_utils.matches(spec['combo2'],x.cpts)]
    lookup = my_utils.organize(matches, lambda x:x.mpi)
    pairs = []
    for mpi, matches in lookup.iteritems():
        c1_match = None # a "placement" is a c2 match, just easier to think of as a placement
        for p in matches:
            if my_utils.matches(c1, p.cpts):
                c1_match = p
            elif my_utils.matches(c2,p.cpts) and c1_match:
                pairs.append((c1_match, p))
                c1_match =None
    out[sheet_name] = pairs

#flatten the pair lists for the purposes of writing
for key,pairs in out.iteritems():
    out[key] = sum([list(pair) for pair in pairs],[])

write_out(out, reasons_lookup)                   

