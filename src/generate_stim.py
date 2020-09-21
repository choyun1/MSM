from fastprogress.fastprogress import progress_bar

from utils.stim_tools import *


################################################################################
# SYNTHESIS PARAMETERS
################################################################################
r = 100 # cm
elev = 0
stim_type = "SIN"
ramp_dur = 20e-3 # Ramp duration for noise
level = 80
spatial_resolution = 2 # average samples per degree over the whole trajectory
target_alt_rates = [0]
# target_alt_rates = [0.1, 0.5, 1, 2, 4, 5, 6, 8, 10, 15]
control_condition = "co-located"
# control_condition = "opposite"
n_stim = 500

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
        talkers, \
        target, masker, \
        target_sentence_items, masker_sentence_items = make_sentence()
        if stim_type == "SIN": # noise masker condition
            talkers[1] = ""
            masker = GaussianNoise(len(target)/target.fs, target.fs)
            masker = ramp_edges(masker, ramp_dur)
            masker_sentence_items = ""
        target, masker = center_sounds([target, masker])
        target = target.make_binaural()
        masker = masker.make_binaural()

        # Create trajectories for target and masker
        if rate == 0: # control conditions
            if control_condition == "co-located":
                target_angle = 0
                masker_angle = 0
                target_traj = np.array([[0., 1., 0.]])
                masker_traj = np.array([[0., 1., 0.]])
            elif control_condition == "opposite":
                target_loc = np.random.choice([-1., 1.])
                masker_loc = -target_loc
                target_angle = 90*target_loc
                masker_angle = 90*masker_loc
                target_traj = np.array([[target_loc, 0., 0.]])
                masker_traj = np.array([[masker_loc, 0., 0.]])
            else:
                raise ValueError("invalid control condition!")
        else:
            target_angle = np.random.choice([-1., 1.])*90
            masker_angle = -target_angle
            traj_dur = len(target)/target.fs
            target_traj = \
                make_circular_sinuisoidal_trajectory(r, elev, target_angle,
                                                     traj_dur, rate,
                                                     spatial_resolution)
            masker_traj = \
                make_circular_sinuisoidal_trajectory(r, elev, masker_angle,
                                                     traj_dur, rate,
                                                     spatial_resolution)

        # Synthesize moving sound
        target = move_sound(target_traj, target)
        masker = move_sound(masker_traj, masker)
        combined = target + masker
        stimulus = normalize_rms([combined])[0] + compute_attenuation(level)

        # Save stimulus and stimulus information
        stim_fname = "stim_" + str(stim_num).zfill(5) + ".wav"
        stimulus.save(STIM_DIR/stim_fname)
        stim_database = stim_database.append( \
            {"stim_type": stim_type,
             "target_talker": talkers[0],
             "target_sentence": " ".join(target_sentence_items),
             "target_alt_rate": rate,
             "target_init_position": target_angle,
             "masker_talker": talkers[1],
             "masker_sentence": " ".join(masker_sentence_items),
             "masker_alt_rate": rate,
             "masker_init_position": masker_angle},
             ignore_index=True)
        stim_database.to_csv(STIM_DIR/"stimulus_database.csv", index=False)
        stim_num += 1
################################################################################
# END SYNTHESIS
################################################################################
print("\n...Finished!")
