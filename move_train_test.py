#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys
import pandas as pd

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

data_dirs = [os.path.join(project_folder, qG1_1), os.path.join(project_folder, qG1_2), os.path.join(project_folder, pG1)]
test_dir = os.path.join(project_folder, collection, 'wav_files_to_use_test/')
train_dir = os.path.join(project_folder, collection, 'wav_files_to_use_train/')
trans_dir = os.path.join(project_folder, collection, 'manual_transcriptions/')


def make_rec_set(recs1, recs2):
    recs1_df = pd.read_table(recs1, header=None)
    recs2_df = pd.read_table(recs2, header=None)
    rec_set = recs1_df.merge(recs2_df, how="outer")
    rec_set.to_string(os.path.join(collection, 'rec_to_use.txt'), header=None, index=None)
    return rec_set


recs = make_rec_set(os.path.join(qG1_1, 'rec_to_use.txt'), os.path.join(pG1, 'rec_to_use.txt'))
name_lst = []
for value in recs.itertuples():
    name_lst.append(value._1)

test_speakers = [line.strip('\n') for line in open(speakerfile, 'r').readlines()]

print(f"Moving {len(test_speakers)} test speakers...")
print(f"Moving {len(name_lst) - len(test_speakers)} train speakers...")

for data_dir in data_dirs:
    for name in name_lst:
        if name in test_speakers:
            os.system(f"find {data_dir} -not -path '*/.*' -a -name '{name}*.wav' -exec mv " + '{}' + f" {test_dir} \;")
        else:
            os.system(f"find {data_dir} -not -path '*/.*' -a -name '{name}*.wav' -exec mv " + '{}' + f" {train_dir} \;")
        os.system(f"find {data_dir} -not -path '*/.*' -a -name '{name}*.ort' -exec mv " + '{}' + f" {trans_dir} \;")
