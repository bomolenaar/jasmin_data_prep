#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys
import pandas as pd

"""
@Author:    Bo Molenaar
@Date:      3 June 2022

This script is used to move all .wav and .ort files from their respective directories to a composite directory
for each file type. Wav files are also split into test and train dirs based on speaker id.
Which speakers are assigned to test is gathered from a .txt file supplied by the user. All others are moved to train.
"""

if (len(sys.argv) < 7):
    print(
        "You must add 6 arguments: a file specifying test speakers, locations of comp-q G1-1, G1-2 and comp-p G1 data, a folder name for generating the files and the root path to this project folder")
    sys.exit(-1)

speakerfile = sys.argv[1]
qG1_1 = sys.argv[2]
qG1_2 = sys.argv[3]
pG1 = sys.argv[4]
collection = sys.argv[5]
project_folder = sys.argv[6]

# make a list of dirs to pull files from
data_dirs = [os.path.join(project_folder, qG1_1), os.path.join(project_folder, qG1_2), os.path.join(project_folder, pG1)]
# declare dirs to move files to
test_dir = os.path.join(project_folder, collection, 'wav_files_to_use_test/')
train_dir = os.path.join(project_folder, collection, 'wav_files_to_use_train/')
trans_dir = os.path.join(project_folder, collection, 'manual_transcriptions/')


def make_rec_set(recs1, recs2):
    """"
    Merges 2 rec_to_use.txt files from different JASMIN speaker subsets.
    Optionally outputs a new rec_to_use.txt into your composite directory.
    """
    recs1_df = pd.read_table(recs1, header=None)
    recs2_df = pd.read_table(recs2, header=None)
    rec_set = recs1_df.merge(recs2_df, how="outer")
    # comment line below if you don't need to store a copy of the merged speaker list
    rec_set.to_string(os.path.join(collection, 'rec_to_use.txt'), header=None, index=None)
    return rec_set


# merge recs to use from both subsets
recs = make_rec_set(os.path.join(qG1_1, 'rec_to_use.txt'), os.path.join(pG1, 'rec_to_use.txt'))
# make a list of speakers in merged recs set
name_lst = []
for value in recs.itertuples():
    name_lst.append(value._1)

# get speaker ids from supplied file
test_speakers = [line.strip('\n') for line in open(speakerfile, 'r').readlines()]

print(f"Moving {len(test_speakers)} test speakers...")
print(f"Moving {len(name_lst) - len(test_speakers)} train speakers...")

# iterate over supplied subset dirs
for data_dir in data_dirs:
    # iterate over speakers
    for name in name_lst:
        if name in test_speakers:
            # move test speaker wavs to collection/test_dir
            os.system(f"find {data_dir} -not -path '*/.*' -a -name '{name}*.wav' -exec mv " + '{}' + f" {test_dir} \;")
        else:
            # move all other speaker wavs to collection/train_dir
            os.system(f"find {data_dir} -not -path '*/.*' -a -name '{name}*.wav' -exec mv " + '{}' + f" {train_dir} \;")
        # move all manual transcriptions to collection/trans_dir
        os.system(f"find {data_dir} -not -path '*/.*' -a -name '{name}*.ort' -exec mv " + '{}' + f" {trans_dir} \;")
