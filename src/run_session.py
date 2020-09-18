import os

from psychopy import core, visual, event

# Project imports
from utils.init_constants import *
from utils.stim_tools import *
from utils.GUI_components import *
from utils.GUI_routines import *


################################################################################
# EXPT PARAMETERS
################################################################################
SUBJECT_ID = "test"
TASK_TYPE = "SOS"

# Session parameters
N_BLOCKS = 3
N_TRIALS = 100
ANSWER_CHOICES = VERBS + NUMBERS + ADJECTIVES + NOUNS + CONJUNCTIONS \
               + NAMES + VERBS + NUMBERS + ADJECTIVES + NOUNS

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
word_submission_queue = WordQueue(win, n_slots=11, y_pos=7.5, width=2)
word_answer_queue     = WordQueue(win, n_slots=11, y_pos=5,   width=2)
word_grid_interface   = WordGridInterface(win, column_len=len(VERBS),
                                          words_in_grid=ANSWER_CHOICES)


################################################################################
# RUN EXPT LOOP
################################################################################
for _ in range(N_TRACKS):
    # Calculate current track number
    TRACK_NUM = int(sorted([fn for fn in os.listdir(SAVE_DIR)
                            if "TRACK" in fn])[-1].split("_")[0][-3:]) + 1
    file_name = "TRACK" + str(TRACK_NUM).zfill(3) + "_" + SUBJECT_ID + "_" \
                   + TASK_TYPE + "_" + MASK_TYPE + ".csv"
    save_path = DATA_DIR/file_name

    # New data file
    run_data = pd.DataFrame(columns=DATA_COLUMNS)

    # Set ready screen
    helper_text.set_text("Speech on speech staircase.\n\nPress NEXT when ready.")
    push_button.set_text("NEXT")

    helper_text.draw()
    push_button.draw()
    win.flip()

    # Intro screen
    while not push_button.is_pressed():
        mouse.clickReset()

        # Check for exit keyboard input
        exit_keys = event.getKeys(keyList=EXIT_KEYS)
        if exit_keys:
            exit_program(win)

        # Get mouse clicks
        if mouse.left_click_released():
            curr_mouse_pos = mouse.getPos()
            # Check if the mouse cursor is contained in push button
            if push_button.contains(curr_mouse_pos):
                push_button.set_pressed()

    # Change push button text and reset
    push_button.reset_pressed()
    push_button.set_text("SUBMIT")

    ###
    # RUN STAIRCASE
    staircase_timer = core.Clock()
    while curr_rev < N_REVERSALS and curr_trial < MAX_TRIALS:
        # Display trial number
        helper_text.set_pos((0, 5))
        helper_text.set_text("TRACK {:d};\tTRIAL {:d};\t{:d}/{:d} reversals".format(
                              TRACK_NUM, curr_trial + 1, curr_rev, N_REVERSALS - 1))
        helper_text.draw()
        win.flip()

        L_total = np.random.uniform(*COMBINED_LEVEL_LIMITS)
        # Make stimulus
        stimulus = stimulus.make_binaural()

        # Play stimulus
        core.wait(0.2)
        stimulus.play(blocking=True)

        # Get subject response
        subj_response, subj_response_correct = \
            do_word_recall_task(win, mouse,
                                word_submission_queue, word_answer_queue,
                                word_grid_interface, helper_text, push_button,
                                N_PATTERNS, target_sentence_items)

        # Save data
        elapsed_time = staircase_timer.getTime()
        RUN_DATA = RUN_DATA.append(
            {"trial_num": curr_trial + 1,
             "curr_direction": curr_dir,
             "curr_reversals": curr_rev,
             "curr_consecutive_correct": curr_consec,
             "curr_trial_correct": curr_corr,
             "total_level": L_total,
             "target_level": L_targ,
             "masker_levels": L_maskers,
             "curr_TMR": curr_TMR,
             "elapsed_time": elapsed_time},
             ignore_index=True )
        RUN_DATA.to_csv(DATA_SAVE_PATH, index=False)

        curr_trial += 1

    # End of run screen
    helper_text.set_pos((0, 0))
    helper_text.set_text("End of track")
    push_button.set_text("FINISH")

    helper_text.draw()
    push_button.draw()
    win.flip()

    while not push_button.is_pressed():
        mouse.clickReset()

        # Check for exit keyboard input
        exit_keys = event.getKeys(keyList=EXIT_KEYS)
        if exit_keys:
            exit_program(win)

        # Get mouse clicks
        if mouse.left_click_released():
            curr_mouse_pos = mouse.getPos()
            # Check if the mouse cursor is contained in push button
            if push_button.contains(curr_mouse_pos):
                push_button.set_pressed()

    win.flip()
    push_button.reset_pressed()
    core.wait(0.5)

################################################################################
# END EXPT
################################################################################
exit_program(win)
