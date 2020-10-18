from utils.init_constants import *


def HL_adjustment(f):
    return np.interp(f, HL_FREQ, HL_to_SPL)


def compute_attenuation(level, freq=None):
    if freq is None: # broadband
        ref_level = 133
    else:
        ref_level = np.interp(freq, FFT_FREQ, SCALED_SPEC)
    db_atten = level - ref_level
    return db_atten


def make_sentence(n_talkers):
    # Randomly select target and masker talkers and words
    talkers = np.random.choice(ELIGIBLE_TALKERS, n_talkers, replace=False)
    sentence_words = \
        np.hstack( [np.random.choice(list(set(NAMES) - set(["Sue"])),
                                     (n_talkers, 1), replace=False),
                    np.random.choice(VERBS, (n_talkers, 1), replace=False),
                    np.random.choice(NUMBERS, (n_talkers, 1), replace=False),
                    np.random.choice(ADJECTIVES, (n_talkers, 1), replace=False),
                    np.random.choice(NOUNS, (n_talkers, 1), replace=False)] )
    sentence_words[0, 0] = "Sue"
    sentence_sounds = [ concat_sounds([ ELIGIBLE_BUG_DICT["_".join([word, talkers[i]])]
                                        for word in sentence_words[i, :] ])
                        for i in range(n_talkers) ]
    sentence_sounds = normalize_rms(sentence_sounds)
    return talkers, sentence_words, sentence_sounds


def make_tone_pattern(pattern, fs, CF, n_tones, tone_dur, edge_dur):
    """Make tone pattern"""
    pattern = pattern.upper()
    # Define the sequence of % deviation from CF for the target pattern
    if pattern == "CONSTANT": # constant
        band_value_sequence = n_tones*[np.random.choice(BAND_VALUES)]
    elif pattern == "RISING": # rising
        band_value_sequence = np.linspace(MIN_BAND_VAL, MAX_BAND_VAL, n_tones)
    elif pattern == "FALLING": # falling
        band_value_sequence = np.linspace(MAX_BAND_VAL, MIN_BAND_VAL, n_tones)
    elif pattern == "ALTERNATING": # alternating
        from itertools import cycle
        if np.random.randint(0, 2) == 0: # low high low high ...
            alternating_cycle = cycle([MIN_BAND_VAL, MAX_BAND_VAL])
        else: # high low high low ...
            alternating_cycle = cycle([MAX_BAND_VAL, MIN_BAND_VAL])
        band_value_sequence = [next(alternating_cycle) for _ in range(n_tones)]
    elif pattern == "STEP-UP" or pattern == "STEP-DOWN": # step up or step down
        if round(n_tones) % 2 == 0: # even number of tones
            lower_half = n_tones//2*[MIN_BAND_VAL]
            upper_half = n_tones//2*[MAX_BAND_VAL]
        else: # odd number of tones
            lower_half = ((n_tones + 1)//2 - 1)*[MIN_BAND_VAL]
            upper_half = ((n_tones + 1)//2)*[MAX_BAND_VAL]

        if pattern == "STEP-UP": # step up
            band_value_sequence = lower_half + upper_half
        else: # step down
            band_value_sequence = upper_half + lower_half
    else:
        raise ValueError("invalid tone pattern")

    # Generate the target pattern
    freq_sequence = [(1 + band_value/100)*CF
                     for band_value in band_value_sequence]
    tone_sequence = [ramp_edges(PureTone(tone_dur, fs, freq), edge_dur) for freq in freq_sequence]
    return normalize_rms([concat_sounds(tone_sequence)])[0]


def make_TP_sequence(n_seqs, seq_len=5, protected_delta=1,
                     fs=44100, n_tones=8, tone_dur=80e-3, edge_dur=20e-3, gap_dur=100e-3):
    # Choose frequency bands
    if n_seqs >= len(CENTER_FREQS) - 2*protected_delta:
        raise ValueError("too many pattern sequences requested")
    bands_chosen = False
    while not bands_chosen:
        bands_draw = np.random.choice(len(CENTER_FREQS), n_seqs, replace=False)
        band_differences_from_target = np.array([abs(bands_draw[i] - bands_draw[0])
                                                 for i in range(1, n_seqs)])
        if not any(band_differences_from_target <= protected_delta):
            bands_chosen = True
    CFs = CENTER_FREQS[bands_draw]
    bands = np.array(["band_" + str(band_num) for band_num in bands_draw])

    # Choose the patterns
    patterns = np.random.choice(PATTERN_TYPES, (n_seqs, seq_len))
    patterns[:, 0] = np.random.choice(list(set(PATTERN_TYPES) - set(["CONSTANT"])),
                                      n_seqs, replace=False)
    patterns[0, 0] = "CONSTANT"

    # Make the pattern sequences
    gap = Silence(gap_dur, fs)
    tp_seqs = []
    for i in range(n_seqs):
        curr_seq_list = [make_tone_pattern(pattern, fs, CFs[i], n_tones, tone_dur, edge_dur)
                         for pattern in patterns[i, :]]
        # insert silent gap between each tone pattern
        temp_list = (2*len(curr_seq_list) - 1)*[gap]
        temp_list[0::2] = curr_seq_list
        temp_list = [gap] + temp_list + [gap]
        tp_seqs.append(concat_sounds(temp_list))
    return bands, patterns, tp_seqs


def make_circular_sinuisoidal_trajectory(r, elev, init_angle,
                                         T_dur, freq, spatial_resolution):
    """
    r = radius [cm]
    elev = elevation [degrees]
    init_angle = initial angle [degrees]; based on sine wave
    T_dur = duration of the trajectory
    freq = frequency of oscillation
    spatial_resolution = average points per degree over the whole trajectory
    """
    N = int(180*spatial_resolution*T_dur*freq) # number of spatial samples
    A = 90
    t = np.linspace(0, T_dur, N)
    angular_traj = A*np.sin(2*np.pi*(freq*t + init_angle/360))
    hcc_coords = np.array([(r, elev, angle) for angle in angular_traj])
    hcc_coords_tuple = list(map(tuple, hcc_coords))
    rect_coords_tuple = [hcc_to_rect(*coords) for coords in hcc_coords_tuple]
    rect_coords = tuple_to_array(rect_coords_tuple)
    return rect_coords


def set_stim_order(stim_database, n_srcs, task_type, conditions,
                   n_blocks=None,
                   n_trials_per_block_per_condition=None,
                   n_trials_per_block=None,
                   n_blocks_per_condition=None,
                   randomize_within_block=True):
    if randomize_within_block:
        if n_trials_per_block or n_blocks_per_condition:
            raise ValueError
        n_trials_per_condition = n_blocks*n_trials_per_block_per_condition
    else:
        if n_blocks or n_trials_per_block_per_condition:
            raise ValueError
        n_trials_per_condition = n_trials_per_block*n_blocks_per_condition

    temp = pd.DataFrame(columns=["cond", "stim_num", "pattern"])
    for cond in conditions:
        if cond == "co-located":
            cond_subset = \
                stim_database[(stim_database["n_srcs"] == n_srcs) &
                              (stim_database["stim_type"] == task_type) &
                              (stim_database["is_target"]) &
                              (stim_database["alt_rate"] == 0) &
                              (stim_database["init_angle"] == 0)].sample(n_trials_per_condition)
        elif cond == "plus_minus_90":
            cond_subset = \
                stim_database[(stim_database["n_srcs"] == n_srcs) &
                              (stim_database["stim_type"] == task_type) &
                              (stim_database["is_target"]) &
                              (stim_database["alt_rate"] == 0) &
                              (stim_database["init_angle"] != 0)].sample(n_trials_per_condition)
        else:
            cond_subset = \
                stim_database[(stim_database["n_srcs"] == n_srcs) &
                              (stim_database["stim_type"] == task_type) &
                              (stim_database["is_target"]) &
                              (stim_database["alt_rate"] == cond)].sample(n_trials_per_condition)
        cond_subset = cond_subset[["stim_num", "pattern"]]
        cond_subset.insert(0, "cond", len(cond_subset)*[str(cond)])
        temp = temp.append(cond_subset)

    # Set stimulus order - strategy is to randomly draw from temp
    # and remove the drawn samples
    run_stim_order = []
    if randomize_within_block:
        for block_num in range(n_blocks):
            curr_block = []
            for cond in conditions:
                curr_cond_df = temp[temp["cond"] == cond]
                sampled = curr_cond_df.sample(n_trials_per_block_per_condition, replace=False)
                temp = temp.drop(sampled.index) # removed the drawn rows
                sampled_stim_nums = sampled["stim_num"].values.astype(int)
                sampled_stim_patterns = sampled["pattern"].values
                sampled_stim_patterns = [pattern.split(" ") for pattern in sampled_stim_patterns]
                sampled_stims = []
                for stim_num in sampled_stim_nums:
                    stim_path = STIM_DIR/("stim_" + str(stim_num).zfill(5) + ".wav")
                    stimulus = SoundLoader(stim_path)
                    sampled_stims.append(stimulus)
                curr_block += list(zip(sampled_stims, sampled_stim_nums, sampled_stim_patterns))
            np.random.shuffle(curr_block)
            run_stim_order.append(curr_block)
    else: # if not randomized within block
        for _ in range(n_blocks_per_condition):
            np.random.shuffle(conditions)
            for cond in conditions:
                curr_block = []
                curr_cond_df = temp[temp["cond"] == cond]
                sampled = curr_cond_df.sample(n_trials_per_block, replace=False)
                temp = temp.drop(sampled.index) # removed the drawn rows
                sampled_stim_nums = sampled["stim_num"].values.astype(int)
                sampled_stim_patterns = sampled["pattern"].values
                sampled_stim_patterns = [pattern.split(" ") for pattern in sampled_stim_patterns]
                sampled_stims = []
                for stim_num in sampled_stim_nums:
                    stim_path = STIM_DIR/("stim_" + str(stim_num).zfill(5) + ".wav")
                    stimulus = SoundLoader(stim_path)
                    sampled_stims.append(stimulus)
                curr_block = list(zip(sampled_stims, sampled_stim_nums, sampled_stim_patterns))
                np.random.shuffle(curr_block)
                run_stim_order.append(curr_block)
    return run_stim_order
