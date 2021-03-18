### Basic imports
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import sounddevice as sd


print(80*"=")
print("|| MSM INITIALIZATION")
print(80*"=")

### Directory paths
print("Setting paths...")
if sys.platform == "linux":
    PROJ_DIR = Path.home()/"Sync"/"KiddLab"/"MSM"
    BUGS_DIR = Path.home()/"Sync"/"Sounds"/"BUC-Mx_2014_With8Conjunctions"
    SIGTOOLS_DIR = Path.home()/"Sync"/"Python"/"sigtools"
elif sys.platform == "win32":
    sd.default.device = "ASIO Hammerfall DSP"
    PROJ_DIR = Path("K:/")/"Cho"/"MSM"
    BUGS_DIR = Path("K:/")/"Cho"/"BUC-Mx_2014_With8Conjunctions"
    SIGTOOLS_DIR = Path("K:/")/"Cho"/"sigtools"
else:
    raise ValueError("\nunexpected operating system!\nuse 'linux' or 'win32'")
sys.path.append(str(SIGTOOLS_DIR))
DATA_DIR = PROJ_DIR/"data"
STIM_DIR = PROJ_DIR/"assets"/"stimuli"
IMGS_DIR = PROJ_DIR/"assets"/"img"


### sigtools imports
print("Importing sigtools...")
from sigtools.utils import *
from sigtools.sounds import *
from sigtools.representations import *
from sigtools.processing import *
from sigtools.spatialization import *


### Set up sounddevice
print("Setting up sounddevice...")
sd.default.channels = 2


### Level adjustments
# Headphone transfer function
print("Importing level adjustments...")
FFT_FREQ = np.loadtxt(PROJ_DIR/"assets"/"headphone_calibration"/"freq.dat")
MAG_SPEC = np.loadtxt(PROJ_DIR/"assets"/"headphone_calibration"/"smooth_mag.dat")
SCALED_SPEC = MAG_SPEC + 15 + 10*np.log10(len(FFT_FREQ)) - 3

# Level adjustments for audibility across frequency
HL_FREQ = np.array([ 125,  160,  200,  250,  315,  400,  500,  630,
                     750,  800, 1000, 1250, 1500, 1600, 2000, 2500,
                    3000, 3150, 4000, 5000, 6000, 6300, 8000])
HL_to_SPL = np.array([45.0, 38.5, 32.5, 27.0, 22.0, 17.0, 13.5, 10.5,
                       9.0,  8.5,  7.5,  7.5,  7.5,  8.0,  9.0, 10.5,
                      11.5, 11.5, 12.0, 11.0, 16.0, 21.0, 15.5])


### Definitions for BUG corpus
# Define eligible words and talkers
# Exclude the following talkers based on Gin's email from 05/03/19:
#   5M, 12M, 4F, 10F
print("Setting eligible BUG words...")
ALL_MALE_TALKERS   = ["1M", "2M", "3M", "4M",   "5M",
                      "7M", "8M", "9M", "10M", "11M"       ]
ALL_FEMALE_TALKERS = ["1F", "2F", "3F",         "5F", "6F",
                      "7F", "8F", "9F",        "11F", "12F"]
ALL_TALKERS = ALL_MALE_TALKERS + ALL_FEMALE_TALKERS
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
ELIGIBLE_BUG_SNDS = [SoundLoader( (BUGS_DIR/fn).with_suffix(".wav") )
                     for fn in ELIGIBLE_BUG_FILES]
ELIGIBLE_BUG_DICT = dict(zip(ELIGIBLE_BUG_FILES, ELIGIBLE_BUG_SNDS))


### Pre-computation for making speech-shaped noise
print("Preparing to create long-term spectrum matched noise...")
ALL_WORDS_SUM = sum(zeropad_sounds(ELIGIBLE_BUG_SNDS))
ALL_WORDS_SPECT = MagnitudeSpectrum(ALL_WORDS_SUM)


### Definitions for tone pattern synthesis
print("Set values for tone pattern synthesis...")
PATTERN_TYPES = ["CONSTANT", "RISING", "FALLING",
                 "ALTERNATING", "STEP-UP", "STEP-DOWN"]
# CENTER_FREQS = np.array([ 215,  269,  336,  420,  525,  656,  820, 1026,
#                          1282, 1602, 2003, 2504, 3129, 3912, 4890, 6612])
CENTER_FREQS = np.array([215, 269, 336, 420, 525, 656, 820, 1026, 1282, 1602])
MIN_BAND_VAL, MAX_BAND_VAL = -7, 7
BAND_VALUES = np.linspace(MIN_BAND_VAL, MAX_BAND_VAL, 8)
PATTERN_IMG_PATHS = [
    IMGS_DIR/"tone_pattern_constant.png",
    IMGS_DIR/"tone_pattern_rising.png",
    IMGS_DIR/"tone_pattern_falling.png",
    IMGS_DIR/"tone_pattern_alternating_UP_DOWN.png",
    IMGS_DIR/"tone_pattern_step_up.png",
    IMGS_DIR/"tone_pattern_step_down.png"
]
PATTERN_SMALL_IMG_PATHS = [
    IMGS_DIR/"tone_pattern_constant_small.png",
    IMGS_DIR/"tone_pattern_rising_small.png",
    IMGS_DIR/"tone_pattern_falling_small.png",
    IMGS_DIR/"tone_pattern_alternating_UP_DOWN_small.png",
    IMGS_DIR/"tone_pattern_step_up_small.png",
    IMGS_DIR/"tone_pattern_step_down_small.png"
]


### Experimental conditions
from collections import namedtuple
print("Defining experimental conditions...")
Condition = namedtuple("Condition",
                       "stim_type target_alt_rate masker_alt_rate target_init_angle masker_init_angle")
# CONTROL_EM = [Condition("SEM", 0. , 0. , 45. , 45. ),
#               Condition("SEM", 0. , 0. , 63.5, 63.5)]
# EXPT_EV_EM = [Condition("SEM", 0.5, 0.5, None, None),
#               Condition("SEM", 1. , 1. , None, None),
#               Condition("SEM", 2. , 2. , None, None),
#               Condition("SEM", 5. , 5. , None, None)]
# EXPT_DV_EM = [Condition("SEM", 0.5, 5. , None, None),
#               Condition("SEM", 1. , 2. , None, None),
#               Condition("SEM", 2. , 1. , None, None),
#               Condition("SEM", 5. , 0.5, None, None)]
# CONTROL_IM = [Condition("SIM", 0. , 0. , 45. , 45. ),
#               Condition("SIM", 0. , 0. , 63.5, 63.5)]
# EXPT_EV_IM = [Condition("SIM", 0.5, 0.5, None, None),
#               Condition("SIM", 1. , 1. , None, None),
#               Condition("SIM", 2. , 2. , None, None),
#               Condition("SIM", 5. , 5. , None, None)]
# EXPT_DV_IM = [Condition("SIM", 0.5, 5. , None, None),
#               Condition("SIM", 1. , 2. , None, None),
#               Condition("SIM", 2. , 1. , None, None),
#               Condition("SIM", 5. , 0.5, None, None)]
# TRAIN_COND = [Condition("SEM", 0. , 0. , 63.5, 63.5),
#               Condition("SEM", 1. , 1. , None, None),
#               Condition("SEM", 1,   2. , None, None),
#               Condition("SEM", 0. , 0. , 45. , 45. ),
#               Condition("SIM", 0.5, 0.5, None, None),
#               Condition("SIM", 0.5, 5. , None, None)]
# ALL_CONDITIONS = CONTROL_EM + EXPT_EV_EM + EXPT_DV_EM \
#                + CONTROL_IM + EXPT_EV_IM + EXPT_DV_IM

# PILOT_V6_CONTROLS = [Condition("SEM", 0. , 0. , 45. , 45. ),
#                      Condition("SIM", 0. , 0. , 45. , 45. )]
# PILOT_V6_EV_EM = [Condition("SEM", 0.1, 0.1, None, None),
#                   Condition("SEM", 0.5, 0.5, None, None),
#                   Condition("SEM", 1. , 1. , None, None),
#                   Condition("SEM", 2. , 2. , None, None)]
# PILOT_V6_DV_EM = [Condition("SEM", 0.1, 2. , None, None),
#                   Condition("SEM", 0.5, 1. , None, None),
#                   Condition("SEM", 1. , 0.5, None, None),
#                   Condition("SEM", 2. , 0.1, None, None)]
# PILOT_V6_EV_IM = [Condition("SIM", 0.1, 0.1, None, None),
#                   Condition("SIM", 0.5, 0.5, None, None),
#                   Condition("SIM", 1. , 1. , None, None),
#                   Condition("SIM", 2. , 2. , None, None)]
# PILOT_V6_DV_IM = [Condition("SIM", 0.1, 2. , None, None),
#                   Condition("SIM", 0.5, 1. , None, None),
#                   Condition("SIM", 1. , 0.5, None, None),
#                   Condition("SIM", 2. , 0.1, None, None)]
# PILOT_V6_CONDS = PILOT_V6_CONTROLS \
#                + PILOT_V6_EV_EM + PILOT_V6_DV_EM \
#                + PILOT_V6_EV_IM + PILOT_V6_DV_IM

PILOT_V7_CONTROLS = [Condition("SEM", 0. , 0. , 45. , 45. ),
                     Condition("SIM", 0. , 0. , 45. , 45. )]
PILOT_V7_EV_EM = [Condition("SEM", 0.1, 0.1, None, None),
                  Condition("SEM", 0.5, 0.5, None, None),
                  Condition("SEM", 1. , 1. , None, None),
                  Condition("SEM", 2. , 2. , None, None)]
PILOT_V7_DV_EM = [Condition("SEM", 0.1, 2. , None, None),
                  Condition("SEM", 0.5, 1. , None, None),
                  Condition("SEM", 1. , 0.5, None, None),
                  Condition("SEM", 2. , 0.1, None, None)]
PILOT_V7_EV_IM = [Condition("SIM", 0.1, 0.1, None, None),
                  Condition("SIM", 0.5, 0.5, None, None),
                  Condition("SIM", 1. , 1. , None, None),
                  Condition("SIM", 2. , 2. , None, None)]
PILOT_V7_DV_IM = [Condition("SIM", 0.1, 2. , None, None),
                  Condition("SIM", 0.5, 1. , None, None),
                  Condition("SIM", 1. , 0.5, None, None),
                  Condition("SIM", 2. , 0.1, None, None)]
PILOT_V7_CONDS = PILOT_V7_CONTROLS \
               + PILOT_V7_EV_EM + PILOT_V7_DV_EM \
               + PILOT_V7_EV_IM + PILOT_V7_DV_IM


### Dataframe columns
STIM_COLUMNS = ["stim_num", "stim_type", "TMR",
                "src", "is_target", "pattern",
                "alt_rate", "init_angle", "init_dir_R"]
DATA_COLUMNS = ["run_num", "subject_ID", "stim_type",
                "block_num", "trial_num", "stim_num",
                "subj_response", "correct",
                "elapsed_time"]

print("Initialization complete!")
print(80*"=")
