from fastprogress.fastprogress import progress_bar

from utils.stim_tools import *


################################################################################
# SYNTHESIS PARAMETERS
################################################################################
n_stim = 100
# stim_type = "SEM"
# TMR = -25
stim_type = "SIM"
TMR = 0
alt_rates = [0.5, 1, 2, 5]
spatial_resolution = 2 # average samples per degree over the whole trajectory
level = 80
r = 100
elev = 0

# Load stimulus database
try:
    stim_database = pd.read_csv(STIM_DIR/"stimulus_database.csv")
    stim_num = stim_database["stim_num"].iloc[-1] + 1
except FileNotFoundError:
    stim_database = pd.DataFrame(columns=STIM_COLUMNS)
    stim_num = 0

################################################################################
# SYNTHESIS ROUTINE
################################################################################
for rate in alt_rates:
    print("\nSynthesizing {:s} {:.1f} Hz stimuli...".format(stim_type, rate))
    for _ in progress_bar(range(n_stim)):
        rates = [rate, 0]

        if stim_type == "SEM":
            srcs, patterns, snds = make_sentence(2)
            patterns = [" ".join(patterns[i, :]).upper() for i in range(len(snds))]
            srcs[1] = "GN"
            patterns[1] = ""
            snds[1] = ramp_edges(GaussianNoise(len(snds[0])/snds[0].fs, snds[0].fs), 25e-3)
        elif stim_type == "SIM":
            srcs, patterns, snds = make_sentence(2)
            patterns = [" ".join(patterns[i, :]).upper() for i in range(len(snds))]
        else:
            raise ValueError("invalid stim_type; choose 'SEM' or 'SIM'")
        is_target = [True, False]
        snds = zeropad_sounds(snds)
        snds = normalize_rms(snds)
        snds = [snd.make_binaural() for snd in snds]

        # target_init_angle = 180*(np.random.rand(1)[0] - 0.5)
        # masker_init_angle = 180*(np.random.rand(1)[0] - 0.5)
        target_init_angle = 90*np.random.choice([-1, 1])
        masker_init_angle = 0
        init_angles = [target_init_angle, masker_init_angle]

        target_init_dir_R = np.random.choice([True, False])
        # masker_init_dir_R = np.random.choice([True, False])
        masker_init_dir_R = not target_init_dir_R
        init_dir_Rs = [target_init_dir_R, masker_init_dir_R]

        traj_dur = len(snds[0])/snds[0].fs
        target_traj = make_circular_sinuisoidal_trajectory(r, elev, target_init_angle, target_init_dir_R, traj_dur, rates[0], spatial_resolution)
        masker_traj = make_circular_sinuisoidal_trajectory(r, elev, masker_init_angle, masker_init_dir_R, traj_dur, rates[1], spatial_resolution)
        trajs = [target_traj, masker_traj]

        moved_snds = [move_sound(trajs[i], snds[i]) for i in range(len(snds))]
        moved_snds[0] += TMR
        combined_moved_snds = sum(moved_snds)
        stimulus = normalize_rms([combined_moved_snds])[0] + compute_attenuation(level)

        # Save stimulus and stimulus information
        stim_fname = "stim_" + str(stim_num).zfill(5) + ".wav"
        stimulus.save(STIM_DIR/stim_fname)
        stim_database = stim_database.append( \
            [{"stim_num": stim_num, "stim_type": stim_type, "TMR": TMR,
              "src": srcs[i], "is_target": is_target[i], "pattern": patterns[i],
              "alt_rate": rates[i], "init_angle": init_angles[i], "init_dir_R": init_dir_Rs[i]}
             for i in range(len(snds))],
            ignore_index=True)
        stim_database.to_csv(STIM_DIR/"stimulus_database.csv", index=False)
        stim_num += 1
################################################################################
# END SYNTHESIS
################################################################################
print("\n...Finished!")
