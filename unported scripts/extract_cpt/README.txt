= Purpose =
Suppose you have a spreadsheet of data like extract_cpt_example.xls. (It will probably help to open the file and look at it now.) Each row represents a procedure. Each procedure has a bunch of CPT codes listed in columns labeled CPT1, CPT2, etc. The program in this folder is a stand-alone script that helps extract rows into a separate spreadsheet according to their CPT codes.



= Usage Instructions =

== Installation ==
This program does not depend on the rest of the srqi module, but it does require that you have the Enthought Python distribution installed.

(Alternatively, if you only want to use this script, you can opt to only install the xlrd and xlwt modules, which are available for free online if you don't want to use all of Enthought.)

== Set Up == 
extract_cpt.py must be alone in a folder with:
1) an excel file called "code_groups.xls" (create this file now)
2) at least one other .xls file (not .xlsx), formatted as described below, which will be the input file (you will copy this from wherever you keep your data)
3) optionally, this README file

== Demo ==

This script comes ready to go. If you don't like reading instructions, just double click "extract_cpt.py" and see what happens. If it worked, an output.xls file should be created. Look through it and the other files in the folder and see if you can get a sense of what is going on.

Note: If you have a file called output.xls in your folder when you run the script, it will be overwritten.

== input .xls file ==

Sheet 2 of the input .xls file must have a columns labeled "CPT1", "CPT2", etc.
There are no other requirements for this file. 
REMEMBER: .xls, NOT .xlsx! The data has to be on SHEET 2! (The 2nd sheet from the left as the tabs appear on the bottom of the open .xls file in excel.) Not sheet 1!
Rows from sheet 2 will be copied into the output file.

== code_groups.xls ==

Each sheet in code_groups.xls will correspond to a sheet of ouput.

A row of the input file will be copied into a row of the output file if it matches ANY of the rows in code_groups.xls.

A row of input is considered to "match" a row in code_groups.xls if ALL of the cpt codes in the code_groups row are found in the input row.

**If the last value in the code_groups row is -99**, the input row matches the code_groups row if it contains ALL of the cpt codes in the code_groups row and ONLY the cpt codes in the code groups row.

