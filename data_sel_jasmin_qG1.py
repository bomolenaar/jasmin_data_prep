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
textgrid_path = '/vol/tensusers4/bmolenaar/A3proj/Limonard_textgrids_utf8'
selected_recordings = os.path.join(main_folder, 'rec_to_use.txt')
wav_folder = os.path.join(second_folder, 'wav_files_to_use/')
wav_folder_train = os.path.join(second_folder, 'wav_files_to_use_train/')
wav_folder_test = os.path.join(main_folder, 'wav_files_to_use_test/')
wav_folder_untrimmed = os.path.join(main_folder, 'wav_files_untrimmed/')
ort_folder = os.path.join(main_folder, 'manual_transcriptions/')
prompt_folder = os.path.join(main_folder, 'prompts/')
second_ort_folder = os.path.join(second_folder, 'manual_transcriptions/')


# remove old main_folder and second_folder and create new ones
path_to_main_folder = Path(main_folder)
if os.path.exists(path_to_main_folder):
    shutil.rmtree(path_to_main_folder)
path_to_main_folder.mkdir()

path_to_second_folder = Path(second_folder)
if os.path.exists(path_to_second_folder):
    shutil.rmtree(path_to_second_folder)
path_to_second_folder.mkdir()

def split_save_stories(textgrid_list, wav_folder, wav_folder_train, wav_folder_test, wav_folder_untrimmed, ort_folder, second_ort_folder, prompt_folder):
    """takes JASMIN comp-q G1 files and segments them into 1st and 2nd story;
    1st includes prompts, 2nd does not"""
    delta_skipped = 0
    uhms_skipped = 0
    for name in textgrid_list:
        file = open(name, 'r', encoding='utf8').readlines()
        basename = name.split('.')[0].split('/')[-1]
        number = 1
        transcript = []
        transcript_text = ""

        ignore_words = {'',
                        'ggg', 'ggg.', '!ggg.', 'xxx', 'xxx.', '!xxx',
                        'uh', 'uh.', 'uh..', 'uhm', 'uhm.', 'uhm..'}

        for line in range(len(file)):
            if 'item [1]' in file[line]:
                transcripts_start = line
            if 'item [2]' in file[line]:
                transcripts_end = line-1
            if 'item [4]' in file[line]:
                prompts_start = line
            if 'item [5]' in file[line]:
                prompts_end = line-1

        # iterate over prompts
        for line in range(prompts_start, prompts_end):
            if ('text =' in file[line]) and ('name =' not in file[line-7]):
                prompt = re.findall('"([^"]*)"', file[line])[0]
                if prompt != "":
                    xmin_prompt = round(float(re.findall("\d+\.?\d*", file[line-2])[0]), 4)
                    xmax_prompt = round(float(re.findall("\d+\.?\d*", file[line-1])[0]), 4)

                    # os.system(f"sox {wav_folder}{basename}.wav {wav_folder_test}{basename}_1_{str(number).zfill(3)}.wav trim {xmin_prompt} ={xmax_prompt} pad 0.3 0.3")
                    #
                    # with open(f"{prompt_folder}{basename}_1_{str(number).zfill(3)}.prompt", 'w', encoding='utf-8') as prompt_file:
                    #     prompt_file.write(prompt)

                    # iterate over manual transcriptions
                    for line in range(transcripts_start, transcripts_end):
                        if ('xmin =' in file[line]) and ('name =' not in file[line-5]):
                            xmin = round(float(re.findall("\d+\.?\d*", file[line])[0]), 4)
                            xmax = round(float(re.findall("\d+\.?\d*", file[line+1])[0]), 4)
                            if (xmin >= xmin_prompt) and (xmax <= xmax_prompt):
                                word = re.findall('"([^"]*)"', file[line+2])[0]

                                # SOLUTION:
                                # 1. get # decimals xmin, xmax, xmin_prompt, xmax_prompt
                                # 2. round to lowest of matching set
                                # 3. compare as usual without modifying the values

                                ### DEBUG BLOCK ###
                                names = {'fn000051', 'fn000066', 'fn000068'}
                                if basename in names:
                                    print(basename, number)
                                    print(prompt)
                                    print("xmin_prompt", xmin_prompt)
                                    print("xmin", xmin)
                                    print("xmax_prompt", xmax_prompt)
                                    print("xmax", xmax)
                                    print()
                                ### END DEBUG BLOCK ###

                                transcript.append([word, xmin, xmax])
                                if xmax == xmax_prompt:
                                    for word, xmin, xmax in transcript:
                                        if word != "":
                                            transcript_text += word + ' '
                                    # with open(f"{ort_folder}{basename}_1_{str(number).zfill(3)}.ort", 'w', encoding='utf-8') as transcript_file:
                                    #     transcript_file.write(transcript_text)
                                    transcript = []
                                    transcript_text = ""
                                    number += 1

        # iterate over manual transcriptions again but this time post prompts
        number = 1
        for line in range(transcripts_start, transcripts_end):
            if 'xmin =' in file[line]:
                xmin = round((float(re.findall("\d+\.?\d*", file[line])[0])), 4)
                if xmin > xmax_prompt:
                    xmax = round(float(re.findall("\d+\.?\d*", file[line+1])[0]), 4)
                    word = re.findall('"([^"]*)"', file[line+2])[0]
                    if word not in ignore_words:
                        transcript.append([word, xmin, xmax])
                        if ('...' in word) and (len(transcript) >= 2):
                            delta = transcript[-1][1] - transcript[-2][2]
                            if delta <= 0.5:
                                delta_skipped += 1
                                continue
                        # elif '...' in word:
                        #     continue
                        elif ('.' in word) or ('?' in word):
                            if (len(transcript) == 1) and ("uh" in transcript[0][0]):
                                uhms_skipped += 1
                                continue
                            start = transcript[0][1]
                            end = transcript[-1][2]
                            for word, xmin, xmax in transcript:
                                transcript_text += word + ' '

                            # with open(f"{second_ort_folder}{basename}_2_{str(number).zfill(3)}.ort", 'w', encoding='utf-8') as transcript_file:
                            #     transcript_file.write(transcript_text)
                            #
                            # os.system(f"sox {wav_folder}{basename}.wav {wav_folder_train}{basename}_2_{str(number).zfill(3)}.wav trim {start} ={end} pad 0.3 0.3")

                            transcript = []
                            transcript_text = ""
                            number += 1

        # move untrimmed files
        os.system(f"mv {wav_folder}{basename}.wav {wav_folder_untrimmed}{basename}.wav")

    # remove empty wav folder
    shutil.rmtree(wav_folder)

    print(f"'...' deltas skipped: {delta_skipped}")
    print(f"uh(m)... skipped: {uhms_skipped}")


# generate selected recordings, change the if statement accordingly
with open(recordings,'r', encoding='utf-8') as f_in, open(selected_recordings,'w', encoding='utf-8') as f_out:
    for line in f_in:
        w_lst = line.split()
        if (w_lst[3] == '1') and (w_lst[2] == 'comp-q'):
            f_out.write(line)

# create folders if not exist, remove folders if exist
folder_lst = [prompt_folder, ort_folder, wav_folder_test,
              wav_folder, wav_folder_untrimmed, second_ort_folder, wav_folder_train]
for folder in folder_lst:
    if os.path.isdir(folder):
        filelist = [f for f in os.listdir(folder)]
        for f in filelist:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
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
    # print(j)
    shutil.copy(j, wav_folder)

print('textgrid_file_lst', len(tg_file_lst))

split_save_stories(tg_file_lst, wav_folder, wav_folder_train, wav_folder_test, wav_folder_untrimmed, ort_folder, second_ort_folder, prompt_folder)
