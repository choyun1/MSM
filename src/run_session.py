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
n_srcs = np.array([2, 3, 4])
targ_amps = np.array([0., 1.25, 5., 20.])
n_trials_per_block_per_amp = 5
run_stim_order, src_order = \
    choose_stim_for_run(stim_database,
                        n_srcs,
                        targ_amps,
                        n_trials_per_block_per_amp,
                        balanced=True)

# Set save file path and create data structure
file_name = "RUN_" + str(run_num).zfill(3) + ".csv"
save_path = DATA_DIR/file_name
run_data = pd.DataFrame(columns=DATA_COLUMNS)
answer_choices = NAMES + VERBS + NUMBERS + ADJECTIVES + NOUNS

# Initialize GUI elements
win = visual.Window(fullscr=True, winType="pyglet",
                    monitor="testMonitor", units="deg")
mouse = CustomMouse(win=win)
word_grid_interface   = WordGridInterface(win, column_len=len(VERBS),
                                          words_in_grid=answer_choices,
                                          x_offset=-8.5, y_offset=3,
                                          word_box_width=4, word_box_height=1.5)
answer_queue     = WordQueue(win, n_slots=5, gap=1, width=3, height=1, y_pos=5)
submission_queue = WordQueue(win, n_slots=5, gap=1, width=3, height=1, y_pos=7.5)
helper_text = SupportText(win)
push_button = PushButton(win)

################################################################################
# RUN EXPT LOOP
################################################################################
# Pre-generate example stimuli
ex1_stim = make_ex(1, 20)
ex2_stim = make_ex(1, 20)
ex3_stim = make_ex(2, 20)
ex4_stim = make_ex(2, 20)
ex5_stim = make_ex(4, 20)
ex6_stim = make_ex(1, 1.25)
ex7_stim = make_ex(3, 1.25)

# Start timer
expt_timer = core.Clock()

######
# Intro screen
intro_str = make_intro()
helper_text.set(text=intro_str, pos=(0, 0))
helper_text.draw()
push_button.set_text("NEXT")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)

######
# Example 1
ex1_str = ex1()
helper_text.set(text=ex1_str, pos=(0, 0), size=(16, 8))
helper_text.draw()
win.flip()
core.wait(2)
ex1_stim.play(blocking=True)
core.wait(0.5)
helper_text.draw()
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)

######
# Example 2
ex2_str = ex2()
helper_text.set(text=ex2_str, pos=(0, 0), size=(16, 8))
helper_text.draw()
win.flip()
core.wait(2)
ex2_stim.play(blocking=True)
core.wait(0.5)
helper_text.draw()
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)

######
# Example 3
ex3_str = ex3()
helper_text.set(text=ex3_str, pos=(0, 0), size=(16, 8))
helper_text.draw()
push_button.set_text("PLAY")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)
helper_text.draw()
win.flip()
ex3_stim.play(blocking=True)
core.wait(0.5)
helper_text.draw()
push_button.set_text("NEXT")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)

######
# Example 4
ex4_str = ex4()
helper_text.set(text=ex4_str, pos=(0, 0), size=(16, 8))
helper_text.draw()
push_button.set_text("PLAY")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)
helper_text.draw()
win.flip()
ex4_stim.play(blocking=True)
core.wait(0.5)
helper_text.draw()
push_button.set_text("NEXT")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)

######
# Example 5
ex5_str = ex5()
helper_text.set(text=ex5_str, pos=(0, 0), size=(16, 8))
helper_text.draw()
push_button.set_text("PLAY")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)
helper_text.draw()
win.flip()
ex5_stim.play(blocking=True)
core.wait(0.5)
helper_text.draw()
push_button.set_text("NEXT")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)


######
# Example 6
ex6_str = ex6()
helper_text.set(text=ex6_str, pos=(0, 0), size=(16, 8))
helper_text.draw()
push_button.set_text("PLAY")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)
helper_text.draw()
win.flip()
ex6_stim.play(blocking=True)
core.wait(0.5)
helper_text.draw()
push_button.set_text("NEXT")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)


######
# Example 7
ex7_str = ex7()
helper_text.set(text=ex7_str, pos=(0, 0), size=(16, 8))
helper_text.draw()
push_button.set_text("PLAY")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)
helper_text.draw()
win.flip()
ex7_stim.play(blocking=True)
core.wait(0.5)
helper_text.draw()
push_button.set_text("NEXT")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)


#####
# Warning
warn_str = warning()
helper_text.set(text=warn_str, pos=(0, 0), size=(16, 8))
helper_text.draw()
push_button.set_text("NEXT")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)


#####
# Show task instructions
task_instruction_str = make_task_instruction()
helper_text.set(text=task_instruction_str, pos=(0, 0), size=(16, 8))
helper_text.draw()
push_button.set_text("START")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)

n_blocks = len(run_stim_order)
for block_num, block_stim_order in enumerate(run_stim_order):
    # Set ready screen
    block_str = \
        "BLOCK {:d} of {:d}\n\n"\
        "There will be {:d} talkers in this block.\n\n\n"\
        "Click 'NEXT' when ready.".format(block_num + 1, n_blocks, src_order[block_num])
    helper_text.set(text=block_str, pos=(0, 2), size=(16, 6))
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
        helper_text.set(text=trial_txt, pos=(0, 5), size=(6, 3))
        helper_text.draw()
        win.flip()

        # Play stimulus
        core.wait(0.25)
        stim.play(blocking=True)

        # Wait for subject response
        subj_response, correct = \
            do_recall_task(win, mouse, helper_text, push_button,
                           submission_queue, answer_queue,
                           word_grid_interface, target_pattern_items)
        elapsed_time = expt_timer.getTime()

        # Save data
        run_data = run_data.append(
            {"run_num": run_num,
             "subject_ID": subject_ID,
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
