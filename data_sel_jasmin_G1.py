#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import os
import glob
import sys
import shutil
from pathlib import Path

if (len(sys.argv) < 4):
    print("You must add three arguments: folder names for generating qG1-1 and qG1-2 files and the root path to this project folder.")
    sys.exit(-1)


subset1 = sys.argv[1]
subset2 = sys.argv[2]
main_folder = os.path.join(sys.argv[3], subset1)
second_folder = os.path.join(sys.argv[3], subset2)
jasmin_folder = '/vol/bigdata/corpora/JASMIN/'
recordings = '/vol/bigdata/corpora/JASMIN/CDdoc/data/meta/text/nl/recordings.txt'
textgrid_path = '/vol/tensusers4/bmolenaar/IS2022proj/Limonard_textgrids_utf8'
selected_recordings = os.path.join(main_folder, 'rec_to_use.txt')
wav_folder_train = os.path.join(second_folder, 'wav_files_to_use_train')
wav_folder_test = os.path.join(main_folder, 'wav_files_to_use_test')
ort_folder = os.path.join(main_folder, 'manual_transcriptions')
prompt_folder = os.path.join(main_folder, 'prompts')
second_ort_folder = os.path.join(second_folder, 'manual_transcriptions')

# remove my old folders
shutil.rmtree(main_folder, ignore_errors=True)
shutil.rmtree(second_folder, ignore_errors=True)

# create main_folder and second_folder
path_to_main_folder = Path(main_folder)
path_to_main_folder.mkdir()
path_to_second_folder = Path(second_folder)
path_to_second_folder.mkdir()

def split_save_stories(textgrid_list, wav_folder_train, wav_folder_test, ort_folder, second_ort_folder, prompt_folder):
    'wtf did i do here again?'

    for textgrid in textgrid_list:
        file = open(textgrid, 'r', encoding='utf8').readlines()
        for line in range(len(file)):
            if 'item [1]' in file[line]:
                transcripts_start = line
            if 'item [2]' in file[line]:
                transcripts_end = line[-1]
            if 'item [4]' in file[line]:
                prompts_start = line
            if 'item [5]' in file[line]:
                prompts_end = line[-1]

        # iterate over prompts
        for line in range(prompts_start, prompts_end):
            if ('text =' in file[line]) and ('name =' not in file[line]):
                if re.findall('"([^"]*)"', file[line]) != "":
                    text = file[line].split('=')[1].strip(' ')
                    xmin = re.findall("\d+\.?\d*", file[line-2])
                    xmax = re.findall("\d+\.?\d*", file[line-1])


# generate selected recordings, change the if statement accordingly
with open(recordings,'r', encoding='utf-8') as f_in, open(selected_recordings,'w', encoding='utf-8') as f_out:
    for line in f_in:
        w_lst = line.split()
        if (w_lst[3] == '1') and (w_lst[2] == 'comp-q'):
            f_out.write(line)

# create folders if not exist, remove folders if exist
folder_lst = [prompt_folder, second_ort_folder, ort_folder, wav_folder_train, wav_folder_test]
for folder in folder_lst:
    if os.path.isdir(folder):
        filelist = [f for f in os.listdir(folder) if not os.path.isdir(f)]
        for f in filelist:
            os.remove(os.path.join(folder,f))
    else:
        os.mkdir(folder)

# put selected recordings .wav my folder
name_lst = []
with open(selected_recordings, 'r', encoding='utf-8') as f:
    for line in f:
        name_lst.append(line.split()[0])

wav_file_lst = []
tg_file_lst = []
# Cristian: this is not optimized at all... but it works :)
for i in name_lst:
    for dirpath, dirnames, filenames in os.walk(jasmin_folder):
        for filename in filenames:
            if i in filename:
                if filename.endswith('.wav'):
                    wav_file_lst.append(os.path.join(dirpath, filename))
    for dirpath, dirnames, filenames in os.walk(textgrid_path):
        for filename in filenames:
            if i in filename:
                if filename.endswith('.TextGrid'):
                    tg_file_lst.append(os.path.join(dirpath, filename))

print('wav_file_lst',len(wav_file_lst))
for j in wav_file_lst:
    #print(j)
    shutil.copy(j, wav_folder)

print('textgrid_file_lst',len(tg_file_lst))
print(tg_file_lst[:5])

#split_save_stories()
