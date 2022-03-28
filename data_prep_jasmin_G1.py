#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re, sys, os
import os.path
import string_norm.text_filter as text_filter

if (len(sys.argv) < 3):
    print("You must add two arguments: a folder name for generating the files and the root path to this project folder.")
    sys.exit(-1)

subset = sys.argv[1]
# TODO: this should run with subset = 2 instead of 1 for consistency
myfolder = sys.argv[2]
## DIRECTORIES all of them ending with / ##
# output data dir, e.g.; "/vol/tensusers3/nvhelleman/jasmin/data/"
filedir = myfolder+subset+"data/"
# tier dir, e.g.; "/vol/tensusers3/nvhelleman/jasmin/20220210/tier/"
# original_prev = os.path.join(myfolder, subset, 'tier')
original = myfolder + subset + 'manual_transcriptions/'
original_filtered = original[:-1] + '_filtered/'
G1_prompts = myfolder + 'jasmin_qG1-1/' + 'prompts/'
G1_ort = myfolder + 'jasmin_qG1-1/' + 'manual_transcriptions/'
# os.system('./encoding.sh '+original_prev+ ' '+original)
# wav (test) files to use dir, e.g.; "/vol/tensusers3/nvhelleman/jasmin/20220210/wav_files_to_use/"
# test_set = os.path.join(myfolder, 'jasmin_qG1-1', 'wav_files_to_use_test/')
# wav (train)
train_set = os.path.join(myfolder, subset, 'wav_files_to_use_train/')
# rec to use file
rec = os.path.join(myfolder, 'jasmin_qG1-1', 'rec_to_use.txt')

# os.system(f'mkdir -p {train_set}')
# os.system(f'mkdir -p {test_set}')
# os.system(f'mkdir -p {filedir}')
# os.system(f'mkdir -p {filedir}/train_jasmin')
# os.system('mkdir -p data/test_jasmin')

# normalise manual transcriptions, prompts for G1-1 and G1-2
# os.system(f'python3 string_norm.py {original} {original}')
# os.system(f'python3 string_norm.py {G1_prompts} {G1_prompts}')
# os.system(f'python3 string_norm.py {G1_ort} {G1_ort}')

## TEXT ##
def text(filenames):
    results = []
    for name in filenames:
        basename = name.split('.')[0]
        file = open(original + basename + '.ort')  # take non-normalised
        transcript = ""
        clean_transcript = ""
        for line in file:
            transcript += line.strip("\n") + ' '
            if "." in line:
                for word in transcript.split(' '):
                    clean_word = text_filter.remove_accents_from_lower(text_filter.clean_word(word))
                    clean_transcript += clean_word + ' '
                results.append("{} {}".format(basename, clean_transcript))
                transcript = ""
                clean_transcript = ""
    return '\n'.join(sorted(results))


## TRAIN / TEST SET ##
TRAIN_PATH = 'train_jasmin/'
# TEST_PATH = 'test_jasmin/'
train = []
# test = []
for name in os.listdir(train_set):
    train.append(name)  # => train set
# for name in os.listdir(test_set):
#     test.append(name)   # => test set

with open(filedir+TRAIN_PATH+'text', 'w', encoding='utf-8') as train_text: #, open(filedir+TEST_PATH+'text', 'w', encoding='utf-8') as test_text:
    train_text.write(text(train)+ '\n')
    # test_text.write(text(test)+ '\n')


## UTT2SPK ##
def utt2spk(filenames):
    results = []
    for name in filenames:
        basename = name.split('.')[0]
        spk_id = basename.split('_')[0]
        results.append("{} {}".format(basename, spk_id))
    return '\n'.join(sorted(results))


with open(filedir+TRAIN_PATH+'utt2spk', 'w', encoding='utf-8') as train_text: #, open(filedir+TEST_PATH+'utt2spk', 'w', encoding='utf-8') as test_text:
    train_text.write(utt2spk(train))
    # test_text.write(utt2spk(test))


## WAV.SCP ##
def wav_scp(filenames, set):
    results = []
    for name in filenames:
        basename = name.split('.')[0]
        results.append("{} {}".format(basename, set + name))
    return "\n".join(sorted(results))


with open(filedir+TRAIN_PATH+'wav.scp', 'w', encoding='utf-8') as train_text: #, open(filedir+TEST_PATH+'wav.scp', 'w', encoding='utf-8') as test_text:
    train_text.write(wav_scp(train, train_set)+ '\n')
    # test_text.write(wav_scp(test, test_set)+ '\n')


## SPK2UTT ##
def spk2utt():
    os.system('utils/utt2spk_to_spk2utt.pl '+filedir+TRAIN_PATH+'/utt2spk > '+filedir+TRAIN_PATH+'/spk2utt')
    # os.system('utils/utt2spk_to_spk2utt.pl '+filedir+TEST_PATH+'/utt2spk > '+filedir+TEST_PATH+'/spk2utt')


spk2utt()

with open(filedir+TRAIN_PATH+'utt2spk', 'w') as train_text: #, open(filedir+TEST_PATH+'utt2spk', 'w') as test_text:
    train_text.write('\n')
    # test_text.write('\n')


## SEGMENTS ##
def segments(filenames):
    results = []
    for name in filenames:
        basename = name.split('.')[0]
        file = open(original + basename + '.ort')
        begin = ""
        end = ""
        start = True
        number = 1
        for line in file:
          if "xmin =" in line and start:
            begin = line.split('= ')[1].replace('\n', '')
            start = False
          if "xmax =" in line:
            end = line.split('= ')[1].replace('\n', '')
          if "text =" in line:
            if "." in line:
              results.append("{} {} {} {}".format(basename+"_"+str(number).zfill(4), basename, begin, end))
              number += 1
              start = True
    return '\n'.join(sorted(results))


# with open(filedir+TRAIN_PATH+'segments', 'w', encoding='utf-8') as train_text, open(filedir+TEST_PATH+'segments', 'w', encoding='utf-8') as test_text:
#     train_text.write(segments(train)+ '\n')
#     test_text.write(segments(test)+ '\n')


## SPK2GENDER ##
def spk2gender(filenames):
    results = []
    for name in filenames:
        file = open(rec)
        basename = name.split('.')[0]
        spk_id = basename.split('_')[0]
        for line in file:
          if spk_id in line:
            if "F" in line:
              results.append("{} {}".format(spk_id, "f"))
            elif "M" in line:
              results.append("{} {}".format(spk_id, "m"))
    unique_results = list(set(results))
    return "\n".join(sorted(unique_results))


with open(filedir+TRAIN_PATH+'spk2gender', 'w', encoding='utf-8') as train_text: #, open(filedir+TEST_PATH+'spk2gender', 'w', encoding='utf-8') as test_text:
    train_text.write(spk2gender(train)+ '\n')
    # test_text.write(spk2gender(test)+ '\n')
