"""A utility program to help extract rows from
Syngo ouput according to the CPT codes
of the procedures that the rows reprsent.
"""

import xlrd
import os
import xlwt

def get_code_groups():
    """
    Each sheet of the workbook represents a different output sheet.
    There is no functional difference between running this once with
    a code_groups.xls workbook with multiple sheets and running it
    multiple times on code_groups.xls workbooks with a single sheet each.

    In each sheet, each row represents a code combination.
    For example, the if the code_groups.xls sheet looks like:
    12345 22345
    32345
    the output will be an excel file that contains a sheet of
    all the rows that have CPT codes (12345 AND 22345) OR 32345
    (non-exclusive OR). If the last cpt code in a row is -99
    the row comes exclusive. So for example
    12345 22345 -99
    32345
    would match (12345 AND 22345 and ONLY these cpt codes) OR 32345.
    (See the "matches" function later in this file.)
    """
    code_groups_wb = xlrd.open_workbook('code_groups.xls')
    code_groups = {} #code_groups[sheet_name (a "group")][# of cpt code combinations][# of cpt codes in combination]
    for sheet in code_groups_wb.sheets():
        code_groups[sheet.name] = []
        for r in range(sheet.nrows):
            code_groups[sheet.name].append([])
            for c in range(sheet.ncols):
                if not sheet.cell(r,c).value == '': 
                    cpt = int(sheet.cell(r,c).value)
                    code_groups[sheet.name][-1].append(cpt)
    return code_groups


def find_input_file():
    files = os.listdir('.')
    for f in files:
        if f.split('.')[-1] == 'xls' and not f.split('.')[0] == 'code_groups':
            return f

def find_input_files():
    files = os.listdir('.')
    out = []
    for f in files:
        split = f.split('.')
        if split[-1] =='xls' and not split[0] == 'code_groups':
            out.append(f)
    return out

def is_subset(list1, list2):
    """Returns true if list 1 is a subset of list 2
    (assumes neither list has any repeats)
    """
    for item in list1:
        if not item in list2:
            return False
    return True

def same_contents(list1,list2):
    """Returns true if list 1 has the exact same
    contents as list 2. (assumes neither list has
    any repeats)
    """
    if not len(list1) == len(list2):
        return False
    return is_subset(list1,list2)

def matches(list1,list2):
    """Returns is_subset or same_contents
    depending on whether or not the last
    item in list1 is -99
    """
    if list1[-1] == -99:
        return same_contents(list1[:-1],list2)
    else:
        return is_subset(list1,list2)

def rdxf_to_wtxf(rdxf, rdbook):
    """Copied and adapted from the xlutils module
    rdxf - a xf object from a cell in an xlrd workbook
    rdbook - an xlrd workbook

    Returns: an xlwt style xf object
    """
    wtxf = xlwt.Style.XFStyle()
    #
    # number format
    #
    wtxf.num_format_str = rdbook.format_map[rdxf.format_key].format_str
    #
    # font
    #
    wtf = wtxf.font
    rdf = rdbook.font_list[rdxf.font_index]
    wtf.height = rdf.height
    wtf.italic = rdf.italic
    wtf.struck_out = rdf.struck_out
    wtf.outline = rdf.outline
    wtf.shadow = rdf.outline
    wtf.colour_index = rdf.colour_index
    wtf.bold = rdf.bold #### This attribute is redundant, should be driven by weight
    wtf._weight = rdf.weight #### Why "private"?
    wtf.escapement = rdf.escapement
    wtf.underline = rdf.underline_type #### 
    # wtf.???? = rdf.underline #### redundant attribute, set on the fly when writing
    wtf.family = rdf.family
    wtf.charset = rdf.character_set
    wtf.name = rdf.name
    # 
    # protection
    #
    wtp = wtxf.protection
    rdp = rdxf.protection
    wtp.cell_locked = rdp.cell_locked
    wtp.formula_hidden = rdp.formula_hidden
    #
    # border(s) (rename ????)
    #
    wtb = wtxf.borders
    rdb = rdxf.border
    wtb.left   = rdb.left_line_style
    wtb.right  = rdb.right_line_style
    wtb.top    = rdb.top_line_style
    wtb.bottom = rdb.bottom_line_style 
    wtb.diag   = rdb.diag_line_style
    wtb.left_colour   = rdb.left_colour_index 
    wtb.right_colour  = rdb.right_colour_index 
    wtb.top_colour    = rdb.top_colour_index
    wtb.bottom_colour = rdb.bottom_colour_index 
    wtb.diag_colour   = rdb.diag_colour_index 
    wtb.need_diag1 = rdb.diag_down
    wtb.need_diag2 = rdb.diag_up
    #
    # background / pattern (rename???)
    #
    wtpat = wtxf.pattern
    rdbg = rdxf.background
    wtpat.pattern = rdbg.fill_pattern
    wtpat.pattern_fore_colour = rdbg.pattern_colour_index
    wtpat.pattern_back_colour = rdbg.background_colour_index
    #
    # alignment
    #
    wta = wtxf.alignment
    rda = rdxf.alignment
    wta.horz = rda.hor_align
    wta.vert = rda.vert_align
    wta.dire = rda.text_direction
    # wta.orie # orientation doesn't occur in BIFF8! Superceded by rotation ("rota").
    wta.rota = rda.rotation
    wta.wrap = rda.text_wrapped
    wta.shri = rda.shrink_to_fit
    wta.inde = rda.indent_level
    # wta.merg = ????
    #
    return wtxf

def process_file(code_groups, input_file_name):
    print "Reading input file " + input_file_name + "..."
    rb = xlrd.open_workbook(input_file_name, formatting_info=True)
    print "Done."
    print "Processing..."
    rs = rb.sheet_by_index(1)
    #find the columns representing cpt codes
    header_row = [cell.value for cell in rs.row(0)]
    first_cpt_col = header_row.index('CPT1')
    last_cpt_col = first_cpt_col
    while last_cpt_col<rs.ncols and header_row[last_cpt_col][:3] == 'CPT':
        last_cpt_col = last_cpt_col +1
    last_cpt_col = last_cpt_col -1
    #find the cpt codes assocaited with each row
    row_cpts = []
    row_cpts.append([])#first row has no cpts
    for r in range(1,rs.nrows):
        cpts = []
        for c in range(first_cpt_col, last_cpt_col+1):
            try:
                cpts.append(int(rs.cell(r,c).value))
            except ValueError:
                break #stop the first time you come to an invalid cpt
        row_cpts.append(cpts)
    #for each group, find the rows of interest
    group_rows = {}
    for group_name, code_group in code_groups.iteritems():
        group_rows[group_name] =[0]#include the header in every group 
        for r in range(1,rs.nrows):
            for cpt_combo in code_group:
                #if the row matches any of the cpt combos, add it once
                if matches(cpt_combo, row_cpts[r]):
                    group_rows[group_name].append(r)
                    break
    #get the style for each column
    col_styles = []
    for c in range(rs.ncols):
        cell = rs.cell(1,c)
        rdxf = rb.xf_list[cell.xf_index]
        style = rdxf_to_wtxf(rdxf,rb)
        col_styles.append(style)
    return (group_rows, col_styles, rs)

def write_output(group_rows, col_styles, rs):
    #rs is the sheet
    #write the relevant rows
    wb = xlwt.Workbook()
    for group_name, row_numbers in group_rows.iteritems():
        s = wb.add_sheet(group_name)
        for out_r,in_r in enumerate(row_numbers):
            for c in range(rs.ncols):
                if in_r>0:
                    s.write(out_r,c,rs.cell(in_r,c).value, col_styles[c])
                else:
                    s.write(out_r,c,rs.cell(in_r,c).value)
    wb.save('output.xls')

def write_combined_output(triple_list):
    #takes a list of 3-tuples, (group_rows,col_styles,rs)
    #complicated way of merging output from several process_file runs
    wb = xlwt.Workbook()
    tracker = {}
    #col_styles = triple_list[0][1]
    for group_rows,col_styles, rs in triple_list:
        for group_name, row_numbers in group_rows.iteritems():
            if not group_name in tracker:
                tracker[group_name] = {'sheet':wb.add_sheet(group_name),
                                       'first_row':0}
            s = tracker[group_name]['sheet']
            for out_r,in_r in enumerate(row_numbers):
                for c in range(rs.ncols):
                    if in_r>0:
                        s.write(out_r + tracker[group_name]['first_row'],
                                c, rs.cell(in_r,c).value, col_styles[c])
                    else:#don't apply styles to the header row
                        s.write(out_r+tracker[group_name]['first_row'],
                                c, rs.cell(in_r,c).value)
            tracker[group_name]['first_row'] = 1+out_r+tracker[group_name]['first_row']
    wb.save('output.xls')

def main():
    print "Processing code groups file..."
    code_groups = get_code_groups()
    print "Done"
    print "Looking for input files..."
    in_file_names = find_input_files()
    triple_list = []
    for file_name in in_file_names:
        triple_list.append(process_file(code_groups,file_name))
    write_combined_output(triple_list)
    

if __name__ =='__main__':
    main()
