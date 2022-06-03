#!usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys

""""
@Author:    Bo Molenaar
@Date:      3 June 2022

This script performs text_filter.py for a given input folder and stores filtered output to given output folder.
"""

infolder = sys.argv[1]
outfolder = sys.argv[2]

# location of text_filter.py by Cristian Tejedor Garcia
textfilter_path = '/vol/tensusers4/bmolenaar/jasmin_data_prep/string_norm/text_filter.py'

# make a temp dir to put the text filter output
if infolder == outfolder:
    outfolder = outfolder[:-1] + '_filtered/'

if os.path.isdir(outfolder):
    os.rmdir(outfolder)
os.mkdir(outfolder)

# handle archiving of original files > indir_unfiltered
if infolder.split('/')[1] != "":
    infolder_fields = infolder.split('/')
    infolder_new = "/".join(infolder_fields[:-2]) + "/." + infolder_fields[-2] + "_unfiltered"
elif infolder.split("/")[1] == "":
    infolder_new = '.' + infolder[:-1] + '_unfiltered/'

# start with a clean indir_unfiltered
if os.path.isdir(infolder_new):
    os.rmdir(infolder_new)

# get files from indir to be filtered
file_lst = []
for dirpath, dirnames, filenames in os.walk(infolder):
    for file in filenames:
        if '.ort' or '.prompt' or '.awd' in file:
            file_lst.append(file)

# run the filter for each file in indir
for file in file_lst:
    os.system(f"python3 {textfilter_path} {infolder}{file} {outfolder}{file}")

# make outdir name = indir name
os.system(f"mv {infolder} {infolder_new}")
os.system(f"mv {outfolder} {infolder}")
