""""
@Author:        Bo Molenaar
@Date:          3 June 2022

@Lastedited:    16 March 2023

This script performs text_filter.py for a given input folder 
and stores filtered output to given output folder.
Optionally you can select to use text_filter_no-unk.py with opt -u False or --unk=False

Expected input: 1) folder to read files from, 2) folder to place output, 
3) extension of files to read, 4) optional -u or --unk flag
"""

#!usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import getopt
import ast
from multiprocessing import Pool
from subprocess import run

UNK = True
indir = sys.argv[1]
outdir = sys.argv[2]
filetype = sys.argv[3]
argv = sys.argv[4:]

try:
    opts, args = getopt.getopt(argv, "u:", ["unk="])
except getopt.GetoptError as err:
    print(err)
    opts = []

for opt, arg in opts:
    if opt in ["-u", "--unk"]:
        UNK = ast.literal_eval(unk)


def filter_file(myzip):
    os.nice(19)
    textfilter_path, infile, outfile = myzip
    filter_cmd = f"python3 {textfilter_path} {infile} {outfile}"
    run(filter_cmd, shell=True, check=True)


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
            if filetype in file:
                file_lst.append(file)
    args_zip_list = []

    # make a temp dir to put the text filter output if infolder name = outfolder name
    if infolder == outfolder:
        outfolder = outfolder[:-1] + '_filtered/'

        if os.path.isdir(outfolder):
            shutil.rmtree(outfolder)
        os.mkdir(outfolder)

        # handle archiving of original files > indir_unfiltered
        infolder_archive = ""
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
            infile = os.path.join(infolder, file)
            outfile = os.path.join(outfolder, file)
            args_zip_list.append((textfilter_path, infile, outfile))
        with Pool(32) as pool:
            pool.map(filter_file, args_zip_list)

        # make outdir name = indir name
        os.system(f"mv {infolder} {infolder_archive}")
        os.system(f"mv {outfolder} {infolder}")

    else:
        if os.path.isdir(outfolder):
            shutil.rmtree(outfolder)
        os.mkdir(outfolder)

        # run the filter for each file in indir
        for file in file_lst:
            infile = os.path.join(infolder, file)
            outfile = os.path.join(outfolder, file)
            args_zip_list.append((textfilter_path, infile, outfile))
        with Pool(32) as pool:
            pool.map(filter_file, args_zip_list)


string_norm(indir, outdir, UNK)
