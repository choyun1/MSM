### Basic imports
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import sounddevice as sd


### Directory paths
if sys.platform == "linux":
    PROJ_DIR = Path.home()/"Sync"/"KiddLab"/"MSM"
    BUGS_DIR = Path.home()/"Sync"/"Sounds"/"BUC-Mx_2014_With8Conjunctions"
    sys.path.insert(0, "/home/acho/Sync/Python/sigtools")
elif sys.platform == "win32":
    PROJ_DIR = Path("K:")/"Cho"/"MSM"
    BUGS_DIR = Path("K:")/"Cho"/"BUC-Mx_2014_With8Conjunctions"
    sys.path.insert(0, "K:\\Cho\\sigtools")
else:
    raise ValueError("\nunexpected operating system! use 'linux' or 'win32'")
DATA_DIR = PROJ_DIR/"data"
STIM_DIR = PROJ_DIR/"assets"/"stimuli"


### sigtools imports
from sigtools.utils import *
from sigtools.sounds import *
from sigtools.processing import *
from sigtools.representations import *
from sigtools.spatialization import *


### Set up sounddevice
# sd.default.device = "ASIO Hammerfall DSP"
sd.default.channels = 2


### Level adjustments for headphone transfer function
L_ADJ_DIR = PROJ_DIR/"assets"/"headphone_calibration"
FFT_FREQ = np.loadtxt(L_ADJ_DIR/"freq.dat")
MAG_SPEC = np.loadtxt(L_ADJ_DIR/"smooth_mag.dat")
SCALED_SPEC = MAG_SPEC + 15 + 10*np.log10(len(FFT_FREQ)) - 3


### Level adjustments for audibility across frequency
HL_FREQ = np.array([ 125,  160,  200,  250,  315,  400,  500,  630,
                     750,  800, 1000, 1250, 1500, 1600, 2000, 2500,
                    3000, 3150, 4000, 5000, 6000, 6300, 8000])
HL_to_SPL = np.array([45.0, 38.5, 32.5, 27.0, 22.0, 17.0, 13.5, 10.5,
                       9.0,  8.5,  7.5,  7.5,  7.5,  8.0,  9.0, 10.5,
                      11.5, 11.5, 12.0, 11.0, 16.0, 21.0, 15.5])


### Definitions for BUG corpus
# Define eligible words and talkers
# Exclude the following talkers based on an email from Gin Best on 05/03/19:
#   5M, 12M, 4F, 10F
ALL_MALE_TALKERS   = ["1M", "2M", "3M", "4M",   "5M",
                      "7M", "8M", "9M", "10M", "11M"       ]
ALL_FEMALE_TALKERS = ["1F", "2F", "3F",         "5F", "6F",
                      "7F", "8F", "9F",        "11F", "12F"]
ALL_POSSIBLE_TALKERS = ALL_MALE_TALKERS + ALL_FEMALE_TALKERS
ELIGIBLE_TALKERS = ALL_MALE_TALKERS

NAMES = ["Bob", "Jill", "Jane", "Lynn", "Mike", "Pat", "Sam", "Sue"]
VERBS = ["bought", "gave", "found", "held", "lost", "saw", "sold", "took"]
NUMBERS = ["two", "three", "four", "five", "six", "eight", "nine", "ten"]
ADJECTIVES = ["big", "cheap", "green", "hot", "new", "old", "red", "small"]
NOUNS = ["bags", "cards", "gloves", "hats", "pens", "shoes", "socks", "toys"]
CONJUNCTIONS = ["and", "but", "if", "or", "then", "when", "where", "while"]
ALL_WORDS = NAMES + VERBS + NUMBERS + ADJECTIVES + NOUNS + CONJUNCTIONS
ELIGIBLE_WORDS = ALL_WORDS

ALL_BUG_FILES = [fn.stem for fn in BUGS_DIR.glob("*.wav")]
ELIGIBLE_BUG_FILES = [fn for fn in ALL_BUG_FILES
                          if fn.split("_")[0] in ELIGIBLE_WORDS
                         and fn.split("_")[1] in ELIGIBLE_TALKERS]
ELIGIBLE_BUG_SNDS  = [SoundLoader( (BUGS_DIR/fn).with_suffix(".wav") )
                      for fn in ELIGIBLE_BUG_FILES]
ELIGIBLE_BUG_DICT  = dict(zip(ELIGIBLE_BUG_FILES, ELIGIBLE_BUG_SNDS))


### Dataframe columns
EXIT_KEYS = ("q", "escape")
STIM_COLUMNS = ["stim_type",
                "alternation_rate",
                "target_talker", "target_sentence",
                "init_target_position", "init_target_moving_right",
                "masker_talker", "masker_sentence",
                "init_masker_position", "init_masker_moving_right"]
DATA_COLUMNS = ["subject_ID",
                "run_num", "block_num", "trial_num",
                "target_talker", "target_sentence",
                "masker_talker", "masker_sentence",
                "subj_response", "correct",
                "elapsed_time",
                "stim_file"]
