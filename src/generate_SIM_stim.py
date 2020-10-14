from fastprogress.fastprogress import progress_bar

from utils.stim_tools import *


################################################################################
# SYNTHESIS PARAMETERS
################################################################################
r = 100 # cm
elev = 0
stim_type = "SOS"
SNR = 0
ramp_dur = 20e-3 # Ramp duration for noise
level = 80
n_talkers = 3
spatial_resolution = 2 # average samples per degree over the whole trajectory
# target_alt_rates = [0.1, 0.5, 1, 2, 4, 5, 6, 8, 10, 15]
# target_alt_rates = [0.5, 4]
target_alt_rates = [2]
# control_condition = "co-located"
control_condition = "opposite"
n_stim = 100

# Load stimulus database
try:
    stim_database = pd.read_csv(STIM_DIR/"stimulus_database.csv")
    stim_num = len(stim_database)
except FileNotFoundError:
    stim_database = pd.DataFrame(columns=STIM_COLUMNS)
    stim_num = 0

################################################################################
# SYNTHESIS ROUTINE
################################################################################
for rate in target_alt_rates:
    print("\nSynthesizing {:.1f} Hz stimuli...".format(rate))
    for i in progress_bar(range(n_stim)):
        # Make sentences, center, and make binaural
        talkers, sentence_items, sentences = make_sentence(n_talkers)
        # if stim_type == "SIN": # noise masker condition
        #     talkers[1] = ""
        #     masker = GaussianNoise(len(target)/target.fs, target.fs)
        #     masker = ramp_edges(masker, ramp_dur)
        #     masker_sentence_items = ""
        target, masker1, masker2 = center_sounds(sentences)
        target  = target.make_binaural()
        masker1 = masker1.make_binaural()
        masker2 = masker2.make_binaural()
        target_sentence = " ".join(sentence_items[0, :])
        masker1_sentence = " ".join(sentence_items[1, :])
        masker2_sentence = " ".join(sentence_items[2, :])

        # Create trajectories for target and masker
        if rate == 0: # control conditions
            if control_condition == "co-located":
                target_angle = 0
                masker1_angle = 0
                target_traj = np.array([[0., 1., 0.]])
                masker1_traj = np.array([[0., 1., 0.]])
            elif control_condition == "opposite":
                target_loc = np.random.choice([-1., 1.])
                masker1_loc = -target_loc
                target_angle = 90*target_loc
                masker1_angle = 90*masker1_loc
                target_traj = np.array([[target_loc, 0., 0.]])
                masker1_traj = np.array([[masker1_loc, 0., 0.]])
            else:
                raise ValueError("invalid control condition!")
            masker2_angle = 0
            masker2_sentence = ""
        else:
            target_angle  = np.random.choice([-1., 1.])*90
            masker1_angle = target_angle
            masker2_angle = -target_angle
            traj_dur = len(target)/target.fs
            target_traj = \
                make_circular_sinuisoidal_trajectory(r, elev, target_angle,
                                                     traj_dur, rate,
                                                     spatial_resolution)
            masker1_traj = \
                make_circular_sinuisoidal_trajectory(r, elev, masker1_angle,
                                                     traj_dur, rate,
                                                     spatial_resolution)
            masker2_traj = \
                make_circular_sinuisoidal_trajectory(r, elev, masker2_angle,
                                                     traj_dur, rate,
                                                     spatial_resolution)
        # Synthesize moving sound
        target  = move_sound(target_traj, target)
        masker1 = move_sound(masker1_traj, masker1)
        combined = target + masker1
        if rate != 0:
            masker2 = move_sound(masker2_traj, masker2)
            combined = target + masker1 + masker2
        # if stim_type == "SIN": # SNR = -20 if noise
        #     target += SNR
        stimulus = normalize_rms([combined])[0] + compute_attenuation(level)

        # Save stimulus and stimulus information
        stim_fname = "stim_" + str(stim_num).zfill(5) + ".wav"
        stimulus.save(STIM_DIR/stim_fname)
        stim_database = stim_database.append( \
            {"stim_type": stim_type,
             "target_talker": talkers[0],
             "target_sentence": target_sentence,
             "target_alt_rate": rate,
             "target_init_position": target_angle,
             "masker1_talker": talkers[1],
             "masker1_sentence": masker1_sentence,
             "masker1_alt_rate": rate,
             "masker1_init_position": masker1_angle,
             "masker2_talker": talkers[2],
             "masker2_sentence": masker2_sentence,
             "masker2_alt_rate": rate,
             "masker2_init_position": masker2_angle},
             ignore_index=True)
        stim_database.to_csv(STIM_DIR/"stimulus_database.csv", index=False)
        stim_num += 1
################################################################################
# END SYNTHESIS
################################################################################
print("\n...Finished!")
