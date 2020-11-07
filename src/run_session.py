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
subject_ID = "AYC"
n_blocks_per_cond = 2
n_trials_per_block = 10

curr_expt = []
for _ in range(n_blocks_per_cond):
    curr_expt = n_blocks_per_cond*(CONTROL_IM + EXPT_EV_IM + EXPT_DV_IM)
stim_type = curr_expt[0].stim_type
run_stim_order = choose_stim_for_run(stim_database, curr_expt, n_trials_per_block)

# Check that the specified conditions are in the stimulus database
# validate_parameters(stim_database, task_type, n_srcs, conditions)

# Blocking parameters
# randomize_within_block = True
# n_blocks = 10                         # if randomized within block
# n_trials_per_block_per_condition = 2 # if randomized within block
# n_trials_per_block = None      # if NOT randomized within block
# n_blocks_per_condition = None   # if NOT randomized within block
# run_stim_order = set_stim_order(stim_database, task_type, n_srcs, conditions,
#                                 n_blocks,
#                                 n_trials_per_block_per_condition,
#                                 n_trials_per_block,
#                                 n_blocks_per_condition,
#                                 randomize_within_block)
# if randomize_within_block:
#     n_trials_per_block = n_trials_per_block_per_condition*len(conditions)

# Set save file path and create data structure
file_name = "RUN_" + str(run_num).zfill(3) + ".csv"
save_path = DATA_DIR/file_name
run_data = pd.DataFrame(columns=DATA_COLUMNS)
# answer_choices = VERBS + NUMBERS + ADJECTIVES + NOUNS
answer_choices = sorted(VERBS + NUMBERS + ADJECTIVES + NOUNS)

# Initialize GUI elements
win = \
    visual.Window(
        fullscr=True,
        winType="pyglet",
        monitor="testMonitor",
        units="deg"
    )
push_button = PushButton(win)
mouse = CustomMouse(win=win)
helper_text = SupportingText(win)
word_submission_queue = WordQueue(win, n_slots=5, gap=1, width=3, height=1, y_pos=7.5)
word_answer_queue     = WordQueue(win, n_slots=5, gap=1, width=3, height=1, y_pos=5)
word_grid_interface   = WordGridInterface(win, column_len=len(VERBS),
                                          words_in_grid=answer_choices,
                                          x_offset=-15.5, y_offset=3.5,
                                          word_box_width=3.75, word_box_height=1.5)

################################################################################
# RUN EXPT LOOP
################################################################################
expt_timer = core.Clock()

# Show task instructions
task_instruction_txt = make_task_instruction_str()
helper_text.set_text(task_instruction_txt)
helper_text.draw()
push_button.set_text("NEXT")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)

n_blocks = len(run_stim_order)
for block_num, block_stim_order in enumerate(run_stim_order):
    # Set ready screen
    block_ready_txt = "BLOCK {:d} of {:d}\n\nPress NEXT when ready.".format(
                      block_num + 1, n_blocks)
    helper_text.set_text(block_ready_txt)
    helper_text.draw()
    push_button.draw()
    push_button.set_text("NEXT")
    win.flip()
    wait_for_push_button(win, mouse, push_button)

    n_trials = len(block_stim_order)
    for trial_num, (stim, stim_num, target_pattern_items) \
    in enumerate(block_stim_order):
        # Display trial number
        trial_txt = "BLOCK {:d}/{:d};\tTRIAL {:d}/{:d}".format(
                     block_num + 1, n_blocks, trial_num + 1, n_trials_per_block)
        helper_text.set_pos((0, 5))
        helper_text.set_text(trial_txt)
        helper_text.draw()
        win.flip()

        # Make and play stimulus
        core.wait(0.25)
        stim.play(blocking=True)

        # Wait for subject response
        subj_response, correct = \
            do_recall_task(stim_type, win, mouse, helper_text, push_button,
                           word_submission_queue, word_answer_queue,
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
helper_text.set_text("Run complete!\n\nPlease see the experimenter.")
helper_text.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)
################################################################################
# END EXPT
################################################################################
exit_program(win)
