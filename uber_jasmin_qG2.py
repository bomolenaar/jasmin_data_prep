#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os, sys

if (len(sys.argv) < 5):
    print(
        "You must add four arguments: a folder name for generating the files; the root path to this project folder; file_input extension and file_output extension")
    sys.exit(-1)
subset = sys.argv[1]
project_folder = sys.argv[2]
file_input_ext = sys.argv[3]
file_output_ext = sys.argv[4]

if os.path.exists('utils'):
    print('Directory "utils/" exists :)')

    # 1. DATA SELECTION
    # Optional: uncomment the following lines to select and praat the files
    print("Data selection...")
    os.system('python3 data_sel_jasmin_qG2.py ' + subset + ' ' + project_folder)
    # You need to run these two scripts on Windows (not working on Linux yet)
    # create data directory and subdirs
    os.system(f'mkdir -p {subset}/data')
    os.system(f'mkdir -p {subset}/data/train')
    # os.system('mkdir -p data/test')

    print("Preparing Praat files...")
    os.system(
        '/usr/bin/praat --run step1_tg_to_std_format.praat "' + subset + '/awd_files_to_use" "' + subset + '/praat_files_to_use" ' + file_input_ext + ' ' + file_output_ext)
    # TODO: change the parameters accordingly
    os.system(
        '/usr/bin/praat --run step2_extract_tier.praat "' + subset + '/praat_files_to_use" "' + subset + '/tier"')

    # 2. DATA PREPARATION
    print("Data preparation...")
    os.system('python3 data_prep_jasmin_qG2.py ' + subset + ' ' + project_folder)

    # 3. DATA CHECKING
    os.system(f'./utils/validate_data_dir.sh {subset}/data/train/ --no-feats')
    # os.system('./utils/validate_data_dir.sh data/test_jasmin/ --no-feats')
else:
    print('You need a valid utils/ folder:\n Try this command: ln -s $KALDI_ROOT/egs/wsj/s5/utils/ utils')
