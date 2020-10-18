from fastprogress.fastprogress import progress_bar

from utils.stim_tools import *


################################################################################
# SYNTHESIS PARAMETERS
################################################################################
stim_types = ["SIM", "TIM"]
conditions = ["co-located", "plus_minus_90", 0.5] # alt rate
n_srcs = 2
n_stim = 10
spatial_resolution = 2 # average samples per degree over the whole trajectory
level = 80
r = 100 # cm
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
for stim_type in stim_types:
    for cond in conditions:
        if cond == "co-located" or cond == "plus_minus_90":
            print("\nSynthesizing {:s} {:s} stimuli...".format(stim_type, cond))
            alt_rates = [0 for _ in range(n_srcs)]
        else:
            print("\nSynthesizing {:s} {:.1f} Hz stimuli...".format(stim_type, cond))
            alt_rates = [cond for _ in range(n_srcs)]

        for i in progress_bar(range(n_stim)):
            # Make sound patterns
            if stim_type == "SIM":
                srcs, patterns, snds = make_sentence(n_srcs)
            elif stim_type == "TIM":
                srcs, patterns, snds = make_TP_sequence(n_srcs)
            else:
                raise ValueError("invalid stim_type; use 'SIM' or 'TIM'")
            patterns = [" ".join(patterns[i, :]).upper() for i in range(n_srcs)]
            snds = center_sounds(snds)
            snds = [snd.make_binaural() for snd in snds]
            is_target = [False for _ in range(n_srcs)]
            is_target[0] = True

            # Create trajectories
            if cond == "co-located":
                init_angles = np.zeros(n_srcs)
                trajs = np.array([hcc_to_rect(r, 0, init_angles[i])
                                  for i in range(n_srcs)]).reshape(n_srcs, -1, 3)
            elif cond == "plus_minus_90":
                init_angles = np.zeros(n_srcs)
                init_angles[0] = 90*np.random.choice([-1., 1.])
                for i in range(1, n_srcs):
                    init_angles[i] = (-1)**i*init_angles[0]
                trajs = np.array([hcc_to_rect(r, 0, init_angles[i])
                                  for i in range(n_srcs)]).reshape(n_srcs, -1, 3)
            else:
                init_angles = np.zeros(n_srcs)
                init_angles[0] = np.random.choice([-1., 1.])*90
                for i in range(1, n_srcs):
                    init_angles[i] = (-1)**i*init_angles[0]
                traj_dur = len(snds[0])/snds[0].fs
                trajs = np.array( \
                    [make_circular_sinuisoidal_trajectory(r, elev, init_angles[i],
                                                          traj_dur, alt_rates[i],
                                                          spatial_resolution)
                     for i in range(n_srcs)])

            # Synthesize moving sound
            moved_snds = [move_sound(trajs[i], snds[i]) for i in range(n_srcs)]
            combined = sum(moved_snds)
            stimulus = normalize_rms([combined])[0] + compute_attenuation(level)

            # Save stimulus and stimulus information
            stim_fname = "stim_" + str(stim_num).zfill(5) + ".wav"
            stimulus.save(STIM_DIR/stim_fname)
            stim_database = stim_database.append( \
                [{"stim_num": stim_num, "stim_type": stim_type, "n_srcs": n_srcs,
                  "src": srcs[i], "is_target": is_target[i], "pattern": patterns[i],
                  "alt_rate": alt_rates[i], "init_angle": init_angles[i]}
                 for i in range(n_srcs)],
                ignore_index=True)
            stim_database.to_csv(STIM_DIR/"stimulus_database.csv", index=False)
            stim_num += 1
################################################################################
# END SYNTHESIS
################################################################################
print("\n...Finished!")
