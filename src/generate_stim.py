from fastprogress.fastprogress import master_bar, progress_bar

from utils.stim_tools import *


################################################################################
# SYNTHESIS PARAMETERS
################################################################################
r = 100 # cm
elev = 0
new_fs = 16000
spatial_resolution = 2 # average points per degree over the whole trajectory
alternation_rates = [0.1, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
n_stim = 100
stim_type = "SOS"

# Load stimulus database
try:
    STIM_DATABASE = pd.read_csv(STIM_DIR/"stimulus_database.csv")
    stim_num = len(STIM_DATABASE)
except FileNotFoundError:
    STIM_DATABASE = pd.DataFrame(columns=STIM_COLUMNS)
    stim_num = 0


################################################################################
# SYNTHESIS ROUTINE
################################################################################
dummy_snd = Silence(0.01, new_fs)
for rate in alternation_rates:
    print("\nSynthesizing {:.1f} Hz stimuli...".format(rate))
    for i in progress_bar(range(n_stim)):
        # Make sentences and downsample, center, and make binaural
        talkers, \
        target_sentence, masker_sentence, \
        target_sentence_items, masker_sentence_items = make_sentence()
        _, target_sentence, masker_sentence = \
            equalize_fs([dummy_snd, target_sentence, masker_sentence])
        target_sentence, masker_sentence = \
            center_sounds([target_sentence, masker_sentence])
        target_sentence = target_sentence.make_binaural()
        masker_sentence = masker_sentence.make_binaural()

        # Create trajectories for target and masker
        traj_dur = len(target_sentence)/target_sentence.fs
        target_angle = np.random.choice([-1, 1])*90
        masker_angle = -target_angle
        target_traj = \
            make_circular_sinuisoidal_trajectory(r, elev, target_angle, traj_dur,
                                                 rate, spatial_resolution)
        masker_traj = \
            make_circular_sinuisoidal_trajectory(r, elev, masker_angle, traj_dur,
                                                 rate, spatial_resolution)

        # Synthesize moving sound
        target_sentence = move_sound(target_traj, target_sentence)
        masker_sentence = move_sound(masker_traj, masker_sentence)
        stimulus = (target_sentence + masker_sentence) - 30

        # Save stimulus and stimulus information
        stim_fname = "stim_" + str(stim_num).zfill(6) + ".wav"
        stimulus.save(STIM_DIR/stim_fname)
        STIM_DATABASE = STIM_DATABASE.append( \
            {"stim_type": stim_type,
             "alternation_rate": rate,
             "target_talker": talkers[0],
             "target_sentence": " ".join(target_sentence_items),
             "init_target_position": target_angle,
             "masker_talker": talkers[1],
             "masker_sentence": " ".join(masker_sentence_items),
             "init_masker_position": masker_angle},
             ignore_index=True)
        STIM_DATABASE.to_csv(STIM_DIR/"stimulus_database.csv", index=False)
        stim_num += 1

print("\n...Finished!")
