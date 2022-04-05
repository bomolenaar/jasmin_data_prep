#!usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys

infolder = sys.argv[1]
outfolder = sys.argv[2]

textfilter_path = '/vol/tensusers4/bmolenaar/jasmin_data_prep/string_norm/text_filter.py'

if infolder == outfolder:
    outfolder = outfolder[:-1] + '_filtered/'

if os.path.isdir(outfolder):
    os.system(f"rm -r {outfolder}")
os.mkdir(outfolder)

infolder_new = '.' + infolder[:-1] + '_unfiltered/'
if os.path.isdir(infolder_new):
    os.system(f"rm -r {infolder_new}")

file_lst = []
for dirpath, dirnames, filenames in os.walk(infolder):
    for file in filenames:
        if '.ort' or '.prompt' in file:
            file_lst.append(file)

for file in file_lst:
    os.system(f"python3 {textfilter_path} {infolder}{file} {outfolder}{file}")

os.system(f"mv {infolder} {infolder_new}")
os.system(f"mv {outfolder} {infolder}")
