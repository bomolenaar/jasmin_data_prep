#!usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys

infolder = sys.argv[1]
outfolder = sys.argv[2]

if infolder == outfolder:
    outfolder = outfolder[:-1] + '_filtered'

file_lst = []
for dirpath, dirnames, filenames in os.walk(infolder):
    for file in filenames:
        if '.ort' or '.prompt' in file:
            file_lst.append(file)

print(file_lst)
