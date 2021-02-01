from psychopy import core, event


def make_task_instruction():
    task_instr_str =\
        "Thank you for participating in this experiment!\n\n"\
        "This is a speech intelligibility task. You will simultaneously "\
        "hear ONE MALE TARGET TALKER and ONE MASKER. The masker may be "\
        "another male talker or a noise source, and you will be informed "\
        "before the start of each block which will be used.\n\n"\
        "You may hear the sounds coming from different locations, and the "\
        "sounds may move around your head. You will be informed if and how "\
        "quickly the sounds will move before the start of each block.\n\n"\
        "The target talker will always begin his sentence with the name 'SUE', "\
        "followed by a RANDOM string of 4 words. Ignore the masker, and respond "\
        "using the word grid interface that appears after the sound is played. "\
        "You may report back the words spoken by the target talker in ANY "\
        "ORDER.\n\n\n"\
        "Press 'NEXT' when ready."
    return task_instr_str


def make_stim_info_str(cond):
    masker_type = "NOISE SOURCE" if cond.stim_type == "SEM" else "MALE TALKER"
    target_rate, masker_rate = cond.target_alt_rate, cond.masker_alt_rate
    rate_to_speed_map = {0:   "be STATIC and not move",
                         0.1: "move VERY SLOWLY",
                         0.5: "move SLOWLY",
                         1:   "move FAST",
                         2:   "move VERY FAST"}
    stim_str = "The MASKER will be a {:s}.\n\n"\
               "The TARGET will {:s}.\nThe MASKER will {:s}.\n\n\n\n".format(\
                masker_type,
                rate_to_speed_map[target_rate],
                rate_to_speed_map[masker_rate])
    return stim_str


def exit_program(win):
    win.close()
    core.quit()


def push_button_wait_logic(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        win = args[0]
        mouse = args[1]
        push_button = args[2]
        while not push_button.is_pressed():
            mouse.clickReset()
            # Check for exit keyboard input
            exit_keys = event.getKeys(keyList=("q", "escape"))
            if exit_keys:
                exit_program(win)
            func(*args, **kwargs)
        push_button.reset_pressed()
    return wrapper


@push_button_wait_logic
def wait_for_push_button(win, mouse, push_button):
    if mouse.left_click_released():
        curr_mouse_pos = mouse.getPos()
        # Check if the mouse cursor is contained in push button
        if push_button.contains(curr_mouse_pos):
            push_button.set_pressed()


@push_button_wait_logic
def grid_logic(win, mouse, push_button, helper_text, n_slots, submission_queue,
               grid_interface):
    # Flip frame
    grid_interface.draw()
    submission_queue.draw()
    # trial_str = "Report back the words spoken by the target talker in the EXACT "
    #             "ORDER by clicking on the words in the grid."
    trial_str = "Report back the words spoken by the target talker in ANY ORDER "\
                "by clicking on the words in the grid."
    helper_text.set(text=trial_str, pos=(0, 10))
    helper_text.draw()
    push_button.draw()
    win.flip()

    # Check for number of selected tone patterns in the submission box
    if len(submission_queue) == n_slots:
        push_button.enable()
    else:
        push_button.disable()

    # Get mouse clicks
    if mouse.left_click_released():
        curr_mouse_pos = mouse.getPos()
        # Check if the mouse cursor is contained in one of the grid choices
        for idx, box in enumerate(grid_interface.word_boxes):
            if box.contains(curr_mouse_pos):
                submission_queue.insert(
                    grid_interface.word_labels[idx].text)
        # Check if the mouse cursor is contained in push button
        if push_button.contains(curr_mouse_pos) and push_button.is_enabled():
            push_button.set_pressed()


def do_recall_task(stim_type, win, mouse, helper_text, push_button,
                   submission_queue, answer_queue,
                   grid_interface, target_patterns):
    # Reset GUI elements
    answer_queue.reset()
    submission_queue.reset()
    submission_queue.reset_borders()
    helper_text.set(text="", color=(0, 0, 0))
    push_button.reset_pressed()
    push_button.set_text("SUBMIT")
    win.flip()

    # Build the correct answer queue
    n_slots = len(target_patterns)
    for item in target_patterns:
        answer_queue.insert(item)
    submission_queue.insert(target_patterns[0]) # always insert correct pattern

    # Wait for user response using the grid interface
    grid_logic(win, mouse, push_button, helper_text, n_slots, submission_queue,
               grid_interface)

    # ### Scoring for answer in EXACT ORDER
    # # Score subject responses, minus the first constant pattern
    # subj_response_correct = \
    #     sum(answer_queue.queue_items[i] == submission_queue.queue_items[i]
    #         for i in range(1, n_slots))
    # # Compare the answer and submission one by one to toggle feedback color
    # for i in range(1, n_slots):
    #     if answer_queue.queue_items[i] == submission_queue.queue_items[i]:
    #         submission_queue.set_border_color(i, (0, 255, 0))
    #     else:
    #         submission_queue.set_border_color(i, (255, 0, 0))
    #     submission_queue.toggle_border(i)

    ### Scoring for answer in ANY ORDER
    # Score subject responses, minus the first constant pattern
    answer_set = set(answer_queue.queue_items[1:])
    submission_set = set(submission_queue.queue_items[1:])
    subj_response_correct = len(answer_set.intersection(submission_set))
    # Compare the answer and submission one by one to toggle feedback color
    for i in range(1, n_slots):
        if submission_queue.queue_items[i] in answer_set:
            submission_queue.set_border_color(i, (0, 255, 0))
        else:
            submission_queue.set_border_color(i, (255, 0, 0))
        submission_queue.toggle_border(i)

    # Display answer and feedback
    helper_text.set(text="CORRECT ANSWERS", pos=(0, 3))
    helper_text.draw()
    # answer_queue.draw()
    submission_queue.draw()
    win.flip()
    core.wait(0.5)

    # Re-draw elements for waiting
    helper_text.set(text="Press 'NEXT' to continue", pos=(0, -2))
    helper_text.draw()
    push_button.set_text("NEXT")
    push_button.enable()
    push_button.draw()
    # answer_queue.draw()
    submission_queue.draw()
    win.flip()
    wait_for_push_button(win, mouse, push_button)

    return submission_queue.queue_items, subj_response_correct


# def do_tone_ID_task(win, mouse, tone_submission_queue, tone_answer_queue,
#                     tone_pattern_interface, helper_text, push_button,
#                     N_PATTERNS, target_pattern_numbers):
#     # Reset GUI elements
#     tone_answer_queue.reset()
#     tone_submission_queue.reset()
#     tone_submission_queue.reset_borders()
#     helper_text.set_text("")
#     helper_text.set_color((0, 0, 0))
#     push_button.reset_pressed()
#     push_button.set_text("SUBMIT")
#     win.flip()
#
#     # Always insert constant pattern into the submission queue
#     tone_submission_queue.insert(0)
#
#     # Check for user input
#     while not push_button.is_pressed():
#         mouse.clickReset()
#
#         # Set helper text
#         helper_text.set_pos((0, 11))
#         helper_text.set_text("Select the patterns in the order they were played.")
#
#         # Check for number of selected tone patterns in the submission box
#         if len(tone_submission_queue) == N_PATTERNS:
#             push_button.enable()
#         else:
#             push_button.disable()
#
#         # Flip frame
#         tone_pattern_interface.draw()
#         tone_submission_queue.draw()
#         helper_text.draw()
#         push_button.draw()
#         win.flip()
#
#         # Check for exit keyboard input
#         exit_keys = event.getKeys(keyList=EXIT_KEYS)
#         if exit_keys:
#             exit_program(win)
#
#         # Get mouse clicks
#         if mouse.left_click_released():
#             curr_mouse_pos = mouse.getPos()
#             # Check if the mouse cursor is contained in one of the grid choices
#             for idx, border in enumerate(tone_pattern_interface.tone_pattern_borders):
#                 if border.contains(curr_mouse_pos):
#                     tone_submission_queue.insert(idx)
#
#             # Check if the mouse cursor is contained in push button
#             if push_button.contains(curr_mouse_pos) and push_button.is_enabled():
#                 push_button.set_pressed()
#
#     # Build the correct answer queue
#     # tone_answer_queue.insert(0)
#     for pattern_num in target_pattern_numbers:
#         tone_answer_queue.insert(pattern_num)
#
#     # Compare the answer and submission one by one to see which is correct
#     for i in range(1, len(tone_submission_queue)):
#         if tone_answer_queue.patterns[i] == tone_submission_queue.patterns[i]:
#             tone_submission_queue.set_border_color(i, (0, 255, 0))
#         else:
#             tone_submission_queue.set_border_color(i, (255, 0, 0))
#         tone_submission_queue.toggle_border(i)
#
#     # Score subject responses, EXCLUDING the first constant pattern
#     subj_response = tone_submission_queue.patterns
#     subj_response_correct = \
#         sum(tone_answer_queue.patterns[i] == subj_response[i]
#             for i in range(1, len(subj_response)))
#
#     # Display answer and feedback
#     helper_text.set_text("CORRECT ANSWER")
#     helper_text.set_pos((-18, 5))
#     tone_answer_queue.draw()
#     tone_submission_queue.draw()
#     helper_text.draw()
#     win.flip()
#
#     core.wait(0.5)
#
#     push_button.reset_pressed()
#     push_button.set_text("NEXT")
#     push_button.enable()
#
#     # Wait for subject to press "NEXT"
#     while not push_button.is_pressed():
#         mouse.clickReset()
#
#         # Flip frame
#         tone_answer_queue.draw()
#         tone_submission_queue.draw()
#         helper_text.draw()
#         push_button.draw()
#         win.flip()
#
#         # Check for exit keyboard input
#         quit_program = event.getKeys(keyList=EXIT_KEYS)
#         if quit_program:
#             win.close()
#             core.quit()
#
#         # Get mouse clicks
#         if mouse.left_click_released():
#             curr_mouse_pos = mouse.getPos()
#
#             # Check if the mouse cursor is contained in push button
#             if push_button.contains(curr_mouse_pos) and push_button.is_enabled():
#                 push_button.set_pressed()
#
#     # Reset GUI elements
#     tone_answer_queue.reset()
#     tone_submission_queue.reset()
#     tone_submission_queue.reset_borders()
#     helper_text.set_text("")
#     helper_text.set_color((0, 0, 0))
#     push_button.reset_pressed()
#     push_button.set_text("SUBMIT")
#
#     return subj_response, subj_response_correct
