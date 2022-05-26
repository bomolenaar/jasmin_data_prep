#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import os
import glob
import sys
import shutil
from pathlib import Path

if (len(sys.argv) < 3):
    print("You must add two arguments: a folder name for generating the files and the root path to this project folder.")
    sys.exit(-1)

subset = sys.argv[1]
myfolder = os.path.join(sys.argv[2], subset)

jasmin_folder = '/vol/bigdata/corpora/JASMIN/'
recordings = '/vol/bigdata/corpora/JASMIN/CDdoc/data/meta/text/nl/recordings.txt'
selected_recordings = os.path.join(myfolder, 'rec_to_use.txt')

wav_folder = os.path.join(myfolder, 'wav_files_to_use/')
awd_folder = os.path.join(myfolder, 'awd_files_to_use/')

wav_untrimmed_folder = os.path.join(myfolder, '.wav_files_untrimmed/')
trans_folder = os.path.join(myfolder, 'manual_transcriptions/')

praat_folder = os.path.join(myfolder, 'praat_files_to_use/')
original_prev = os.path.join(myfolder, 'tier')
original = original_prev+'_utf8/'

# remove my old folder
shutil.rmtree(myfolder, ignore_errors=True)

# create myfolder
path_to_myfolder = Path(myfolder)
path_to_myfolder.mkdir()

# generate selected recordings, change the if statement accordingly
with open(recordings, 'r', encoding='utf-8') as f_in, open(selected_recordings, 'w', encoding='utf-8') as f_out:
    for line in f_in:
        w_lst = line.split()
        if (w_lst[3] == '1') and (w_lst[2] == 'comp-p'):
            f_out.write(line)

# create folders if not exist, remove folders if exist
myfolder_lst = [wav_folder, awd_folder, trans_folder, praat_folder, original_prev, original, wav_untrimmed_folder]
for folder in myfolder_lst:
    if os.path.isdir(folder):
        filelist = [f for f in os.listdir(folder)]
        for f in filelist:
            if os.path.isdir(f):
                shutil.rmtree(f)
            else:
                os.remove(os.path.join(folder,f))
    else:
        os.mkdir(folder)

# put selected recordings .wav .ort .hmi and .awd in my folders
name_lst = []
with open(selected_recordings, 'r', encoding='utf-8') as f:
    for line in f:
        name_lst.append(line.split()[0])

wav_file_lst = []
awd_file_lst = []
# Cristian: this is not optimized at all... but it works :)
for i in name_lst:
    for dirpath, dirnames, filenames in os.walk(jasmin_folder):
        for filename in filenames:
            if i in filename:
                if filename.endswith('.wav'):
                    wav_file_lst.append(os.path.join(dirpath, filename))
                if filename.endswith('.awd'):
                    awd_file_lst.append(os.path.join(dirpath, filename))

print('wav_file_lst',len(wav_file_lst))
for j in wav_file_lst:
    #print(j)
    shutil.copy(j, wav_folder)

print('awd_file_lst',len(awd_file_lst))
for q in awd_file_lst:
    #print(q)
    shutil.copy(q, awd_folder)


def gen_trans_wavs(wav_folder, tier_folder, trans_folder, wav_folder_untrimmed):
    delta_skipped = 0
    for name in os.listdir(wav_folder):
        basename = name.split('.')[0]
        file = open(tier_folder + basename + '.awd', 'r', encoding='utf8').readlines()

        transcript = []
        transcript_text = ""
        number = 1
        ignore_words = {'',
                        'ggg.', '!ggg.', 'xxx.', '!xxx',
                        'uh', 'uh.', 'uh..', 'uh...', 'uhm', 'uhm.', 'uhm..', 'uhm...'}

        for line in range(15, len(file)):
            if 'xmin =' in file[line]:
                xmin = float(re.findall("\d+\.?\d*", file[line])[0])
                xmax = float(re.findall("\d+\.?\d*", file[line + 1])[0])
                word = re.findall('"([^"]*)"', file[line + 2])[0]
                if word not in ignore_words:
                    transcript.append([word, xmin, xmax])
                    if ('...' in word) and (len(transcript) > 1):
                        delta = float(transcript[-1][1]) - float(transcript[-2][2])
                        if delta <= 0.5:
                            delta_skipped += 1
                            continue
                    elif ('.' in word) or ('?' in word):
                        start = transcript[0][1]
                        end = transcript[-1][2]
                        for word, xmin, xmax in transcript:
                            transcript_text += word + ' '

                        with open(f"{trans_folder}{basename}_1_{str(number).zfill(3)}.ort", 'w',
                                  encoding='utf-8') as transcript_file:
                            transcript_file.write(transcript_text)

                        os.system(
                            f"sox {wav_folder}{basename}.wav {wav_folder}{basename}_1_{str(number).zfill(3)}.wav trim {start} ={end} pad 0.3 0.3")

                        transcript = []
                        transcript_text = ""
                        number += 1

        # move untrimmed file
        os.system(f"mv {wav_folder}{basename}.wav {wav_folder_untrimmed}{basename}.wav")

    print(f"'...' deltas skipped: {delta_skipped}")


os.system(f'/usr/bin/praat --run step1_tg_to_std_format.praat {awd_folder} {praat_folder} .awd .awd')
os.system(f'/usr/bin/praat --run step2_extract_tier.praat {praat_folder} {original_prev}')

os.system('./encoding.sh '+original_prev + ' '+original)

print("Segmenting...")
gen_trans_wavs(wav_folder, original, trans_folder, wav_untrimmed_folder)

print("String normalisation...")
os.system(f"python3 string_norm.py {trans_folder} {trans_folder}")
