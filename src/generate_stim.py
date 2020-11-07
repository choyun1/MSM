from fastprogress.fastprogress import progress_bar

from utils.stim_tools import *


################################################################################
# SYNTHESIS PARAMETERS
################################################################################
n_stim = 100

n_srcs = 2
TMR_EM = -20
TMR_IM = 0
noise_ramp = 50e-3
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
for cond in ALL_CONDITIONS:
    print("\nSynthesizing {:s}, {:.1f} Hz, {:.1f} Hz stimuli...".format(\
          cond.stim_type, cond.target_alt_rate, cond.masker_alt_rate))
    for _ in progress_bar(range(n_stim)):
        # Make sources and patterns
        srcs, patterns, snds = make_sentence(n_srcs, "random")
        if cond.stim_type == "SEM":
            TMR = TMR_EM
            srcs[1] = "SSN"
            patterns[1] = ""
            snds[1] = ramp_edges(\
                ALL_WORDS_SPECT.to_Noise(len(snds[0])/snds[0].fs, snds[0].fs),
                                 noise_ramp)
        elif cond.stim_type == "SIM":
            TMR = TMR_IM
        else:
            raise ValueError("invalid stim_type; choose 'SEM' or 'SIM'")
        snds = zeropad_sounds(snds)
        snds = normalize_rms(snds)
        snds = [snd.make_binaural() for snd in snds]

        # Set angles, velocities, directions
        is_target = n_srcs*[False]
        is_target[0] = True
        rates = [cond.target_alt_rate, cond.masker_alt_rate]
        if rates[0] == 0: # Static 90 or 127
            target_init_angle = cond.target_init_angle*np.random.choice([-1, 1])
            masker_init_angle = -target_init_angle
            target_init_dir_R = True
            masker_init_dir_R = False
        elif rates[0] == rates[1]:
            target_init_angle = 180*(np.random.rand() - 0.5)
            masker_init_angle = -target_init_angle
            target_init_dir_R = np.random.choice([True, False])
            masker_init_dir_R = not target_init_dir_R
        else:
            target_init_angle = 180*(np.random.rand() - 0.5)
            masker_init_angle = 180*(np.random.rand() - 0.5)
            target_init_dir_R = np.random.choice([True, False])
            masker_init_dir_R = np.random.choice([True, False])
        init_angles = [target_init_angle, masker_init_angle]
        init_dir_Rs = [target_init_dir_R, masker_init_dir_R]

        # Make the trajectories
        traj_dur = len(snds[0])/snds[0].fs
        trajs = [make_circular_sinuisoidal_trajectory(\
                     spatial_resolution, traj_dur, r, elev,
                     rates[i], init_angles[i], init_dir_Rs[i])
                 for i in range(n_srcs)]

        # Move each source
        moved_snds = [move_sound(trajs[i], snds[i]) for i in range(n_srcs)]
        moved_snds[0] += TMR
        combined_moved_snds = normalize_rms([sum(moved_snds)])[0]
        stimulus = combined_moved_snds + compute_attenuation(level)

        # Save stimulus and stimulus information
        stim_fname = "stim_" + str(stim_num).zfill(5) + ".wav"
        stimulus.save(STIM_DIR/stim_fname)
        stim_database = stim_database.append(\
            [{"stim_num": stim_num,
              "stim_type": cond.stim_type,
              "TMR": TMR,
              "src": srcs[i],
              "is_target": is_target[i],
              "pattern": patterns[i],
              "alt_rate": rates[i],
              "init_angle": init_angles[i],
              "init_dir_R": init_dir_Rs[i]}
             for i in range(n_srcs)],
            ignore_index=True)
        stim_database.to_csv(STIM_DIR/"stimulus_database.csv", index=False)
        stim_num += 1
################################################################################
# END SYNTHESIS
################################################################################
print("\n...Finished!")
