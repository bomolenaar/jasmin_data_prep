#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys

if (len(sys.argv) < 4):
    print(
        "You must add three arguments: two folder names for generating the files: test then train; the root path to this project folder")
    sys.exit(-1)
subset1 = sys.argv[1]
subset2 = sys.argv[2]
project_folder = sys.argv[3]
# file_input_ext = sys.argv[4]
# file_output_ext = sys.argv[5]

if os.path.exists('utils'):
    print('Directory "utils/" exists :)')

    # 1. DATA SELECTION
    # Optional: uncomment the following lines to select and praat the files
    print("Data selection...")
    os.system('python3 data_sel_jasmin_qG1.py ' + subset1 + ' ' + subset2 + ' ' + project_folder)

    # create data directories and subdirs
    os.system(f'mkdir -p {subset2}/data')
    os.system(f'mkdir -p {subset2}/data/train')
    os.system(f'mkdir -p {subset1}/data')
    os.system(f'mkdir -p {subset1}/data/test')

    # print("Preparing Praat files...")
    # os.system(
    #     '/usr/bin/praat --run step1_tg_to_std_format.praat "' + subset + '/awd_files_to_use" "' + subset + '/praat_files_to_use" ' + file_input_ext + ' ' + file_output_ext)
    # # TODO: change the parameters accordingly
    # os.system(
    #     '/usr/bin/praat --run step2_extract_tier.praat "' + subset + '/praat_files_to_use" "' + subset + '/tier"')

    # 2. DATA PREPARATION
    print("Data preparation...")
    os.system('python3 data_prep_jasmin_qG1.py ' + subset1 + ' ' + subset2 + ' ' + project_folder)

    # 3. DATA CHECKING
    os.system(f'./utils/validate_data_dir.sh {subset2}/data/train/ --no-feats')
    os.system(f'./utils/validate_data_dir.sh {subset1}/data/test/ --no-feats')
else:
    print('You need a valid utils/ folder:\n Try this command: ln -s $KALDI_ROOT/egs/wsj/s5/utils/ utils')
