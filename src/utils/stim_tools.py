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


def make_sentence():
    n_talkers = 2

    # Randomly select target and masker talkers and words
    talkers = list(np.random.choice(ELIGIBLE_TALKERS, n_talkers, replace=False))
    all_sentences = \
        np.hstack( [np.random.choice(list(set(NAMES) - set(["Sue"])),
                                     (n_talkers, 1), replace=False),
                    np.random.choice(VERBS, (n_talkers, 1), replace=False),
                    np.random.choice(NUMBERS, (n_talkers, 1), replace=False),
                    np.random.choice(ADJECTIVES, (n_talkers, 1), replace=False),
                    np.random.choice(NOUNS, (n_talkers, 1), replace=False),
                    np.random.choice(CONJUNCTIONS, (n_talkers, 1), replace=False),
                    np.random.choice(list(set(NAMES) - set(["Sue"])),
                                     (n_talkers, 1), replace=False),
                    np.random.choice(VERBS, (n_talkers, 1), replace=False),
                    np.random.choice(NUMBERS, (n_talkers, 1), replace=False),
                    np.random.choice(ADJECTIVES, (n_talkers, 1), replace=False),
                    np.random.choice(NOUNS, (n_talkers, 1), replace=False)] )
    all_sentences[0, 0] = "Sue"

    # Make target sentence
    target_talker = talkers[0]
    target_sentence_items = list(all_sentences[0, :])
    target_sentence = concat_sounds([ELIGIBLE_BUG_DICT["_".join([word, target_talker])]
                                     for word in target_sentence_items])
    # Make masker sentence
    masker_talker = talkers[1]
    masker_sentence_items = list(all_sentences[1, :])
    masker_sentence = concat_sounds([ELIGIBLE_BUG_DICT["_".join([word, masker_talker])]
                                     for word in masker_sentence_items])

    # Normalize RMS
    target_sentence, masker_sentence = \
        normalize_rms([target_sentence, masker_sentence])

    return talkers, \
           target_sentence, masker_sentence, \
           target_sentence_items, masker_sentence_items


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


def set_stimuli_for_block(n_trials_per_block_per_rate, conditions, curr_run_data):
    stim_database = pd.read_csv(STIM_DIR/"stimulus_database.csv")
    stimulus_list = []
    for cond in conditions:
        if cond == "co-located":
            curr_cond_all_stim = stim_database[
                (stim_database["target_alt_rate"] == 0) &
                (stim_database["target_init_position"] == 0)].index.values
            curr_cond_used_stim = stim_database.iloc[
                    curr_run_data["stimulus_ID"].values][
                (stim_database["target_alt_rate"] == 0) &
                (stim_database["target_init_position"] == 0)].index.values
        elif cond == "opposite":
            curr_cond_all_stim = stim_database[
                (stim_database["target_alt_rate"] == 0) &
                (stim_database["target_init_position"] != 0)].index.values
            curr_cond_used_stim = stim_database.iloc[
                    curr_run_data["stimulus_ID"].values][
                (stim_database["target_alt_rate"] == 0) &
                (stim_database["target_init_position"] != 0)].index.values
        else:
            curr_cond_all_stim = stim_database[
                stim_database["target_alt_rate"] == cond].index.values
            curr_cond_used_stim = stim_database.iloc[
                    curr_run_data["stimulus_ID"].values][
                stim_database["target_alt_rate"] == cond].index.values
        available_stim = set(curr_cond_all_stim) - set(curr_cond_used_stim)
        chosen_stim = np.random.choice(list(available_stim),
                                       n_trials_per_block_per_rate,
                                       replace=False)

        # Add to stimulus list
        for stim_ID in chosen_stim:
            stim_path = STIM_DIR/("stim_" + str(stim_ID).zfill(5) + ".wav")
            stimulus = SoundLoader(stim_path)
            target_sentence = stim_database.target_sentence[stim_ID]
            target_sentence_items = target_sentence.split(" ")
            stimulus_list.append((stimulus, stim_ID, target_sentence_items))
    np.random.shuffle(stimulus_list)
    return stimulus_list
