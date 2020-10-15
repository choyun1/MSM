from fastprogress.fastprogress import progress_bar

from utils.stim_tools import *


################################################################################
# SYNTHESIS PARAMETERS
################################################################################
n_stim = 100
stim_types = ["SIM"]
n_srcs = 3
level = 80
r = 100 # cm
elev = 0
spatial_resolution = 2 # average samples per degree over the whole trajectory
# SNR = 0
# ramp_dur = 20e-3 # Ramp duration for noise
conditions = ["co-located", "opposite", 0.5, 2, 4, 8] # alt rate

# Load stimulus database
STIM_DIR = STIM_DIR/"pilot_v3"
try:
    stim_database = pd.read_csv(STIM_DIR/"stimulus_database.csv")
    stim_num = len(stim_database)
except FileNotFoundError:
    stim_database = pd.DataFrame(columns=STIM_COLUMNS)
    stim_num = 0

################################################################################
# SYNTHESIS ROUTINE
################################################################################
for stim_type in stim_types:
    for cond in conditions:
        if cond == "co-located":
            target_alt_rate = 0
            masker1_alt_rate = 0
            masker2_alt_rate = 0
            print("\nSynthesizing {:s} {:s} stimuli...".format(stim_type, cond))
        elif cond == "opposite":
            target_alt_rate = 0
            masker1_alt_rate = 0
            masker2_alt_rate = 0
            print("\nSynthesizing {:s} {:s} stimuli...".format(stim_type, cond))
        else:
            target_alt_rate = cond
            masker1_alt_rate = cond
            masker2_alt_rate = cond
            print("\nSynthesizing {:s} {:.1f} Hz stimuli...".format(stim_type, target_alt_rate))

        for i in progress_bar(range(n_stim)):
            # Make sentences, center, and make binaural
            if stim_type == "SIM":
                srcs, patterns, seqs = make_sentence(n_srcs)
            elif stim_type == "TIM":
                srcs, patterns, seqs = make_TP_sequence(n_srcs)
            else:
                raise ValueError("invalid stim_type; use 'SIM' or 'TIM'")
            # if stim_type == "SIN": # noise masker condition
            #     talkers[1] = ""
            #     masker = GaussianNoise(len(target)/target.fs, target.fs)
            #     masker = ramp_edges(masker, ramp_dur)
            #     masker_sentence_items = ""
            target, masker1, masker2 = center_sounds(seqs)
            target  = target.make_binaural()
            masker1 = masker1.make_binaural()
            masker2 = masker2.make_binaural()
            target_pattern  = " ".join(patterns[0, :]).upper()
            masker1_pattern = " ".join(patterns[1, :]).upper()
            masker2_pattern = " ".join(patterns[2, :]).upper()

            # Create trajectories for target and masker
            if cond == "co-located":
                target_angle = 0
                masker1_angle = 0
                masker2_angle = 0
                target_traj = np.array([[0., 1., 0.]])
                masker1_traj = np.array([[0., 1., 0.]])
                masker2_traj = np.array([[0., 1., 0.]])
            elif cond == "opposite":
                target_loc = np.random.choice([-1., 1.])
                masker1_loc = target_loc
                masker2_loc = -target_loc
                target_angle = 90*target_loc
                masker1_angle = 90*masker1_loc
                masker2_angle = 90*masker2_loc
                target_traj = np.array([[target_loc, 0., 0.]])
                masker1_traj = np.array([[masker1_loc, 0., 0.]])
                masker2_traj = np.array([[masker2_loc, 0., 0.]])
            else:
                target_angle  = np.random.choice([-1., 1.])*90
                masker1_angle = target_angle
                masker2_angle = -target_angle
                traj_dur = len(target)/target.fs
                target_traj = \
                    make_circular_sinuisoidal_trajectory(r, elev, target_angle,
                                                         traj_dur, target_alt_rate,
                                                         spatial_resolution)
                masker1_traj = \
                    make_circular_sinuisoidal_trajectory(r, elev, masker1_angle,
                                                         traj_dur, masker1_alt_rate,
                                                         spatial_resolution)
                masker2_traj = \
                    make_circular_sinuisoidal_trajectory(r, elev, masker2_angle,
                                                         traj_dur, masker2_alt_rate,
                                                         spatial_resolution)
            # Synthesize moving sound
            target  = move_sound(target_traj,  target)
            masker1 = move_sound(masker1_traj, masker1)
            masker2 = move_sound(masker2_traj, masker2)
            combined = target + masker1 + masker2
            stimulus = normalize_rms([combined])[0] + compute_attenuation(level)

            # Save stimulus and stimulus information
            stim_fname = "stim_" + str(stim_num).zfill(5) + ".wav"
            stimulus.save(STIM_DIR/stim_fname)
            stim_database = stim_database.append( \
                {"stim_type": stim_type,
                 "target": srcs[0],
                 "target_pattern": target_pattern,
                 "target_alt_rate": target_alt_rate,
                 "target_init_position": target_angle,
                 "masker1": srcs[1],
                 "masker1_pattern": masker1_pattern,
                 "masker1_alt_rate": masker1_alt_rate,
                 "masker1_init_position": masker1_angle,
                 "masker2": srcs[2],
                 "masker2_pattern": masker2_pattern,
                 "masker2_alt_rate": masker2_alt_rate,
                 "masker2_init_position": masker2_angle},
                 ignore_index=True)
            stim_database.to_csv(STIM_DIR/"stimulus_database.csv", index=False)
            stim_num += 1
################################################################################
# END SYNTHESIS
################################################################################
print("\n...Finished!")
