from utils.stim_tools import *


################################################################################
# EXAMPLE STIMULI GENERATOR SCRIPT (largely based on generate_stim.py)
################################################################################
def make_motion_examples(curr_n, traj_amp, level):
    spatial_resolution = 2 # average samples per degree over the whole trajectory
    r = 100
    elev = 0
    f = 2.
    src_spacing = 40

    talkers, sentences, snds = make_sentence(curr_n)
    snds = zeropad_sounds(snds)
    snds = normalize_rms(snds)
    snds = [snd.make_binaural() for snd in snds]
    t_dur = len(snds[0])/snds[0].fs

    # Designate target
    target_idx = np.random.randint(curr_n)
    is_target = np.zeros(curr_n, dtype=bool)
    is_target[target_idx] = True
    rates = np.zeros(curr_n)
    rates[target_idx] = f

    # Set canonical trajectory parameters
    A = traj_amp
    B = f
    C = np.random.choice([0, 0.5])
    D = np.array([src_spacing*i for i in range(curr_n)])
    D = D - D.mean()

    # Select target and make the trajectories
    trajs = [make_circular_sinuisoidal_trajectory(\
                 spatial_resolution, t_dur, r, elev,
                 A, B, C, D[i])
             if target
             else
             make_circular_sinuisoidal_trajectory(\
                 spatial_resolution, t_dur, r, elev,
                 0, 0, 0, D[i])
             for i, target in enumerate(is_target)]

    # Move each source
    moved_snds = [move_sound(trajs[i], snds[i]) for i in range(curr_n)]
    combined_moved_snds = normalize_rms([sum(moved_snds)])[0]
    stimulus = combined_moved_snds + compute_attenuation(level)
    return target_idx, stimulus


################################################################################
# SYNTHESIS PARAMETERS
################################################################################
level = 65.
stim_type = "BUG"
# task_type = "motion_detection"
task_type = "speech_ID"

if task_type == "motion_detection":
    ex_conds = [(1, 30, level), (1, 30, level), (3, 30, level),
                (3, 30, level), (3, 15, level), (3,  0, level)]
    ex_target_idxs, ex_stims = zip(*[make_motion_examples(*pair) for pair in ex_conds])
    for i in range(len(ex_stims)):
        ex_stims[i].save(EXMP_DIR/("detection_ex" + str(i + 1) + ".wav"))
    with open(EXMP_DIR/"detection_ex_target_idxs.txt", "w") as fin:
        for item in ex_target_idxs:
            fin.write("{:d}\n".format(item))

elif task_type == "speech_ID":
    ex_conds = [(3, 30, level), (3, 30, level), (3, 30, level),
                (3, 15, level), (3, 15, level), (3, 15, level)]
    ex_target_idxs, ex_stims = zip(*[make_motion_examples(*pair) for pair in ex_conds])
    for i in range(len(ex_stims)):
        ex_stims[i].save(EXMP_DIR/("speech_ID_ex" + str(i + 1) + ".wav"))
    with open(EXMP_DIR/"speech_ID_ex_target_idxs.txt", "w") as fin:
        for item in ex_target_idxs:
            fin.write("{:d}\n".format(item))

else:
    raise ValueError("invalid synthesis parameters")
