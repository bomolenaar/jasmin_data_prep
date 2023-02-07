#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import os
import sys
import shutil
from pathlib import Path

if (len(sys.argv) < 3):
    print("You must add two arguments: a folder name for generating the files and the root path to this project folder.")
    sys.exit(-1)

subset = sys.argv[1]
myfolder = os.path.join(sys.argv[2], subset)

### Declarations ###
# locations of static source directories
jasmin_folder = '/vol/bigdata/corpora/JASMIN/'
recordings = '/vol/bigdata/corpora/JASMIN/CDdoc/data/meta/text/nl/recordings.txt'
# file to be generated with our speaker list
selected_recordings = os.path.join(myfolder, 'rec_to_use.txt')

# locations of local wav files and awd files
wav_folder = os.path.join(myfolder, 'wav_files_to_use/')
awd_folder = os.path.join(myfolder, 'awd_files_to_use/')

# directory to move full wav files after segmentation
wav_untrimmed_folder = os.path.join(myfolder, '.wav_files_untrimmed/')
# location of directory to generate manual transcriptions
trans_folder = os.path.join(myfolder, 'manual_transcriptions/')

# directories required for praat scripts
praat_folder = os.path.join(myfolder, 'praat_files_to_use/')
original_prev = os.path.join(myfolder, 'tier')
original = original_prev+'_utf8/'

### Directory management ###
# remove my old project folder
shutil.rmtree(myfolder, ignore_errors=True)

# create myfolder
path_to_myfolder = Path(myfolder)
path_to_myfolder.mkdir()

### Select recordings ###
# generate selected recordings, change the if statement accordingly
with open(recordings, 'r', encoding='utf-8') as f_in, open(selected_recordings, 'w', encoding='utf-8') as f_out:
    for line in f_in:
        w_lst = line.split()
        if (w_lst[3] == '1') and (w_lst[2] == 'comp-p'):
            f_out.write(line)

### Directory management 2 ###
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

# Now we make segments and generate necessary files
def gen_trans_wavs(wav_folder, tier_folder, trans_folder, wav_folder_untrimmed):
    """
    Method that takes .awd and .wav files from JASMIN corpus, then establishes segments
    and generates required files for Kaldi data preparation.
    Segments are created based on periods, with the exception of a string ending in
    variations of 'uh(m)...'. Segments that are less than 0.5s apart are merged.

    :param wav_folder: .wav files input dir
    :param tier_folder: .awd files (after praat scripts processing) input dir
    :param trans_folder: .ort files output dir
    :param wav_folder_untrimmed: .wav files archive after trimming output dir
    :return: None
    """

    # Var counting number of segments merged when less than some amount of time apart. Default 0.5s.
    delta_skipped = 0

    # Iterate over wav files
    for name in os.listdir(wav_folder):
        # get speaker id from wav file name
        basename = name.split('.')[0]
        # open awd file for this speaker id
        file = open(tier_folder + basename + '.awd', 'r', encoding='utf8').readlines()

        # declare some vars to use later
        transcript = []
        transcript_text = ""
        number = 1  # segment number for this speaker id
        # words to exclude from segments
        ignore_words = {'',
                        'ggg.', '!ggg.', 'xxx.', '!xxx',
                        'uh', 'uh.', 'uh..', 'uh...', 'uhm', 'uhm.', 'uhm..', 'uhm...'}

        # Iterate over lines in .awd file, starting at Tier 1 = speaker transcription, at the first word
        for line in range(15, len(file)):
            if 'xmin =' in file[line]:
                # store word start and end times
                xmin = float(re.findall("\d+\.?\d*", file[line])[0])
                xmax = float(re.findall("\d+\.?\d*", file[line + 1])[0])
                word = re.findall('"([^"]*)"', file[line + 2])[0]
                # exclude words from ignore set
                if word not in ignore_words:
                    # store word + start time + end time in a 3-tuple list
                    transcript.append([word, xmin, xmax])
                    # check time since prev segment if current segment is only a single word with '...'
                    if ('...' in word) and (len(transcript) > 1):
                        delta = float(transcript[-1][1]) - float(transcript[-2][2])
                        # continue current segment if time since prev segment <= some amount of time (default 0.5s)
                        if delta <= 0.5:
                            delta_skipped += 1
                            continue
                    # now check if current word has a period or question mark == end of segment
                    elif ('.' in word) or ('?' in word):
                        # get start and end time of the segment
                        start = transcript[0][1]
                        end = transcript[-1][2]
                        for word, xmin, xmax in transcript:
                            # generate string with segment transcript
                            transcript_text += word + ' '

                        # write transcript string to file
                        with open(f"{trans_folder}{basename}_1_{str(number).zfill(3)}.ort", 'w',
                                  encoding='utf-8') as transcript_file:
                            transcript_file.write(transcript_text)

                        # crop segment from wav file and pad 0.3s silence on each end
                        os.system(f"sox {wav_folder}{basename}.wav {wav_folder}{basename}_1_{str(number).zfill(3)}.wav trim {start} ={end} pad 0.3 0.3")

                        # reset transcript, string and segment counter
                        transcript = []
                        transcript_text = ""
                        number += 1

        # move untrimmed file
        os.system(f"mv {wav_folder}{basename}.wav {wav_folder_untrimmed}{basename}.wav")

    # print number of segments merged based on delta
    print(f"'...' deltas skipped: {delta_skipped}")


# praat scripts that process original .awd files into the format we want
os.system(f'/usr/bin/praat --run step1_tg_to_std_format.praat {awd_folder} {praat_folder} .awd .awd')
os.system(f'/usr/bin/praat --run step2_extract_tier.praat {praat_folder} {original_prev}')

# convert .awd files encoding to utf-8
os.system('./encoding.sh '+original_prev + ' '+original)

# generate segments
print("Segmenting...")
gen_trans_wavs(wav_folder, original, trans_folder, wav_untrimmed_folder)

# run string normalisation for manual transcriptions
print("String normalisation...")
os.system(f"python3 string_norm.py {trans_folder} {trans_folder}")
