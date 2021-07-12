# Project imports
from utils.init_constants import *
from utils.stim_tools import *
from utils.GUI_components import *
from utils.GUI_routines import *


session_timer = core.Clock()
################################################################################
# EXPT PARAMETERS
################################################################################
# Session parameters
stim_database = pd.read_csv(STIM_DIR/"stimulus_database.csv")
subject_ID = "AYC"
run_num = len([x for x in DATA_DIR.glob("*.csv")])
n_srcs = np.array([3])
targ_amps = np.array([0., 15., 30.])

## CHOOSE TASK TYPE
task_type = "motion_detection"
# task_type = "speech_intelligibility"
# stim_type = "BUG"
stim_type = "SMN"
n_trials_per_amp = 60
n_trials = len(targ_amps)*n_trials_per_amp
run_stim_order = choose_stim_for_run(stim_type,
                                     stim_database,
                                     targ_amps,
                                     n_trials_per_amp)

# Set save file path and create data structure
file_name = "RUN_" + str(run_num).zfill(3) + ".csv"
save_path = DATA_DIR/file_name
run_data = pd.DataFrame(columns=DATA_COLUMNS)
answer_choices = NAMES + VERBS + NUMBERS + ADJECTIVES + NOUNS

# Initialize GUI elements
win = visual.Window(fullscr=True, winType="pyglet",
                    monitor="testMonitor", units="norm")
mouse = CustomMouse(win=win)
helper_text = SupportText(win)
push_button = PushButton(win, pos=(0, -0.7))
afc_interface = AFCInterface(win)
word_grid_interface = WordGridInterface(win, column_len=len(VERBS),
                                        words_in_grid=answer_choices,
                                        x_offset=-0.5, y_offset=0.4,
                                        word_box_width=0.25, word_box_height=0.125)
subject_queue = WordQueue(win, n_slots=5, gap=0.05, width=0.2, height=0.125, y_pos=0.65)
answer_queue  = WordQueue(win, n_slots=5, gap=0.05, width=0.2, height=0.125, y_pos=0.5)


################################################################################
# MAIN BODY
################################################################################

################################################################################
################################################################################
if stim_type == "SMN":
    # ###
    # # TUTORIAL
    # tutorial_strs = make_tutorial_strs(task_type, stim_type)
    #
    # # Read in examples
    # for f in sorted(os.listdir(EXMP_DIR)):
    #     if f.startswith("detection") and f.endswith(".txt"):
    #         with open(EXMP_DIR/f, "r") as fin:
    #             lines = fin.readlines()
    # ex_target_idxs = [int(i) for i in lines]
    # ex_stims = [SoundLoader(EXMP_DIR/f) for f in sorted(os.listdir(EXMP_DIR))
    #             if f.startswith("detection") and
    #                f.endswith(".wav")]
    #
    # for i, curr_str in enumerate(tutorial_strs):
    #     if i == 0: # Intro screen
    #         helper_text.set(text=curr_str, pos=(0, 0.2))
    #         helper_text.draw()
    #         push_button.set(text="NEXT")
    #         push_button.draw()
    #         win.flip()
    #         wait_for_push_button(win, mouse, push_button)
    #     elif i == 1 or i == 2: # Examples 1 & 2
    #         curr_stim = ex_stims[i - 1]
    #         helper_text.set(text=curr_str, pos=(0, 0))
    #         helper_text.draw()
    #         win.flip()
    #         core.wait(2)
    #         curr_stim.play(blocking=True)
    #         core.wait(0.5)
    #         helper_text.draw()
    #         push_button.draw()
    #         win.flip()
    #         wait_for_push_button(win, mouse, push_button)
    #     elif i == 3 or i == 4 or i == 5 or i == 6: # Example 3-6
    #         curr_targ_idx = ex_target_idxs[i - 1]
    #         curr_stim = ex_stims[i - 1]
    #         helper_text.set(text=curr_str)
    #         helper_text.draw()
    #         push_button.set(text="PLAY")
    #         push_button.draw()
    #         win.flip()
    #         wait_for_push_button(win, mouse, push_button)
    #         helper_text.draw()
    #         win.flip()
    #         curr_stim.play(blocking=True)
    #         core.wait(0.5)
    #
    #         helper_text.set(text=" ", pos=(0, -0.2))
    #         _, _ = \
    #             do_detection_task(win, mouse, push_button, helper_text,
    #                               afc_interface, curr_targ_idx)
    #
    #         helper_text.draw()
    #         push_button.set(text="NEXT")
    #         push_button.draw()
    #         win.flip()
    #         wait_for_push_button(win, mouse, push_button)
    #     else: # warn_str and final_str
    #         helper_text.set(text=curr_str)
    #         helper_text.draw()
    #         push_button.set(text="NEXT")
    #         push_button.draw()
    #         win.flip()
    #         wait_for_push_button(win, mouse, push_button)

    #####
    # Main experiment section - detection task
    task_instruction_str =\
        "Now we will begin the experiment. As in the tutorial, please "\
        "identify the moving talker. The amount of motion in the moving "\
        "talker may vary from trial to trial.\n\n\n"\
        "Press 'START' when you are ready to begin."
    helper_text.set(text=task_instruction_str, pos=(0, 0.2))
    helper_text.draw()
    push_button.set(text="START")
    push_button.draw()
    win.flip()
    wait_for_push_button(win, mouse, push_button)

    # Main loop
    for trial_num, (stim_num, stim, target_idx, _) in enumerate(run_stim_order):
        # Display trial number
        trial_txt = "Trial {:d} of {:d}".format(trial_num + 1, n_trials)
        helper_text.set(text=trial_txt, pos=(0, 0.75))
        helper_text.draw()
        win.flip()

        # Play stimulus
        core.wait(0.25)
        stim.play(blocking=True)

        # Wait for subject response
        subj_response, correct = \
            do_detection_task(win, mouse, push_button, helper_text,
                              afc_interface, target_idx)
        elapsed_time = session_timer.getTime()

        # Save data
        run_data = run_data.append(
            {"run_num": run_num,
             "subject_ID": subject_ID,
             "stim_type": stim_type,
             "task_type": task_type,
             "block_num": 0,
             "trial_num": trial_num + 1,
             "stim_num": stim_num,
             "subj_response": subj_response_str,
             "correct": correct,
             "elapsed_time": elapsed_time},
             ignore_index=True)
        run_data.to_csv(save_path, index=False)

################################################################################
################################################################################
elif task_type == "motion_detection":
    ###
    # TUTORIAL
    tutorial_strs = make_tutorial_strs(task_type, stim_type)

    # Read in examples
    for f in sorted(os.listdir(EXMP_DIR)):
        if f.startswith("detection") and f.endswith(".txt"):
            with open(EXMP_DIR/f, "r") as fin:
                lines = fin.readlines()
    ex_target_idxs = [int(i) for i in lines]
    ex_stims = [SoundLoader(EXMP_DIR/f) for f in sorted(os.listdir(EXMP_DIR))
                if f.startswith("detection") and
                   f.endswith(".wav")]

    for i, curr_str in enumerate(tutorial_strs):
        if i == 0: # Intro screen
            helper_text.set(text=curr_str, pos=(0, 0.2))
            helper_text.draw()
            push_button.set(text="NEXT")
            push_button.draw()
            win.flip()
            wait_for_push_button(win, mouse, push_button)
        elif i == 1 or i == 2: # Examples 1 & 2
            curr_stim = ex_stims[i - 1]
            helper_text.set(text=curr_str, pos=(0, 0))
            helper_text.draw()
            win.flip()
            core.wait(2)
            curr_stim.play(blocking=True)
            core.wait(0.5)
            helper_text.draw()
            push_button.draw()
            win.flip()
            wait_for_push_button(win, mouse, push_button)
        elif i == 3 or i == 4 or i == 5 or i == 6: # Example 3-6
            curr_targ_idx = ex_target_idxs[i - 1]
            curr_stim = ex_stims[i - 1]
            helper_text.set(text=curr_str)
            helper_text.draw()
            push_button.set(text="PLAY")
            push_button.draw()
            win.flip()
            wait_for_push_button(win, mouse, push_button)
            helper_text.draw()
            win.flip()
            curr_stim.play(blocking=True)
            core.wait(0.5)

            helper_text.set(text=" ", pos=(0, -0.2))
            _, _ = \
                do_detection_task(win, mouse, push_button, helper_text,
                                  afc_interface, curr_targ_idx)

            helper_text.draw()
            push_button.set(text="NEXT")
            push_button.draw()
            win.flip()
            wait_for_push_button(win, mouse, push_button)
        else: # warn_str and final_str
            helper_text.set(text=curr_str)
            helper_text.draw()
            push_button.set(text="NEXT")
            push_button.draw()
            win.flip()
            wait_for_push_button(win, mouse, push_button)

    #####
    # Main experiment section - detection task
    task_instruction_str =\
        "Now we will begin the experiment. As in the tutorial, please "\
        "identify the moving talker. The amount of motion in the moving "\
        "talker may vary from trial to trial.\n\n\n"\
        "Press 'START' when you are ready to begin."
    helper_text.set(text=task_instruction_str, pos=(0, 0.2))
    helper_text.draw()
    push_button.set(text="START")
    push_button.draw()
    win.flip()
    wait_for_push_button(win, mouse, push_button)

    # Main loop
    for trial_num, (stim_num, stim, target_idx, _) in enumerate(run_stim_order):
        # Display trial number
        trial_txt = "Trial {:d} of {:d}".format(trial_num + 1, n_trials)
        helper_text.set(text=trial_txt, pos=(0, 0.75))
        helper_text.draw()
        win.flip()

        # Play stimulus
        core.wait(0.25)
        stim.play(blocking=True)

        # Wait for subject response
        subj_response, correct = \
            do_detection_task(win, mouse, push_button, helper_text,
                              afc_interface, target_idx)
        elapsed_time = session_timer.getTime()

        # Save data
        run_data = run_data.append(
            {"run_num": run_num,
             "subject_ID": subject_ID,
             "stim_type": stim_type,
             "task_type": task_type,
             "block_num": 0,
             "trial_num": trial_num + 1,
             "stim_num": stim_num,
             "subj_response": subj_response_str,
             "correct": correct,
             "elapsed_time": elapsed_time},
             ignore_index=True)
        run_data.to_csv(save_path, index=False)

################################################################################
################################################################################
elif task_type == "speech_intelligibility":
    ###
    # TUTORIAL
    tutorial_strs = make_tutorial_strs(task_type, stim_type)

    # Read in examples
    for f in sorted(os.listdir(EXMP_DIR)):
        if f.startswith("speech_ID") and f.endswith(".txt"):
            with open(EXMP_DIR/f, "r") as fin:
                lines = fin.readlines()
    ex_target_idxs = [int(i) for i in lines]
    ex_stims = [SoundLoader(EXMP_DIR/f) for f in sorted(os.listdir(EXMP_DIR))
                if f.startswith("speech_ID") and
                   f.endswith(".wav")]
    # Hardcoded answers to example stimuli
    # MUST BE UPDATED EVERY TIME NEW EXAMPLES ARE MADE
    speech_ID_ex_answers = ["MIKE GAVE THREE CHEAP SHOES",
                            "BOB TOOK THREE BIG TOYS",
                            "LYNN LOST NINE RED HATS",
                            "JANE GAVE TEN HOT HATS",
                            "SAM SAW SIX RED SHOES",
                            "JANE BOUGHT TWO SMALL SHOES"]

    for i, curr_str in enumerate(tutorial_strs):
        if i == 0: # Intro screen
            helper_text.set(text=curr_str, pos=(0, 0.2))
            helper_text.draw()
            push_button.set(text="NEXT")
            push_button.draw()
            win.flip()
            wait_for_push_button(win, mouse, push_button)
        elif i == 1 or i == 2 or i == 3 or i == 4 or i == 5 or i == 6: # Examples 1-6
            curr_targ_idx = ex_target_idxs[i - 1]
            curr_stim = ex_stims[i - 1]
            curr_ans = speech_ID_ex_answers[i - 1]
            curr_ans_items = curr_ans.split()
            helper_text.set(text=curr_str)
            helper_text.draw()
            push_button.set(text="PLAY")
            push_button.draw()
            win.flip()
            wait_for_push_button(win, mouse, push_button)
            helper_text.draw()
            win.flip()
            curr_stim.play(blocking=True)
            core.wait(0.5)

            _, _ = \
                do_recall_task(win, mouse, push_button, helper_text,
                               subject_queue, answer_queue,
                               word_grid_interface, curr_ans_items)
        else: # warn_str and final_str
            helper_text.set(text=curr_str)
            helper_text.draw()
            push_button.set(text="NEXT")
            push_button.draw()
            win.flip()
            wait_for_push_button(win, mouse, push_button)

    #####
    # Main experiment section - speech ID
    # Show task instructions
    task_instruction_str =\
        "Now we will begin the experiment. After each trial, please respond "\
        "with the words spoken by the moving talker in the correct order. The "\
        "amount of motion in the moving talker may vary from trial to "\
        "trial.\n\n\n"\
        "Press 'START' when you are ready to begin."
    helper_text.set(text=task_instruction_str, pos=(0, 0.2))
    helper_text.draw()
    push_button.set(text="START")
    push_button.draw()
    win.flip()
    wait_for_push_button(win, mouse, push_button)

    for trial_num, (stim_num, stim, _, target_pattern) in enumerate(run_stim_order):
        # Display trial number
        trial_txt = "Trial {:d} of {:d}".format(trial_num + 1, n_trials)
        helper_text.set(text=trial_txt, pos=(0, 0.75))
        helper_text.draw()
        win.flip()

        # Play stimulus
        core.wait(0.25)
        stim.play(blocking=True)

        # Wait for subject response
        curr_ans_items = target_pattern.split()
        subj_response, correct = \
            do_recall_task(win, mouse, push_button, helper_text,
                           subject_queue, answer_queue,
                           word_grid_interface, curr_ans_items)
        subj_response_str = " ".join(subj_response)
        elapsed_time = session_timer.getTime()

        # Save data
        run_data = run_data.append(
            {"run_num": run_num,
             "subject_ID": subject_ID,
             "stim_type": stim_type,
             "task_type": task_type,
             "block_num": 0,
             "trial_num": trial_num + 1,
             "stim_num": stim_num,
             "subj_response": subj_response_str,
             "correct": correct,
             "elapsed_time": elapsed_time},
             ignore_index=True)
        run_data.to_csv(save_path, index=False)
################################################################################
################################################################################
else:
    raise ValueError('invalid task_type; must be "motion_detection" or "speech_intelligibility"')

################################################################################
################################################################################
# End screen
helper_text.set(text="Run complete!\n\nPlease see the experimenter.",
                pos=(0, 0.5))
helper_text.draw()
win.flip()
wait_for_push_button(win, mouse, push_button)

################################################################################
# END EXPT
################################################################################
exit_program(win)
