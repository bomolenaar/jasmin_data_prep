#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re, sys, os
import os.path

if (len(sys.argv) < 3):
    print("You must add two arguments: a folder name for generating the files and the root path to this project folder.")
    sys.exit(-1)

subset1 = sys.argv[1]
subset2 = sys.argv[2]
myfolder = sys.argv[3]
## DIRECTORIES all of them ending with / ##
# output data dir, e.g.; "/vol/tensusers3/nvhelleman/jasmin/data/"
filedir = myfolder+subset2+"data/"
original = myfolder + subset2 + 'manual_transcriptions/'
G1_ort = myfolder + subset1 + 'manual_transcriptions/'
G1_prompts = myfolder + subset1 + 'prompts/'
# wav (test) files to use dir, e.g.; "/vol/tensusers3/nvhelleman/jasmin/20220210/wav_files_to_use/"
# test_set = os.path.join(myfolder, 'subset', 'wav_files_to_use_test/')
# wav (train)
train_set = os.path.join(myfolder, subset2, 'wav_files_to_use_train/')
# rec to use file
rec = os.path.join(myfolder, subset1, 'rec_to_use.txt')

# normalise manual transcriptions, prompts for G1-1 and G1-2
# os.system(f'python3 string_norm.py {G2_ort} {G2_ort}')
# os.system(f'python3 string_norm.py {G1_prompts} {G1_prompts}')
# os.system(f'python3 string_norm.py {G1_ort} {G1_ort}')

## TRAIN / TEST SET ##
TRAIN_PATH = 'train/'
# TEST_PATH = 'test_jasmin/'
train = []
# test = []
for name in os.listdir(train_set):
    train.append(name)  # => train set
# for name in os.listdir(test_set):
#     test.append(name)   # => test set

os.system(f'mkdir -p {filedir}')
os.system(f'mkdir -p {filedir}/train')


## TEXT ##
def text(filenames):
    results = []
    transcript = ""
    for name in filenames:
        basename = name.split('.')[0]
        file = original + basename + '.ort'
        text = [line for line in open(file, 'r', encoding='utf-8').readlines()]
        for line in text:
            transcript += line.strip('\n')
        results.append("{} {}".format(basename, transcript))
        transcript = ""
    return '\n'.join(sorted(results))


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
