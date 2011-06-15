import my_utils
import Parse_Syngo
import xlrd, xlwt
import datetime

INPUT_FILE_NAME = "code_pairs.xls"
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


procs = Parse_Syngo.parse_syngo_files(my_utils.BJH_SYNGO_FILES)
procs.sort(key= lambda x:x.dos)#sort procs by start time
cps = get_code_pairs(INPUT_FILE_NAME)

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
                out[sheet_name].append((proc,proc2))
                    
wb = xlwt.Workbook()
for sheet_name, pairs in out.iteritems():
    s = wb.add_sheet(sheet_name)
    for i, pair in enumerate(pairs):
        s.write(i,0,pair[0].acc)
        s.write(i,1,pair[1].acc)
wb.save('output.xls')
