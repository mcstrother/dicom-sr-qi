import my_utils
import Parse_Syngo
import xlrd, xlwt
import datetime

PAIR_FILE_NAME = "code_pairs.xls"
EXCUSIVE_CODE = -99

def get_code_pairs(in_file_name):
    code_pairs_wb = xlrd.open_workbook(in_file_name)
    code_pairs = {}
    for sheet in code_pairs_wb.sheets():
        code_pairs[sheet.name] = {}
        code_pairs[sheet.name]['separation'] = datetime.timedelta(days = float(sheet.cell(0,1).value))
        code_pairs[sheet.name]['combo1'] = [int(x.value) for x in sheet.row(1)[1:]]
        code_pairs[sheet.name]['combo2'] = [int(x.value) for x in sheet.row(2)[1:]]
    return code_pairs

import os
def get_syngo_file_names():
    files = os.listdir('.')
    out = []
    for f in files:
        split = f.split('.')
        if split[-1] =='xls' and not split[0] == 'code_pairs':
            out.append(f)
    return out

procs = Parse_Syngo.parse_syngo_files(get_syngo_file_names())
procs.sort(key= lambda x:x.dos)#sort procs by start time
cps = get_code_pairs(PAIR_FILE_NAME)

out = {}
for sheet_name, spec in cps.iteritems():
    combo1_matches = [x for x in procs if my_utils.matches(spec['combo1'],x.cpts)]
    combo2_matches = [x for x in procs if my_utils.matches(spec['combo2'],x.cpts)]
    lookup = {}#comob2_matches sorted by mpi
    for proc in combo2_matches:
        if not proc.mpi in lookup:
            lookup[proc.mpi] =[]
        lookup[proc.mpi].append(proc)
    out[sheet_name] = []
    for proc in combo1_matches:
        if not proc.mpi in lookup:
            continue
        for proc2 in lookup[proc.mpi]:
            if proc2.dos > proc.dos and (proc2.dos -proc.dos) < spec['separation']:
                out[sheet_name].append(proc)
                out[sheet_name].append(proc2)


Parse_Syngo.write_syngo_file('output.xls',out )                    

