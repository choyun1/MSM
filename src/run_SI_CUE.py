from utils.init_constants import *
from utils.stim_tools import *
from utils.GUI_components import *
from utils.GUI_routines import *


session_timer = core.Clock()

###############################################################################
# EXPT PARAMETERS
###############################################################################
# Header information
run_num = len([x for x in DATA_DIR.glob("*.csv")])
file_name = "RUN_" + str(run_num).zfill(3) + ".csv"
save_path = DATA_DIR/file_name
stim_df = pd.read_csv(STIM_DIR/"stimulus_database.csv")
run_data = pd.DataFrame(columns=DATA_COLUMNS)
answer_choices = NAMES + VERBS + NUMBERS + ADJECTIVES + NOUNS

# Session parameters
subject_ID = "test"
task_types = ["BUG-speech_ID"]
targ_amps = [5., 10., 15., 20., 25., 30.]
n_trials_per_task_per_amp = 60
n_trials_per_block_per_amp = 5
n_tasks = len(task_types)
n_amps = len(targ_amps)

# Compute the number of blocks, trials, and run order
n_blocks_per_task, n_blocks, n_trials, n_trials_per_block = \
    compute_n_trials(n_tasks,
                     n_amps,
                     n_trials_per_task_per_amp,
                     n_trials_per_block_per_amp)
task_order = generate_task_order(n_tasks, n_blocks_per_task)
flattened_task_order = [task_idx for row in task_order for task_idx in row]
run_stim_order = \
    generate_run_stim_order(stim_df,
                            task_types,
                            targ_amps,
                            n_trials_per_task_per_amp,
                            n_trials_per_block_per_amp,
                            n_blocks_per_task,
                            task_order)

# Initialize GUI elements
win = visual.Window(fullscr=True, winType="pyglet",
                    monitor="testMonitor", units="norm")
mouse = CustomMouse(win=win)
helper_text = SupportText(win)
push_button = PushButton(win, pos=(0, -0.7))
afc_interface = AFCInterface(win)
word_grid_interface = WordGridInterface(win,
                                        column_len=len(VERBS),
                                        words_in_grid=answer_choices,
                                        x_offset=-0.5,
                                        y_offset=0.4,
                                        word_box_width=0.25,
                                        word_box_height=0.125)
subject_queue = WordQueue(win, n_slots=5, gap=0.05,
                          width=0.2, height=0.125, y_pos=0.65)
answer_queue = WordQueue(win, n_slots=5, gap=0.05,
                         width=0.2, height=0.125, y_pos=0.5)

###############################################################################
# PRACTICE
###############################################################################
practice_targ_amps = [30.]
n_practice_trials_per_task_per_amp = 20
n_practice_trials_per_block_per_amp = 20
n_practice_tasks = len(task_types)
n_practice_amps = len(practice_targ_amps)

n_practice_blocks_per_task, n_practice_blocks, \
    n_practice_trials, n_practice_trials_per_block = \
    compute_n_trials(n_practice_tasks,
                     n_practice_amps,
                     n_practice_trials_per_task_per_amp,
                     n_practice_trials_per_block_per_amp)
practice_task_order = np.array([[0]])
practice_flattened_task_order = [0]
practice_stim_order = \
    generate_run_stim_order(stim_df,
                            task_types,
                            practice_targ_amps,
                            n_practice_trials_per_task_per_amp,
                            n_practice_trials_per_block_per_amp,
                            n_practice_blocks_per_task,
                            practice_task_order)

practice_str = \
    "Thank you for participating in this experiment. In this task, we will " \
    "ask you to repeat back the words spoken by the MOVING talker. We will " \
    "always inform you which talker will be moving before you hear the " \
    "sentence (i.e. LEFT, CENTER, or RIGHT). Please use this information " \
    "to aid you in the task.\n\n" \
    "We will begin by doing some practice. Press 'NEXT' when ready."
helper_text.set(text=practice_str, pos=(0, 0.2))
helper_text.draw()
push_button.set(text="NEXT")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)

# Iterate through blocks
for block_num, block_stim_nums in enumerate(practice_stim_order):
    curr_task_idx = practice_flattened_task_order[block_num]
    stim_type, task_type = task_types[curr_task_idx].split("-")
    block_tuple = generate_block_tuples(stim_df, block_stim_nums)

    # Show current block information
    stim_type_str = "SPEECH"
    task_type_str = "SPEECH IDENTIFICATION"
    curr_block_str = \
        "Block {:d} of {:d}\n\nThis is a {:s} task with {:s} sound sources." \
        "\n\n\nPress 'START' when you are ready.".format(
            block_num + 1, n_practice_blocks, task_type_str, stim_type_str)
    helper_text.set(text=curr_block_str, pos=(0, 0.2))
    helper_text.draw()
    push_button.set(text="START")
    push_button.draw()
    win.flip()
    wait_for_push_button(win, mouse, push_button)

    # Iterate through trials
    for trial_num, (stim_num, stim, target_idx, target_pattern) \
            in enumerate(block_tuple):
        # True answer
        if target_idx == 0:
            target_loc_str = "LEFT"
        elif target_idx == 1:
            target_loc_str = "CENTER"
        else:
            target_loc_str = "RIGHT"

        # Display trial number
        trial_txt = "Block {:d} of {:d}\nTrial {:d} of {:d}".format(
            block_num + 1, n_practice_blocks,
            trial_num + 1, n_practice_trials_per_block)
        cue_txt = "\n\n\nThe moving talker's location is\n\n{:s}".format(
            target_loc_str)
        helper_text.set(text=trial_txt + cue_txt, pos=(0, 0.25))
        helper_text.draw()
        win.flip()

        # Play stimulus
        core.wait(1.8)
        stim.play(blocking=True)

        # Wait for subject response and display feedback
        if task_type == "speech_ID":
            ans_items = target_pattern.split()
            subj_response, correct = \
                do_recall_task(win, mouse, push_button, helper_text,
                               subject_queue, answer_queue,
                               word_grid_interface, ans_items)
            subj_response_str = " ".join(subj_response)
        else:
            raise ValueError("invalid task_type")

        # Get time information
        elapsed_time = session_timer.getTime()
        now = datetime.now()
        local_dt = LOCAL_TZ.localize(now, is_dst=None)
        now_utc = local_dt.astimezone(utc)
        timestr = convert_datatime_to_timestamp(now_utc)

        # Save data
        run_data = run_data.append(
            {"run_num": run_num,
             "subject_ID": subject_ID,
             "stim_type": "BUG",
             "task_type": "pre-cue_SI",
             "block_num": "P" + str(block_num + 1),
             "trial_num": trial_num + 1,
             "stim_num": stim_num,
             "subj_response": subj_response_str,
             "correct": correct,
             "elapsed_time": elapsed_time,
             "timestamp": timestr},
            ignore_index=True)
        run_data.to_csv(save_path, index=False)

    # End of block screen
    end_block_str = "End of practice block {:d}\n\n".format(block_num + 1)
    helper_text.set(text=end_block_str, pos=(0, 0.1))
    helper_text.draw()
    push_button.set(text="CONTINUE")
    push_button.draw()
    win.flip()
    wait_for_push_button(win, mouse, push_button)

practice_finish_str = \
    "Practice complete!\n\n\nPress 'NEXT' when ready."
helper_text.set(text=practice_finish_str, pos=(0, 0.2))
helper_text.draw()
push_button.set(text="NEXT")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)

###############################################################################
# MAIN BODY
###############################################################################
start_expt_str = \
    "Now we will begin the experiment. As in the practice blocks, you will " \
    "be asked to report back the words spoken by the MOVING talker." \
    "You will always be informed which talker will be moving BEFORE the " \
    "sound is played. The amount of movement in the moving sound will vary " \
    "each trial from small to large or anything in-between.\n\n" \
    "Please remember to take breaks between the blocks if you are getting " \
    "fatigued."
helper_text.set(text=start_expt_str, pos=(0, 0.2))
helper_text.draw()
push_button.set(text="NEXT")
push_button.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)

# Iterate through blocks
for block_num, block_stim_nums in enumerate(run_stim_order):
    curr_task_idx = flattened_task_order[block_num]
    stim_type, task_type = task_types[curr_task_idx].split("-")
    block_tuple = generate_block_tuples(stim_df, block_stim_nums)

    # Show current block information
    stim_type_str = "SPEECH"
    task_type_str = "SPEECH IDENTIFICATION"
    curr_block_str = \
        "Block {:d} of {:d}\n\nThis is a {:s} task with {:s} sound sources." \
        "\n\n\nPress 'START' when you are ready.".format(
            block_num + 1, n_blocks, task_type_str, stim_type_str)
    helper_text.set(text=curr_block_str, pos=(0, 0.2))
    helper_text.draw()
    push_button.set(text="START")
    push_button.draw()
    win.flip()
    wait_for_push_button(win, mouse, push_button)

    # Iterate through trials
    for trial_num, (stim_num, stim, target_idx, target_pattern) \
            in enumerate(block_tuple):
        # True answer
        if target_idx == 0:
            target_loc_str = "LEFT"
        elif target_idx == 1:
            target_loc_str = "CENTER"
        else:
            target_loc_str = "RIGHT"

        # Display trial number
        trial_txt = "Block {:d} of {:d}\nTrial {:d} of {:d}".format(
            block_num + 1, n_blocks,
            trial_num + 1, n_trials_per_block)
        cue_txt = "\n\n\nThe moving talker's location is\n\n{:s}".format(
            target_loc_str)
        helper_text.set(text=trial_txt + cue_txt, pos=(0, 0.25))
        helper_text.draw()
        win.flip()

        # Play stimulus
        core.wait(1.8)
        stim.play(blocking=True)

        # Wait for subject response and display feedback
        if task_type == "speech_ID":
            ans_items = target_pattern.split()
            subj_response, correct = \
                do_recall_task(win, mouse, push_button, helper_text,
                               subject_queue, answer_queue,
                               word_grid_interface, ans_items)
            subj_response_str = " ".join(subj_response)
        else:
            raise ValueError("invalid task_type")

        # Get time information
        elapsed_time = session_timer.getTime()
        now = datetime.now()
        local_dt = LOCAL_TZ.localize(now, is_dst=None)
        now_utc = local_dt.astimezone(utc)
        timestr = convert_datatime_to_timestamp(now_utc)

        # Save data
        run_data = run_data.append(
            {"run_num": run_num,
             "subject_ID": subject_ID,
             "stim_type": "BUG",
             "task_type": "pre-cue_SI",
             "block_num": block_num + 1,
             "trial_num": trial_num + 1,
             "stim_num": stim_num,
             "subj_response": subj_response_str,
             "correct": correct,
             "elapsed_time": elapsed_time,
             "timestamp": timestr},
            ignore_index=True)
        run_data.to_csv(save_path, index=False)

    # End of block screen
    end_block_str = "End of block {:d}\n\n".format(block_num + 1)
    helper_text.set(text=end_block_str, pos=(0, 0.1))
    helper_text.draw()
    push_button.set(text="CONTINUE")
    push_button.draw()
    win.flip()
    wait_for_push_button(win, mouse, push_button)

###############################################################################
###############################################################################
# End screen
helper_text.set(text="Run complete!\n\nPlease see the experimenter.",
                pos=(0, 0.5))
helper_text.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)

exit_program(win)
