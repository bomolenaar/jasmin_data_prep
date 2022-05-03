#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re, sys, os, shutil
import os.path

if (len(sys.argv) < 3):
    print("You must add two arguments: a folder name for generating the files and the root path to this project folder.")
    sys.exit(-1)

subset = sys.argv[1]
myfolder = sys.argv[2]
## DIRECTORIES all of them ending with / ##
# output data dir, e.g.; "/vol/tensusers3/nvhelleman/jasmin/data/"
filedir = os.path.join(myfolder, subset, "data/")
# tier dir, e.g.; "/vol/tensusers3/nvhelleman/jasmin/20220210/tier/"
original_prev = os.path.join(myfolder, subset, 'tier')
original = original_prev+'_utf8/'
os.system('./encoding.sh '+original_prev + ' '+original)
# wav (test) files to use dir, e.g.; "/vol/tensusers3/nvhelleman/jasmin/20220210/wav_files_to_use/"
# test_set = os.path.join(myfolder, subset, 'wav_files_to_use_test/')
# wav (train)
wav_folder = os.path.join(myfolder, subset, 'wav_files_to_use/')
train_set = os.path.join(myfolder, subset, 'wav_files_to_use_train/')
trans_folder = os.path.join(myfolder, subset, 'manual_transcriptions/')
wav_untrimmed = os.path.join(myfolder, subset, '.wav_files_untrimmed/')
# rec to use file
rec = os.path.join(myfolder, subset, 'rec_to_use.txt')

wavs = []
for name in os.listdir(wav_folder):
    wavs.append(name)


def gen_trans_wavs(wavs, wav_folder, wav_folder_train, trans_folder, wav_folder_untrimmed):
    for name in wavs:
        basename = name.split('.')[0]
        file = open(original + basename + '.awd', 'r', encoding='utf8').readlines()

        transcript = []
        transcript_text = ""
        number = 1

        for line in range(15, len(file)):
            if 'xmin =' in file[line]:
                xmin = float(re.findall("\d+\.?\d*", file[line])[0])
                xmax = float(re.findall("\d+\.?\d*", file[line + 1])[0])
                word = re.findall('"([^"]*)"', file[line + 2])[0]
                if (word != "") and (word != 'ggg.') and (word != '!ggg.') and (word != 'xxx.'):
                    transcript.append([word, xmin, xmax])
                    # if '...' in word:
                    #     continue
                    # el
                    if ('.' in word) or ('?' in word):
                        start = transcript[0][1]
                        end = transcript[-1][2]
                        for word, xmin, xmax in transcript:
                            transcript_text += word + ' '

                        with open(f"{trans_folder}{basename}_{str(number).zfill(3)}.ort", 'w',
                                  encoding='utf-8') as transcript_file:
                            transcript_file.write(transcript_text)

                        os.system(
                            f"sox {wav_folder}{basename}.wav {wav_folder_train}{basename}_{str(number).zfill(3)}.wav trim {start} ={end} pad 0.3 0.3")

                        transcript = []
                        transcript_text = ""
                        number += 1

        # move untrimmed file
        os.system(f"mv {wav_folder}{basename}.wav {wav_folder_untrimmed}{basename}.wav")

    # remove empty wav folder
    shutil.rmtree(wav_folder)

gen_trans_wavs(wavs, wav_folder, train_set, trans_folder, wav_untrimmed)

os.system(f"python3 string_norm.py {trans_folder} {trans_folder}")

## TRAIN / TEST SET ##
TRAIN_PATH = 'train/'
# TEST_PATH = 'test/'
train = []
# test = []
for name in os.listdir(train_set):
    train.append(name)  # => train set
# for name in os.listdir(test_set):
#     test.append(name)   # => test set

## TEXT ##
def text(filenames):
    results = []
    transcript = ""
    for name in filenames:
        basename = name.split('.')[0]
        file = trans_folder + basename + '.ort'
        text = [line for line in open(file, 'r', encoding='utf-8').readlines()]
        for line in text:
            transcript += line.strip('\n')
        results.append("{} {}".format(basename, transcript))
        transcript = ""
    return '\n'.join(sorted(results))


with open(filedir+TRAIN_PATH+'text', 'w', encoding='utf-8') as train_text:#, open(filedir+TEST_PATH+'text', 'w', encoding='utf-8') as test_text:
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

with open(filedir+TRAIN_PATH+'utt2spk', 'a') as train_text: #, open(filedir+TEST_PATH+'utt2spk', 'a') as test_text:
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
