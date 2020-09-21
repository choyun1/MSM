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
subject_ID = "AYC"
task_type = "SOS"
n_blocks = 1
n_trials_per_block_per_rate = 1
# conditions = [0, 0.1, 0.5, 1, 2, 4, 5, 6, 8, 10, 15]
conditions = ["co-located", "opposite", 0.1, 0.5, 1, 2, 4, 5, 6, 8, 10, 15]

# Set save file path and create data structure
file_name = "RUN_" + str(run_num).zfill(3) + ".csv"
save_path = DATA_DIR/file_name
run_data = pd.DataFrame(columns=DATA_COLUMNS)
answer_choices = VERBS + NUMBERS + ADJECTIVES + NOUNS + CONJUNCTIONS \
               + NAMES + VERBS + NUMBERS + ADJECTIVES + NOUNS
n_trials_per_block = len(rates)*n_trials_per_block_per_rate

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
word_submission_queue = WordQueue(win, n_slots=11, y_pos=7.5, gap=1, width=3, height=1)
word_answer_queue     = WordQueue(win, n_slots=11, y_pos=5,   gap=1, width=3, height=1)
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
wait_for_push_button(win, push_button, mouse)

for block_num in range(n_blocks):
    block_stim_list = set_stimuli_for_block(n_trials_per_block_per_rate,
                                            conditions, run_data)

    # Set ready screen
    block_ready_txt = "BLOCK {:d} of {:d}\n\nPress NEXT when ready.".format(
                      block_num + 1, n_blocks)
    helper_text.set_text(block_ready_txt)
    helper_text.draw()
    push_button.draw()
    push_button.set_text("NEXT")
    win.flip()
    wait_for_push_button(win, push_button, mouse)

    for trial_num in range(n_trials_per_block):
        # Display trial number
        trial_txt = "BLOCK {:d}/{:d};\tTRIAL {:d}/{:d}".format(
                     block_num + 1, n_blocks, trial_num + 1, n_trials_per_block)
        helper_text.set_pos((0, 5))
        helper_text.set_text(trial_txt)
        helper_text.draw()
        win.flip()

        # Make and play stimulus
        stimulus, stimulus_ID, target_sentence_items = block_stim_list[trial_num]
        core.wait(0.25)
        stimulus.play(blocking=True)

        # Wait for subject response
        subj_response, correct = \
            do_word_recall_task(win, push_button, mouse, helper_text,
                                word_submission_queue, word_answer_queue,
                                word_grid_interface,
                                target_sentence_items)
        elapsed_time = expt_timer.getTime()

        # Save data
        run_data = run_data.append(
            {"run_num": run_num,
             "subject_ID": subject_ID,
             "task_type": task_type,
             "block_num": block_num + 1,
             "trial_num": trial_num + 1,
             "stimulus_ID": stimulus_ID,
             "subj_response": " ".join(subj_response),
             "correct": correct,
             "elapsed_time": elapsed_time},
             ignore_index=True)
        run_data.to_csv(save_path, index=False)
# End screen
helper_text.set_text("Run complete! Please see experimenter.")
helper_text.draw()
win.flip()
wait_for_push_button(win, push_button, mouse)
################################################################################
# END EXPT
################################################################################
exit_program(win)
