jasm#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys

""""
@Author:    Bo Molenaar
@Date:      3 June 2022

This script takes 3 JASMIN subsets and performs data selection and preparation for use with Kaldi ASR.
It requires declaration of a file indicating speaker ids to be used as test data (line 28). 
All other found speakers are used as train data.
"""

if (len(sys.argv) < 6):
    print(
        "You must add 5 arguments: locations of comp-q G1-1, G1-2 and comp-p G1 data, a folder name for generating the files and the root path to this project folder")
    sys.exit(-1)

qG1_1 = sys.argv[1]
qG1_2 = sys.argv[2]
pG1 = sys.argv[3]
collection = sys.argv[4]
project_folder = sys.argv[5]

# location of test speakers file
test_speakers = os.path.join(project_folder, "A3_jasmin_G1_test.txt")

# create data directory and subdirs
os.system(f'rm -r {collection}')
os.system(f'mkdir -p {collection}')
os.system(f'mkdir -p {collection}/data')
os.system(f'mkdir -p {collection}/data/train')
os.system(f'mkdir -p {collection}/data/test')

os.system(f'mkdir -p {collection}/wav_files_to_use_test')
os.system(f'mkdir -p {collection}/wav_files_to_use_train')
os.system(f'mkdir -p {collection}/manual_transcriptions')

if os.path.exists('utils'):
    print('Directory "utils/" exists :)')

    # 1. DATA SELECTION
    print("Data selection...")
    print("qG1")
    os.system(f'python3 data_sel_jasmin_qG1.py {qG1_1} {qG1_2} {project_folder}')
    print("pG1")
    os.system(f'python3 data_sel_jasmin_pG1.py {pG1} {project_folder}')

    # 2. MOVE FILES
    os.system(f"python3 move_train_test.py {test_speakers} {qG1_1} {qG1_2} {pG1} {collection} {project_folder}")

    # 3. DATA PREPARATION
    input("Before data preparation, check your train and test wav and transcription folders and press [ENTER]...")
    os.system(f'python3 data_prep_jasmin.py {collection} {project_folder}')

    # 4. DATA CHECKING
    os.system(f'./utils/validate_data_dir.sh {collection}/data/train/ --no-feats')
    os.system(f'./utils/validate_data_dir.sh {collection}/data/test/ --no-feats')
else:
    print('You need a valid utils/ folder:\n Try this command: ln -s $KALDI_ROOT/egs/wsj/s5/utils/ utils')
