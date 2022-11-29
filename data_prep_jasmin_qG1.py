#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re, sys, os
import os.path

if (len(sys.argv) < 4):
    print("You must add three arguments: a folder name for generating the files: test then train; and the root path to this project folder.")
    sys.exit(-1)

subset1 = sys.argv[1]
subset2 = sys.argv[2]
myfolder = sys.argv[3]

## DIRECTORIES all of them ending with / ##
# output data dir, e.g.; "/vol/tensusers4/bmolenaar/jasmin_data_prep/A3_jasmin_G1/data/"

filedir1 = os.path.join(myfolder, subset1, 'data/')
filedir2 = os.path.join(myfolder, subset2, 'data/')

G2_ort = os.path.join(myfolder, subset2, 'manual_transcriptions/')
G1_ort = os.path.join(myfolder, subset1, 'manual_transcriptions/')

# wav (test) files to use dir, e.g.; "/vol/tensusers4/bmolenaar/jasmin_data_prep/A3_jasmin_G1/wav_files_to_use/"
test_set = os.path.join(myfolder, subset1, 'wav_files_to_use/')
# wav (train)
train_set = os.path.join(myfolder, subset2, 'wav_files_to_use/')
# rec to use file
rec = os.path.join(myfolder, subset1, 'rec_to_use.txt')

## TRAIN / TEST SET ##
TRAIN_PATH = 'train/'
TEST_PATH = 'test/'
train = []
test = []
for name in os.listdir(train_set):
    train.append(name)  # => train set
for name in os.listdir(test_set):
    test.append(name)   # => test set


## TEXT ##
def text(filenames, filedir):
    results = []
    transcript = ""
    for name in filenames:
        basename = name.split('.')[0]
        file = filedir + basename + '.ort'
        text = [line for line in open(file, 'r', encoding='utf-8').readlines()]
        for line in text:
            transcript += line.strip('\n')
        results.append("{} {}".format(basename, transcript))
        transcript = ""
    return '\n'.join(sorted(results))


with open(filedir2+TRAIN_PATH+'text', 'w', encoding='utf-8') as train_text, open(filedir1+TEST_PATH+'text', 'w', encoding='utf-8') as test_text:
    train_text.write(text(train, G2_ort)+ '\n')
    test_text.write(text(test, G1_ort)+ '\n')


## UTT2SPK ##
def utt2spk(filenames):
    results = []
    for name in filenames:
        basename = name.split('.')[0]
        spk_id = basename.split('_')[0]
        results.append("{} {}".format(basename, spk_id))
    return '\n'.join(sorted(results))


with open(filedir2+TRAIN_PATH+'utt2spk', 'w', encoding='utf-8') as train_text, open(filedir1+TEST_PATH+'utt2spk', 'w', encoding='utf-8') as test_text:
    train_text.write(utt2spk(train))
    test_text.write(utt2spk(test))


## WAV.SCP ##
def wav_scp(filenames, set):
    results = []
    for name in filenames:
        basename = name.split('.')[0]
        results.append("{} {}".format(basename, set + name))
    return "\n".join(sorted(results))


with open(filedir2+TRAIN_PATH+'wav.scp', 'w', encoding='utf-8') as train_text, open(filedir1+TEST_PATH+'wav.scp', 'w', encoding='utf-8') as test_text:
    train_text.write(wav_scp(train, train_set)+ '\n')
    test_text.write(wav_scp(test, test_set)+ '\n')


## SPK2UTT ##
def spk2utt():
    os.system('utils/utt2spk_to_spk2utt.pl '+filedir2+TRAIN_PATH+'/utt2spk > '+filedir2+TRAIN_PATH+'/spk2utt')
    os.system('utils/utt2spk_to_spk2utt.pl '+filedir1+TEST_PATH+'/utt2spk > '+filedir1+TEST_PATH+'/spk2utt')


spk2utt()

with open(filedir2+TRAIN_PATH+'utt2spk', 'a') as train_text, open(filedir1+TEST_PATH+'utt2spk', 'a') as test_text:
    train_text.write('\n')
    test_text.write('\n')


## SEGMENTS ##
def segments(filenames):
    results = []
    for name in filenames:
        basename = name.split('.')[0]
        original = ''
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


with open(filedir2+TRAIN_PATH+'spk2gender', 'w', encoding='utf-8') as train_text, open(filedir1+TEST_PATH+'spk2gender', 'w', encoding='utf-8') as test_text:
    train_text.write(spk2gender(train)+ '\n')
    test_text.write(spk2gender(test)+ '\n')
