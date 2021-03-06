from fastprogress.fastprogress import progress_bar

from utils.stim_tools import *


################################################################################
# SYNTHESIS PARAMETERS
################################################################################
stim_type = "BUG"
# stim_type = "SMN"
n_stim = 1
n_srcs = [3]
src_spacing = 40.
target_freq = 2.
target_traj_amp = [0., 5., 10., 15., 20., 25., 30., 35.]

level = 65.
spatial_resolution = 2.  # average samples per degree over the whole trajectory
r = 100.
elev = 0.

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
for curr_n in n_srcs:
    for amp in target_traj_amp:
        print("\nSynthesizing curr_n = {:d}, targ_amp = {:2.2f} deg "
              "stimuli...".format(curr_n, amp))
        for _ in progress_bar(range(n_stim)):
            if stim_type == "BUG":
                # Make sources and patterns
                talkers, sentences, snds = make_sentence(curr_n)
                snds = zeropad_sounds(snds)
                t_dur = len(snds[0])/snds[0].fs
                snds = normalize_rms(snds)
                snds = [snd.make_binaural() for snd in snds]
            elif stim_type == "SMN":
                talkers, sentences, snds = make_sentence(curr_n)
                snds = zeropad_sounds(snds)
                t_dur = len(snds[0])/snds[0].fs
                gns = [ALL_WORDS_SPECT.to_Noise(
                    t_dur, snds[0].fs) for snd in snds]
                smns = [gns[i]*snds[i].extract_envelope()
                        for i in range(len(gns))]
                smns = normalize_rms(smns)
                snds = [smn.make_binaural() for smn in smns]
            else:
                raise ValueError("invalid stim_type")

            # Designate target
            target_idx = np.random.randint(curr_n)
            is_target = np.zeros(curr_n, dtype=bool)
            is_target[target_idx] = True
            amplitudes = np.zeros(curr_n)
            amplitudes[target_idx] = amp
            rates = np.zeros(curr_n)
            rates[target_idx] = target_freq

            # Set trajectory parameters
            A = amp
            if A == 0:  # static condition
                B = 0
            else:
                B = target_freq
            C = np.random.choice([0, 0.5])  # initially moving left or right
            D = np.array([src_spacing*i for i in range(curr_n)])
            D = D - D.mean()

            # Make trajectories for target and maskers
            trajs = [make_circular_sinuisoidal_trajectory(
                spatial_resolution, t_dur, r, elev,
                A, B, C, D[i])
                if target_bool
                else
                make_circular_sinuisoidal_trajectory(
                spatial_resolution, t_dur, r, elev,
                0, 0, 0, D[i])
                for i, target_bool in enumerate(is_target)]

            # Move each source
            moved_snds = [move_sound(trajs[i], snds[i]) for i in range(curr_n)]
            combined_moved_snds = normalize_rms([sum(moved_snds)])[0]
            stimulus = combined_moved_snds + compute_attenuation(level)

            # Save stimulus and stimulus information
            stim_fname = "stim_" + str(stim_num).zfill(5) + ".wav"
            stimulus.save(STIM_DIR/stim_fname)
            stim_database = stim_database.append(
                [{"stim_num": stim_num,
                  "stim_type": stim_type,
                  "nominal_level": level,
                  "src": talkers[i],
                  "is_target": is_target[i],
                  "pattern": sentences[i],
                  "amplitude": amplitudes[i],
                  "rate": rates[i],
                  "init_angle": D[i]}
                 for i in range(curr_n)],
                ignore_index=True)
            stim_database.to_csv(STIM_DIR/"stimulus_database.csv", index=False)
            stim_num += 1

            # # If you want answers for example
            # print()
            # print(target_idx)
            # print(sentences[target_idx])
            # print()

################################################################################
# END SYNTHESIS
################################################################################
print("\n...Finished!")
