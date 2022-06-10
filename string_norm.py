#!usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import getopt

""""
@Author:        Bo Molenaar
@Date:          3 June 2022

@Lastedited:    10 June 2022

This script performs text_filter.py for a given input folder and stores filtered output to given output folder.
Optionally you can select to use text_filter_no-unk.py with opt -u False or --unk=False
"""

unk = True
infolder = sys.argv[1]
outfolder = sys.argv[2]
argv = sys.argv[3:]

try:
    opts, args = getopt.getopt(argv, "u:", ["unk="])
except getopt.GetoptError as err:
    print(err)
    opts = []

for opt, arg in opts:
    if opt in ["-u", "--unk"]:
        unk = eval(arg)


def string_norm(infolder, outfolder, use_unk):
    # location of text_filter.py by Cristian Tejedor Garcia
    if not use_unk:
        textfilter_path = '/vol/tensusers4/bmolenaar/jasmin_data_prep/string_norm/text_filter_no-unk.py'
    else:
        textfilter_path = '/vol/tensusers4/bmolenaar/jasmin_data_prep/string_norm/text_filter.py'

    # get files from indir to be filtered
    file_lst = []
    for dirpath, dirnames, filenames in os.walk(infolder):
        for file in filenames:
            if '.ort' or '.prompt' or '.awd' in file:
                file_lst.append(file)

    # make a temp dir to put the text filter output if infolder name = outfolder name
    if infolder == outfolder:
        outfolder = outfolder[:-1] + '_filtered/'

        if os.path.isdir(outfolder):
            shutil.rmtree(outfolder)
        os.mkdir(outfolder)

        # handle archiving of original files > indir_unfiltered
        if infolder.split('/')[1] != "":
            infolder_fields = infolder.split('/')
            infolder_archive = "/".join(infolder_fields[:-2]) + "/." + infolder_fields[-2] + "_unfiltered"
        elif infolder.split("/")[1] == "":
            infolder_archive = '.' + infolder[:-1] + '_unfiltered/'

        # start with a clean indir archive
        if os.path.isdir(infolder_archive):
            shutil.rmtree(infolder_archive)
        os.mkdir(infolder_archive)

        # run the filter for each file in indir
        for file in file_lst:
            os.system(f"python3 {textfilter_path} {infolder}{file} {outfolder}{file}")

        # make outdir name = indir name
        os.system(f"mv {infolder} {infolder_archive}")
        os.system(f"mv {outfolder} {infolder}")

    else:
        if os.path.isdir(outfolder):
            shutil.rmtree(outfolder)
        os.mkdir(outfolder)

        # run the filter for each file in indir
        for file in file_lst:
            os.system(f"python3 {textfilter_path} {infolder}{file} {outfolder}{file}")


string_norm(infolder, outfolder, unk)
