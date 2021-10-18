from utils.init_constants import *


def convert_datatime_to_timestamp(datetime_obj):
    timestr = "UTC {:s}-{:s}-{:s} {:s}:{:s}:{:s}.{:s}".format(
        datetime_obj.strftime("%Y").zfill(4),
        datetime_obj.strftime("%m").zfill(2),
        datetime_obj.strftime("%d").zfill(2),
        datetime_obj.strftime("%H").zfill(2),
        datetime_obj.strftime("%M").zfill(2),
        datetime_obj.strftime("%S").zfill(2),
        str(datetime_obj.microsecond//1000).zfill(3))
    return timestr


def HL_adjustment(f):
    return np.interp(f, HL_FREQ, HL_to_SPL)


def compute_attenuation(level, freq=None):
    if freq is None:  # broadband
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
        raise ValueError(
            "invalid syntax_condition; choose 'syntactic' or 'random'")

    if cue_name:  # If cue_name is given, change the first sentence to cue
        sentence_words[0, 0] = cue_name

    sentence_sounds = [concat_sounds([ELIGIBLE_BUG_DICT["_".join([word, talkers[i]])]
                                      for word in sentence_words[i, :]])
                       for i in range(n_talkers)]
    sentence_sounds = normalize_rms(sentence_sounds)
    sentence_words = [" ".join(sentence_words[i, :]).upper()
                      for i in range(n_talkers)]
    return talkers, sentence_words, sentence_sounds


def make_tone_pattern(pattern, fs, CF, n_tones, tone_dur, edge_dur):
    """Make tone pattern"""
    pattern = pattern.upper()
    # Define the sequence of % deviation from CF for the target pattern
    if pattern == "CONSTANT":  # constant
        band_value_sequence = n_tones*[np.random.choice(BAND_VALUES)]
    elif pattern == "RISING":  # rising
        band_value_sequence = np.linspace(MIN_BAND_VAL, MAX_BAND_VAL, n_tones)
    elif pattern == "FALLING":  # falling
        band_value_sequence = np.linspace(MAX_BAND_VAL, MIN_BAND_VAL, n_tones)
    elif pattern == "ALTERNATING":  # alternating
        from itertools import cycle
        if np.random.randint(0, 2) == 0:  # low high low high ...
            alternating_cycle = cycle([MIN_BAND_VAL, MAX_BAND_VAL])
        else:  # high low high low ...
            alternating_cycle = cycle([MAX_BAND_VAL, MIN_BAND_VAL])
        band_value_sequence = [next(alternating_cycle) for _ in range(n_tones)]
    elif pattern == "STEP-UP" or pattern == "STEP-DOWN":  # step up or step down
        if round(n_tones) % 2 == 0:  # even number of tones
            lower_half = n_tones//2*[MIN_BAND_VAL]
            upper_half = n_tones//2*[MAX_BAND_VAL]
        else:  # odd number of tones
            lower_half = ((n_tones + 1)//2 - 1)*[MIN_BAND_VAL]
            upper_half = ((n_tones + 1)//2)*[MAX_BAND_VAL]

        if pattern == "STEP-UP":  # step up
            band_value_sequence = lower_half + upper_half
        else:  # step down
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
    traj_displacement: center of the oscillation [deg] (i.e. displacement from origin)
    """
    N = int(180*spatial_resolution*T_dur
            * traj_freq)  # number of spatial samples
    if N == 0:  # handle static (i.e. zero) velocity case
        angular_traj = np.array([traj_displacement])
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


def generate_latin_square(n, balanced=False):
    """
    Williams, E. J. (1949): Experimental designs balanced
    for the estimation of residual effects of treatments.
    """
    l = [[((1 + j//2 if j % 2 == 1 else n - j//2) + i) % n + 1
          for j in range(n)]
         for i in range(n)]
    if balanced:
        if n % 2 == 1:  # Repeat reversed for odd n
            l += [seq[::-1] for seq in l]
        return np.array(l) - 1
    else:
        l = np.array(l) - 1
        l[1:] = np.random.permutation(l[1:])  # permute all rows except first
        return l


def compute_n_trials(n_tasks,
                     n_amps,
                     n_trials_per_task_per_amp,
                     n_trials_per_block_per_amp):
    if n_trials_per_task_per_amp % n_trials_per_block_per_amp != 0:
        raise ValueError("invalid n_trials_per_block_per_amp")
    else:
        n_blocks_per_task = int(
            n_trials_per_task_per_amp/n_trials_per_block_per_amp)
    n_blocks = n_blocks_per_task*n_tasks
    n_trials = n_trials_per_task_per_amp*n_amps*n_tasks
    n_trials_per_block = int(n_trials/n_blocks)
    return n_blocks_per_task, n_blocks, n_trials, n_trials_per_block


def generate_task_order(n_tasks, n_blocks_per_task, balanced=True):
    from collections import deque
    from numpy.matlib import repmat

    latin_sq = generate_latin_square(n_tasks, balanced=balanced)
    n_repetition_per_task = len(latin_sq)
    if n_blocks_per_task % n_repetition_per_task != 0:
        raise ValueError("invalid number of trials - does not fit with "
                         "balanced Latin square design")
    else:
        n_repetitions = int(n_blocks_per_task/n_repetition_per_task)
    deque_latin_sq = deque(latin_sq)
    deque_latin_sq.rotate(np.random.randint(n_repetition_per_task))
    rotated_latin_sq = np.array(deque_latin_sq)
    repeated_latin_sq = repmat(rotated_latin_sq, n_repetitions, 1)
    return repeated_latin_sq


def generate_run_stim_order(stim_df,
                            task_types,
                            targ_amps,
                            n_trials_per_task_per_amp,
                            n_trials_per_block_per_amp,
                            n_blocks_per_task,
                            repeated_latin_sq):
    from random import shuffle
    def chunks(lst, n): return [lst[i:i + n] for i in range(0, len(lst), n)]

    # Draw the stim numbers and organize into task types and target amplitudes
    stim_num_dict1 = {}
    for task in task_types:
        stim_type, _ = task.split("-")
        for amp in targ_amps:
            curr_stim_nums = \
                stim_df[(stim_df["is_target"])
                        & (stim_df["stim_type"] == stim_type)
                        & (stim_df["amplitude"] == amp)]["stim_num"].values
            chosen_stim_nums = np.random.choice(curr_stim_nums,
                                                n_trials_per_task_per_amp,
                                                replace=False)
            list_stim_nums = chosen_stim_nums.tolist()
            chunked_stim_nums = chunks(
                list_stim_nums, n_trials_per_block_per_amp)
            stim_num_dict1[(task, amp)] = chunked_stim_nums

    # Organize stimulus numbers into task types and blocks
    stim_num_dict2 = {}
    for task in task_types:
        accumulator2 = []
        for block_num in range(n_blocks_per_task):
            accumulator1 = []
            for amp in targ_amps:
                accumulator1 += stim_num_dict1[(task, amp)][block_num]
            shuffle(accumulator1)  # randomize target amplitudes within a block
            accumulator2.append(accumulator1)
        stim_num_dict2[task] = accumulator2

    # Organize stimulus numbers into blocks
    blocked_stim_num_order = []
    for j, row in enumerate(repeated_latin_sq):
        for i in row:
            task = task_types[i]
            blocked_stim_num_order.append(stim_num_dict2[task][j])

    return blocked_stim_num_order


def generate_block_tuples(stim_df, block_stim_nums):
    # Pack trial information into a tuples
    block_order = []
    for stim_num in block_stim_nums:
        curr_stim_fname = "stim_" + str(stim_num).zfill(5) + ".wav"
        curr_stim_path = STIM_DIR/curr_stim_fname
        curr_stim_df = stim_df[stim_df["stim_num"] == stim_num]
        target_idx = np.where(curr_stim_df["is_target"])[0][0]
        target_sentence = curr_stim_df["pattern"].values[target_idx]
        curr_stim = SoundLoader(curr_stim_path)
        block_order.append((stim_num, curr_stim, target_idx, target_sentence))
    return block_order
