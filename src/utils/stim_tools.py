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


def make_sentence(n_talkers, cue_name=None, syntax_condition="syntactic"):
    from numpy.random import choice
    # Randomly select target and masker talkers and words
    talkers = choice(ELIGIBLE_TALKERS, n_talkers, replace=False)
    if syntax_condition == "syntactic":
        sentence_words = \
            np.hstack([choice([name for name in NAMES if name != cue_name],
                                  (n_talkers, 1), replace=False),
                       choice(VERBS,      (n_talkers, 1), replace=False),
                       choice(NUMBERS,    (n_talkers, 1), replace=False),
                       choice(ADJECTIVES, (n_talkers, 1), replace=False),
                       choice(NOUNS,      (n_talkers, 1), replace=False)])
    elif syntax_condition == "random":
        non_names = VERBS + NUMBERS + ADJECTIVES + NOUNS
        sentence_words = \
            np.hstack([choice([name for name in NAMES if name != cue_name],
                                  (n_talkers, 1), replace=False),
                       choice(non_names, (n_talkers, 4), replace=False)])
    else:
        raise ValueError("invalid syntax_condition; choose 'syntactic' or 'random'")

    if cue_name: # If cue_name is given, change the first sentence to cue
        sentence_words[0, 0] = cue_name

    sentence_sounds = [ concat_sounds([ ELIGIBLE_BUG_DICT["_".join([word, talkers[i]])]
                                        for word in sentence_words[i, :] ])
                        for i in range(n_talkers) ]
    sentence_sounds = normalize_rms(sentence_sounds)
    sentence_words = [" ".join(sentence_words[i, :]).upper()
                      for i in range(n_talkers)]
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
    tone_sequence = [ramp_edges(PureTone(tone_dur, fs, freq), edge_dur)
                     for freq in freq_sequence]
    return normalize_rms([concat_sounds(tone_sequence)])[0]


def make_TP_sequence(n_seqs, seq_len=5, protected_delta=1, fs=44100, n_tones=8,
                     tone_dur=80e-3, edge_dur=20e-3, gap_dur=100e-3):
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
        curr_seq_list = [make_tone_pattern(pattern, fs, CFs[i], n_tones,
                                           tone_dur, edge_dur)
                         for pattern in patterns[i, :]]
        # insert silent gap between each tone pattern
        temp_list = (2*len(curr_seq_list) - 1)*[gap]
        temp_list[0::2] = curr_seq_list
        temp_list = [gap] + temp_list + [gap]
        tp_seqs.append(concat_sounds(temp_list))
    patterns = [" ".join(patterns[i, :]).upper() for i in range(len(tp_seqs))]
    return bands, patterns, tp_seqs


def add_SSN_to_snds(srcs, patterns, snds, difficulty_TMR, SSN_ramp_dur):
    # Adds speech shaped noise to each src
    # Assumes snds are already RMS normalized
    n_snds = len(snds)
    cues = [ELIGIBLE_BUG_DICT["_".join([patterns[i, 0], srcs[i]])]
            for i in range(n_snds)]
    cue_durs = [len(cue)/cue.fs for cue in cues]
    tail_durs = [len(snds[i][cue_durs[i]:])/cues[i].fs for i in range(n_snds)]
    silences = [Silence(cue_durs[i], cues[i].fs) for i in range(n_snds)]
    SSNs = [ALL_WORDS_SPECT.to_Noise(tail_durs[i], cues[i].fs)
            for i in range(n_snds)]
    SSNs = normalize_rms(SSNs)
    SSNs = [ramp_edges(SSN, SSN_ramp_dur) for SSN in SSNs]
    SSN_maskers = [concat_sounds([silences[i], SSNs[i]])
                   for i in range(n_snds)]
    snds = [sum(center_sounds([snds[i] + difficulty_TMR, SSN_maskers[i]]))
            for i in range(n_snds)]
    return normalize_rms(snds)


def make_circular_sinuisoidal_trajectory(spatial_resolution, T_dur, r, elev,
                                         traj_amplitude,
                                         traj_freq,
                                         traj_init_cycle,
                                         traj_displacement):
    """
    spatial_resolution: average points per degree over the whole trajectory
    T_dur: duration of the trajectory
    r: radius [cm]
    elev: elevation [degrees]
    traj_amplitude: peak-to-peak amplitude of the trajectory [deg]
    traj_freq: frequency of trajectory [Hz]
    traj_init_cycle: initial position of the trajectory in a cycle [0, 1)
    traj_displacement: center of the oscillation (i.e. displacement from origin)
    """
    N = int(180*spatial_resolution*T_dur*traj_freq) # number of spatial samples
    if N == 0: # handle static (i.e. zero) velocity case
        angular_traj = np.array([0])
        N = 1
    else:
        sin, pi = np.sin, np.pi
        A, B, C, D = traj_amplitude, traj_freq, traj_init_cycle, traj_displacement
        t = np.linspace(0, T_dur, N)
        angular_traj = A*sin(2*pi*B*(t + C/B)) + D
    hcc_coords = np.array([(r, elev, angle) for angle in angular_traj])
    hcc_coords_tuple = list(map(tuple, hcc_coords))
    rect_coords_tuple = [hcc_to_rect(*coords) for coords in hcc_coords_tuple]
    rect_coords = tuple_to_array(rect_coords_tuple)
    return rect_coords


def traj_to_theta(traj):
    """
    Utility function to convert the trajectory data to azimuthal angle in the
    frontal plane. Plot the returned array to visually confirm trajectory.
    """
    traj_tuple = list(map(tuple, traj))
    theta_list = [rect_to_hcc(*coord)[2] for coord in traj_tuple]
    corr_theta = [(360 - theta) if theta > 180 else -1*theta
                  for theta in theta_list]
    return np.array(corr_theta)


def choose_stim_for_block(stim_database, all_block_list, cond, n_trials_per_block):
    from functools import partial, reduce
    inner_merge = partial(pd.merge, how="inner")
    flatten = lambda t: [item for sublist in t for item in sublist] # flattens list of lists in double loop

    # Choose the subset of the stimulus database that satisfies the current conditions
    conditions = []
    conditions.append(stim_database[(stim_database["stim_type"] == cond.stim_type)])
    conditions.append(stim_database[(stim_database["is_target"] == True) &
                                    (stim_database["alt_rate"] == cond.target_alt_rate)])
    conditions.append(stim_database[(stim_database["is_target"] == False) &
                                    (stim_database["alt_rate"] == cond.masker_alt_rate)])
    if cond.target_init_angle: # if initial angle is specified in conditions, it will be not None
        conditions.append(stim_database[(stim_database["is_target"] == True) &
                                        (np.abs(stim_database["init_angle"]) == cond.target_init_angle)])
    if cond.masker_init_angle:
        conditions.append(stim_database[(stim_database["is_target"] == False) &
                                        (np.abs(stim_database["init_angle"]) == cond.masker_init_angle)])
    subsets = [stim_database.loc[stim_database["stim_num"].isin(cond["stim_num"])]
               for cond in conditions]
    conditioned_stim_database = reduce(inner_merge, subsets)

    # Determine the available stimuli by removing already used stimuli
    eligible_stim_num = conditioned_stim_database["stim_num"].unique()
    used_stim_num = [stim_tuple[1] for stim_tuple in flatten(all_block_list)]
    available_stim_num = list(set(eligible_stim_num) - set(used_stim_num))
    selected_stim_num = sorted(np.random.choice(available_stim_num, n_trials_per_block, replace=False))

    # Load the stimuli as sounds and insert into block
    srcs = [SoundLoader(STIM_DIR/("stim_" + str(stim_num).zfill(5) + ".wav"))
            for stim_num in selected_stim_num]
    pattern_items = [pattern.split(" ") for pattern in
                     stim_database.loc[(stim_database["stim_num"].isin(selected_stim_num)) &
                                       (stim_database["is_target"])]["pattern"]]
    stim_tuple = list(zip(srcs, selected_stim_num, pattern_items))
    np.random.shuffle(stim_tuple)
    return stim_tuple


def choose_stim_for_run(stim_database, curr_expt, n_trials_per_block):
    all_block_list = []
    for condition in curr_expt:
        curr_block_list = choose_stim_for_block(stim_database, all_block_list,
                                                condition, n_trials_per_block)
        all_block_list.append(curr_block_list)
    return all_block_list


# def set_stim_order(stim_database, task_type, n_srcs, conditions,
#                    n_blocks=None,
#                    n_trials_per_block_per_condition=None,
#                    n_trials_per_block=None,
#                    n_blocks_per_condition=None,
#                    randomize_within_block=True):
#     if randomize_within_block:
#         if n_trials_per_block or n_blocks_per_condition:
#             raise ValueError
#         n_trials_per_condition = n_blocks*n_trials_per_block_per_condition
#     else:
#         if n_blocks or n_trials_per_block_per_condition:
#             raise ValueError
#         n_trials_per_condition = n_trials_per_block*n_blocks_per_condition
#
#     # Find all stimuli that satisfy current conditions
#     temp = pd.DataFrame(columns=["cond", "stim_num", "pattern"])
#     for cond in conditions:
#         try:
#             if cond == "co-located":
#                 cond_subset = \
#                     stim_database[(stim_database["stim_type"] == task_type) &
#                                   (stim_database["n_srcs"] == n_srcs) &
#                                   (stim_database["is_target"]) &
#                                   (stim_database["alt_rate"] == 0) &
#                                   (stim_database["init_angle"] == 0)].sample(n_trials_per_condition)
#             elif cond == "plus_minus_90":
#                 cond_subset = \
#                     stim_database[(stim_database["stim_type"] == task_type) &
#                                   (stim_database["n_srcs"] == n_srcs) &
#                                   (stim_database["is_target"]) &
#                                   (stim_database["alt_rate"] == 0) &
#                                   (stim_database["init_angle"] != 0)].sample(n_trials_per_condition)
#             else:
#                 cond_subset = \
#                     stim_database[(stim_database["stim_type"] == task_type) &
#                                   (stim_database["n_srcs"] == n_srcs) &
#                                   (stim_database["is_target"]) &
#                                   (stim_database["alt_rate"] == cond)].sample(n_trials_per_condition)
#         except ValueError:
#             exception_str = ("insufficient number of unique stimuli for the "
#                              "specified number of trials")
#             raise ValueError(exception_str) from None
#         cond_subset = cond_subset[["stim_num", "pattern"]]
#         cond_subset.insert(0, "cond", len(cond_subset)*[cond])
#         temp = temp.append(cond_subset)
#
#     # Set stimulus order - strategy is to randomly draw from temp
#     # and remove the drawn samples
#     run_stim_order = []
#     if randomize_within_block:
#         for block_num in range(n_blocks):
#             curr_block = []
#             for cond in conditions:
#                 curr_cond_df = temp[temp["cond"] == cond]
#                 sampled = curr_cond_df.sample(n_trials_per_block_per_condition,
#                                               replace=False)
#                 temp = temp.drop(sampled.index) # removed the drawn rows
#                 sampled_stim_nums = sampled["stim_num"].values.astype(int)
#                 sampled_stim_patterns = sampled["pattern"].values
#                 sampled_stim_patterns = [pattern.split(" ")
#                                          for pattern in sampled_stim_patterns]
#                 sampled_stims = []
#                 for stim_num in sampled_stim_nums:
#                     stim_path = STIM_DIR/("stim_" + str(stim_num).zfill(5) + ".wav")
#                     stimulus = SoundLoader(stim_path)
#                     sampled_stims.append(stimulus)
#                 curr_block += list(zip(sampled_stims,
#                                        sampled_stim_nums,
#                                        sampled_stim_patterns))
#             np.random.shuffle(curr_block)
#             run_stim_order.append(curr_block)
#     else: # if not randomized within block
#         for _ in range(n_blocks_per_condition):
#             np.random.shuffle(conditions)
#             for cond in conditions:
#                 curr_block = []
#                 curr_cond_df = temp[temp["cond"] == cond]
#                 sampled = curr_cond_df.sample(n_trials_per_block,
#                                               replace=False)
#                 temp = temp.drop(sampled.index) # removed the drawn rows
#                 sampled_stim_nums = sampled["stim_num"].values.astype(int)
#                 sampled_stim_patterns = sampled["pattern"].values
#                 sampled_stim_patterns = [pattern.split(" ")
#                                          for pattern in sampled_stim_patterns]
#                 sampled_stims = []
#                 for stim_num in sampled_stim_nums:
#                     stim_path = STIM_DIR/("stim_" + str(stim_num).zfill(5) + ".wav")
#                     stimulus = SoundLoader(stim_path)
#                     sampled_stims.append(stimulus)
#                 curr_block = list(zip(sampled_stims,
#                                       sampled_stim_nums,
#                                       sampled_stim_patterns))
#                 np.random.shuffle(curr_block)
#                 run_stim_order.append(curr_block)
#     return run_stim_order
#
#
# def validate_parameters(stim_database, task_type, n_srcs, conditions):
#     for cond in conditions:
#         if cond == "co-located":
#             curr_cond_df = \
#                 stim_database[(stim_database["stim_type"] == task_type) &
#                               (stim_database["n_srcs"] == n_srcs) &
#                               (stim_database["is_target"] == True) &
#                               (stim_database["alt_rate"] == 0) &
#                               (stim_database["init_angle"] == 0)]
#         elif cond == "plus_minus_90":
#             curr_cond_df = \
#                 stim_database[(stim_database["stim_type"] == task_type) &
#                               (stim_database["n_srcs"] == n_srcs) &
#                               (stim_database["is_target"] == True) &
#                               (stim_database["alt_rate"] == 0) &
#                               (stim_database["init_angle"] != 0)]
#         else:
#             curr_cond_df = \
#                 stim_database[(stim_database["stim_type"] == task_type) &
#                               (stim_database["n_srcs"] == n_srcs) &
#                               (stim_database["is_target"] == True) &
#                               (stim_database["alt_rate"] == cond)]
#         if len(curr_cond_df) == 0:
#             if type(cond) == str:
#                 exception_str = ("no stimulus with combination {:s}, "
#                                  "{:d} sources, and {:s} available").format(
#                                  task_type, n_srcs, cond)
#             else:
#                 exception_str = ("no stimulus with combination {:s}, "
#                                  "{:d} sources, and {:.1f} Hz available").format(
#                                  task_type, n_srcs, cond)
#             raise ValueError(exception_str)
