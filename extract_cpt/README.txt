== Usage Instructions ==
Ensure enthought python distribution is installed

extract_cpt.py must be alone in a folder with:
1) "code_groups.xls"
2) one other .xls file (not .xlsx), which will be the input file
3) optionally, this README file

= input .xls file =

Sheet 2 of the input .xls file must have a columns labeled "CPT1", "CPT2", etc.
Rows from sheet 2 will be copied into the output file.

= code_groups.xls =

Each sheet in code_groups.xls will correspond to a sheet of ouput.
A row of the input file will be copied into a row of the output file if it matches ANY of the rows in code_groups.xls.
A row of input is considered to "match" a row in code_groups.xls if ALL of the cpt codes in the code_groups row are found in the input row. **If the last value in the code_groups row is -99**, the input row matches the code_groups row if it contains ALL of the cpt codes in the code_groups row and ONLY the cpt codes in the code groups row.

