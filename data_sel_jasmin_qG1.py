#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import os
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

### Declarations ###
# locations of static source directories
jasmin_folder = '/vol/bigdata/corpora/JASMIN/'
recordings = '/vol/bigdata/corpora/JASMIN/CDdoc/data/meta/text/nl/recordings.txt'
textgrid_path = '/vol/tensusers4/bmolenaar/A3proj/Limonard_textgrids_utf8'
# file to be generated with our speaker list
selected_recordings = os.path.join(main_folder, 'rec_to_use.txt')

# locations of local wav files
wav_folder = os.path.join(main_folder, 'wav_files_to_use/')
second_wav_folder = os.path.join(second_folder, 'wav_files_to_use/')
# directory to move full wav files after segmentation
wav_folder_untrimmed = os.path.join(main_folder, '.wav_files_untrimmed/')

# location of directories to generate manual transcriptions and prompts
prompt_folder = os.path.join(main_folder, 'prompts/')
ort_folder = os.path.join(main_folder, 'manual_transcriptions/')
second_ort_folder = os.path.join(second_folder, 'manual_transcriptions/')

# adapt_dir = os.path.join(main_folder, 'adapt/')
# adapt_orts = os.path.join(main_folder, 'adapt/', 'manual_transcriptions/')
# adapt_prompts = os.path.join(main_folder, 'adapt/', 'prompts/')


### Directory management ###
# remove old main_folder and second_folder and create new ones
path_to_main_folder = Path(main_folder)
if os.path.exists(path_to_main_folder):
    shutil.rmtree(path_to_main_folder)
path_to_main_folder.mkdir()

path_to_second_folder = Path(second_folder)
if os.path.exists(path_to_second_folder):
    shutil.rmtree(path_to_second_folder)
path_to_second_folder.mkdir()


### Select recordings ###
# generate selected recordings, change the if statement accordingly
with open(recordings,'r', encoding='utf-8') as f_in, open(selected_recordings,'w', encoding='utf-8') as f_out:
    for line in f_in:
        w_lst = line.split()
        if (w_lst[3] == '1') and (w_lst[2] == 'comp-q'):
            f_out.write(line)

### Directory management 2 ###
# create folders if not exist, remove folders if exist
folder_lst = [prompt_folder, ort_folder, wav_folder, second_wav_folder, wav_folder_untrimmed, second_ort_folder
              # adapt_dir, adapt_orts, adapt_prompts
              ]
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

# put selected recordings .wavs in my folder
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


def split_save_stories(textgrid_list, wav_folder, second_wav_folder, wav_folder_untrimmed, prompt_folder, ort_folder, second_ort_folder):
    """
    Method that takes JASMIN comp-q G1 files and segments them into 1st and 2nd story;
    1st includes prompts, 2nd does not.
    Segments for 1st story are based on prompt start and end times.
    Segments for 2nd story are created based on periods, with the exception of a string ending in
    variations of 'uh(m)...'. Segments that are less than 0.5s apart are merged.
    """

    # Var counting number of segments merged when less than some amount of time apart. Default 0.5s.
    delta_skipped = 0

    # Iterate over TextGrid files
    for name in textgrid_list:
        file = open(name, 'r', encoding='utf8').readlines()
        # get speaker id from TextGrid file name
        basename = name.split('.')[0].split('/')[-1]

        # declare some vars to use later
        number = 1  # segment number for this speaker id
        transcript = []
        transcript_text = ""
        # words to exclude from segments
        ignore_words = {'',
                        'ggg', 'ggg.', '!ggg.', 'xxx', 'xxx.', '!xxx',
                        'uh', 'uh.', 'uh..', 'uh...', 'uhm', 'uhm.', 'uhm..', 'uhm...'}

        # Initiate these variables
        transcripts_start = 0; transcripts_end = 0; prompts_start = 0; prompts_end = 0
        # Iterate over lines in .TextGrid file to determine location of transcript and prompt tiers
        for line in range(len(file)):
            if 'item [1]' in file[line]:
                transcripts_start = line
            if 'item [2]' in file[line]:
                transcripts_end = line-1
            if 'item [4]' in file[line]:
                prompts_start = line+6
            if 'item [5]' in file[line]:
                prompts_end = line-1

        # iterate over prompts first to get 1st story
        for line in range(prompts_start, prompts_end):
            # find prompt text intervals, starting at the first word
            if ('text =' in file[line]) and ('name =' not in file[line-7]):
                prompt = re.findall('"([^"]*)"', file[line])[0]
                # ignore empty prompt intervals
                if prompt != "":
                    # store prompt start and end times
                    xmin_prompt = round(float(re.findall("\d+\.?\d*", file[line-2])[0]), 4)
                    xmax_prompt = round(float(re.findall("\d+\.?\d*", file[line-1])[0]), 4)

                    # store prompt end time with 2 decimals for later end-of-prompt check
                    xmax_prompt_split = format(xmax_prompt, '.2f')

                    # crop segment from wav file and pad 0.3s silence on each end
                    os.system(f"sox {wav_folder}{basename}.wav {wav_folder}{basename}_1_{str(number).zfill(3)}.wav trim {xmin_prompt} ={xmax_prompt} pad 0.3 0.3")

                    # write prompt string to file
                    with open(f"{prompt_folder}{basename}_1_{str(number).zfill(3)}.prompt", 'w', encoding='utf-8') as prompt_file:
                        prompt_file.write(prompt)

                    # now iterate over manual transcriptions within prompts frame
                    for line in range(transcripts_start, transcripts_end):
                        if ('xmin =' in file[line]) and ('name =' not in file[line-5]):
                            # store word start and end times
                            xmin = round(float(re.findall("\d+\.?\d*", file[line])[0]), 4)
                            xmax = round(float(re.findall("\d+\.?\d*", file[line+1])[0]), 4)

                            # store word end time with 2 decimals for later end-of-prompt check
                            xmax_split = format(xmax, '.2f')

                            # check if current transcript word is within prompt timeframe
                            if (xmin >= xmin_prompt) and (xmax <= xmax_prompt):
                                word = re.findall('"([^"]*)"', file[line+2])[0]

                                # store current word in transcript
                                transcript.append(word)
                                # check if end of word time = end of prompt time
                                if xmax_split == xmax_prompt_split:
                                    for word in transcript:
                                        if word != "":  # ignore empty strings
                                            # add word to transcript
                                            transcript_text += word + ' '
                                    # write transcript string to file
                                    with open(f"{ort_folder}{basename}_1_{str(number).zfill(3)}.ort", 'w', encoding='utf-8') as transcript_file:
                                        transcript_file.write(transcript_text)

                                    # reset transcript, transcript string and segment counter
                                    transcript_text = ""
                                    transcript = []
                                    number += 1
                    # print()
        # iterate over manual transcriptions again but this time post prompts for 2nd stories
        number = 1  # reset segment counter
        for line in range(transcripts_start, transcripts_end):
            if 'xmin =' in file[line]:
                # store word start time
                xmin = round((float(re.findall("\d+\.?\d*", file[line])[0])), 4)
                # make sure we only use what is said after the last prompt is finished (= 2nd story)
                if xmin > xmax_prompt:
                    # store word end time
                    xmax = round(float(re.findall("\d+\.?\d*", file[line+1])[0]), 4)
                    word = re.findall('"([^"]*)"', file[line+2])[0]
                    # exclude words from ignore set
                    if word not in ignore_words:
                        # store word + start time + end time in a 3-tuple list
                        transcript.append([word, xmin, xmax])
                        # check time since prev segment if current segment is only a single word with '...'
                        if ('...' in word) and (len(transcript) > 1):
                            delta = transcript[-1][1] - transcript[-2][2]
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
                            with open(f"{second_ort_folder}{basename}_2_{str(number).zfill(3)}.ort", 'w', encoding='utf-8') as transcript_file:
                                transcript_file.write(transcript_text)

                            # crop segment from wav file and pad 0.3s silence on each end
                            os.system(f"sox {wav_folder}{basename}.wav {second_wav_folder}{basename}_2_{str(number).zfill(3)}.wav trim {start} ={end} pad 0.3 0.3")

                            # reset transcript, string and segment counter
                            transcript = []
                            transcript_text = ""
                            number += 1

        # move untrimmed files
        os.system(f"mv {wav_folder}{basename}.wav {wav_folder_untrimmed}{basename}.wav")

    # print number of segments merged based on delta
    # print(f"'...' deltas skipped: {delta_skipped}")


print('wav_file_lst',len(wav_file_lst))
for j in wav_file_lst:
    # print(j)
    shutil.copy(j, wav_folder)

print('textgrid_file_lst', len(tg_file_lst))

# generate segments
print("Segmenting...")
split_save_stories(tg_file_lst, wav_folder, second_wav_folder, wav_folder_untrimmed, prompt_folder, ort_folder, second_ort_folder)

# normalise manual transcriptions, prompts for G1-1 and G1-2
print("String normalisation...")
os.system(f'python3 string_norm.py {ort_folder} {ort_folder}')
os.system(f'python3 string_norm.py {prompt_folder} {prompt_folder}')
os.system(f'python3 string_norm.py {second_ort_folder} {second_ort_folder}')

# os.system(f'python3 string_norm.py {prompt_folder} {adapt_prompts} -u False')
# os.system(f'python3 string_norm.py {ort_folder} {adapt_orts} -u False')
