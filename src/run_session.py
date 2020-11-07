from copy import deepcopy
from random import shuffle

# Project imports
from utils.init_constants import *
from utils.stim_tools import *
from utils.GUI_components import *
from utils.GUI_routines import *


################################################################################
# EXPT PARAMETERS
################################################################################
# Session parameters
run_num = len([x for x in DATA_DIR.glob("*.csv")])
stim_database = pd.read_csv(STIM_DIR/"stimulus_database.csv")
subject_ID = "AYC_TRAIN"
n_blocks_per_cond = 1
n_trials_per_block = 5

curr_expt = []
for _ in range(n_blocks_per_cond):
    # Training
    curr_copy = deepcopy(TRAIN_COND)
    curr_expt += curr_copy

    # # Alternate EM and IM
    # curr_EM_copy = deepcopy(CONTROL_EM + EXPT_EV_EM + EXPT_DV_EM)
    # curr_IM_copy = deepcopy(CONTROL_IM + EXPT_EV_IM + EXPT_DV_IM)
    # shuffle(curr_EM_copy)
    # shuffle(curr_IM_copy)
    # for i in range(len(curr_EM_copy)):
    #     curr_expt.append(curr_EM_copy[i])
    #     curr_expt.append(curr_IM_copy[i])
stim_type = expt_type[0].stim_type
run_stim_order = choose_stim_for_run(stim_database, curr_expt, n_trials_per_block)

# Set save file path and create data structure
file_name = "RUN_" + str(run_num).zfill(3) + ".csv"
save_path = DATA_DIR/file_name
run_data = pd.DataFrame(columns=DATA_COLUMNS)
# answer_choices = VERBS + NUMBERS + ADJECTIVES + NOUNS
answer_choices = sorted(VERBS + NUMBERS + ADJECTIVES + NOUNS)

# Initialize GUI elements
win = visual.Window(fullscr=True, winType="pyglet", monitor="testMonitor", units="deg")
mouse = CustomMouse(win=win)
word_grid_interface   = WordGridInterface(win, column_len=len(VERBS),
                                          words_in_grid=answer_choices,
                                          x_offset=-12, y_offset=3,
                                          word_box_width=4, word_box_height=1.5)
answer_queue     = WordQueue(win, n_slots=5, gap=1, width=3, height=1, y_pos=5)
submission_queue = WordQueue(win, n_slots=5, gap=1, width=3, height=1, y_pos=7.5)
helper_text = SupportText(win)
push_button = PushButton(win)

################################################################################
# RUN EXPT LOOP
################################################################################
expt_timer = core.Clock()

# Show task instructions
task_instruction_str = make_task_instruction()
helper_text.set(text=task_instruction_str, pos=((0, 0)), size=(12, 8))
helper_text.draw()
push_button.set_text("NEXT")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)

n_blocks = len(run_stim_order)
for block_num, block_stim_order in enumerate(run_stim_order):
    # Set ready screen
    curr_block_cond = curr_expt[block_num]
    stim_type = curr_block_cond.stim_type

    block_num_str = "BLOCK {:d} of {:d}\n\n".format(block_num + 1, n_blocks)
    stim_info_str = make_stim_info_str(curr_block_cond)
    press_next_str = "Press 'NEXT' when ready."
    helper_text.set(text=block_num_str + stim_info_str + press_next_str,
                    pos=(0, 2), size=(10, 6))
    helper_text.draw()
    push_button.set_text("NEXT")
    push_button.draw()
    win.flip()
    wait_for_push_button(win, mouse, push_button)

    n_trials = len(block_stim_order)
    for trial_num, (stim, stim_num, target_pattern_items) \
                    in enumerate(block_stim_order):
        # Display trial number
        trial_txt = "BLOCK {:d}/{:d};\tTRIAL {:d}/{:d}".format(
                     block_num + 1, n_blocks, trial_num + 1, n_trials)
        helper_text.set_text(text=trial_txt, pos=(0, 5), size=(6, 3))
        helper_text.draw()
        win.flip()

        # Make and play stimulus
        core.wait(0.25)
        stim.play(blocking=True)

        # Wait for subject response
        subj_response, correct = \
            do_recall_task(stim_type, win, mouse, helper_text, push_button,
                           submission_queue, answer_queue,
                           word_grid_interface, target_pattern_items)
        elapsed_time = expt_timer.getTime()

        # Save data
        run_data = run_data.append(
            {"run_num": run_num,
             "subject_ID": subject_ID,
             "stim_type": stim_type,
             "block_num": block_num + 1,
             "trial_num": trial_num + 1,
             "stim_num": stim_num,
             "subj_response": " ".join(subj_response),
             "correct": correct,
             "elapsed_time": elapsed_time},
             ignore_index=True)
        run_data.to_csv(save_path, index=False)

# End screen
helper_text.set(text="Run complete!\n\nPlease see the experimenter.",
                pos=(0, 5), size=(10, 4))
helper_text.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)
################################################################################
# END EXPT
################################################################################
exit_program(win)
