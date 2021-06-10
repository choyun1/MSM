from psychopy import core, event


def exit_program(win):
    win.close()
    core.quit()


def make_tutorial_strs(task_type):
    if task_type == "motion_detection":
        intro_str = \
            "Thank you for your participation!\n\n"\
            "The first part of this experiment is a MOTION DETECTION task. We "\
            "will walk through a small tutorial to familiarize you with the "\
            "task.\n\n"\
            "Press 'NEXT' to continue."
        ex1_str = \
            "Here is an example of a single talker moving back and forth around "\
            "the CENTER.\n\nPlease listen closely."
        ex2_str = "Here is another example of a moving talker."
        ex3_str = \
            "In the actual experiment, you will be presented with three "\
            "talkers located LEFT, CENTER, and RIGHT. You must "\
            "identify the one talker that is MOVING back and forth.\n\n"\
            "Here is an example with three talkers. Press 'PLAY' when ready."
        ex4_str = "Here is another example.\n\nPress 'PLAY' when ready."
        ex5_str = "Here is one more example.\n\nPress 'PLAY' when ready."
        ex6_str = \
            "The amount of movement may change from trial to trial. The "\
            "movement is very slight in this example.\n\nPress 'PLAY' when ready."
        warn_str = \
            "On some trials, the movement may be so small that it is "\
            "difficult to identify the moving talker. In such cases, simply "\
            "make your best guess."
        final_str = "This concludes the tutorial.\n\nPress 'NEXT' to continue."
        return intro_str,\
               ex1_str,\
               ex2_str,\
               ex3_str,\
               ex4_str,\
               ex5_str,\
               ex6_str,\
               warn_str,\
               final_str
    else:
        intro_str = \
            "This is the SPEECH IDENTIFICATION portion of the experiment. As "\
            "before, you will listen to a sound mixture of three male "\
            "speakers. This time, you will be asked to report back the words "\
            "spoken by the moving talker.\n\n"\
            "Press 'NEXT' to continue."
        ex1_str = \
            "Here is a practice trial. Please listen for the moving talker "\
            "and report back the words spoken by him in the correct order.\n\n"\
            "Press 'PLAY' when ready."
        ex2_str = "Here is another practice trial.\n\nPress 'PLAY' when ready."
        ex3_str = "Here is one more practice trial.\n\nPress 'PLAY' when ready."
        ex4_str = \
            "As in the first part, the motion of the moving talker may vary. "\
            "Here is an example with small target talker movement.\n\n"\
            "Press 'PLAY' when ready."
        ex5_str = "Here is another example.\n\nPress 'PLAY' when ready."
        ex6_str = "Here is final example.\n\nPress 'PLAY' when ready."
        warn_str = \
            "You may have difficulty identifying the moving talker in "\
            "some trials. Please make your best guess when that happens.\n\n\n"\
            "Press 'NEXT' to continue."
        final_str = "This concludes the tutorial.\n\nPress 'NEXT' to continue."
        return intro_str,\
               ex1_str,\
               ex2_str,\
               ex3_str,\
               ex4_str,\
               ex5_str,\
               ex6_str,\
               warn_str,\
               final_str


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


def do_detection_task(win, mouse, push_button, helper_text,
                      afc_interface, target_idx):
    # Wait for user response using the AFC interface
    trial_str = helper_text.text_stim.text + "\n\nWhich talker moved in this trial?"
    helper_text.set(text=trial_str, pos=(0, 0.63))
    helper_text.draw()
    afc_interface.draw()
    win.flip()

    # Wait for user response
    clicked = False
    while not clicked:
        # Detect "exit" keys
        exit_keys = event.getKeys(keyList=("q", "escape"))
        if exit_keys:
            exit_program(win)
        # Detect mouse click event
        if mouse.left_click_released():
            curr_mouse_pos = mouse.getPos()
            # Check if the mouse cursor is contained in one of the buttons
            for idx, button in enumerate(afc_interface.choice_buttons):
                if button.contains(curr_mouse_pos):
                    user_response = idx
                    clicked = True

    # Score subject responses
    subj_response_correct = user_response == target_idx

    # Set feedback text
    if subj_response_correct:
        feedback_txt = "CORRECT!\n\n\n\nPress 'NEXT' to continue."
    else:
        if target_idx == 0:
            ans_str = "LEFT"
        elif target_idx == 1:
            ans_str = "CENTER"
        else:
            ans_str = "RIGHT"
        feedback_txt = "INCORRECT!\n\nIt was the {:s} talker.\n\n\n\nPress "\
                       "'NEXT' to continue.".format(ans_str)

    # Display feedback and ready
    helper_text.set(text=feedback_txt, pos=(0, 0.4))
    helper_text.draw()
    push_button.set(text="NEXT")
    push_button.enable()
    push_button.draw()
    win.flip()
    wait_for_push_button(win, mouse, push_button)

    return user_response, subj_response_correct


def do_recall_task(win, mouse, push_button, helper_text,
                   submission_queue, answer_queue,
                   grid_interface, target_patterns):
    # Reset GUI elements
    answer_queue.reset()
    answer_queue.reset_borders()
    submission_queue.reset()
    submission_queue.reset_borders()
    helper_text.set(text=" ")
    push_button.reset_pressed()
    push_button.set(text="SUBMIT")
    win.flip()

    # Build the correct answer queue
    n_slots = len(target_patterns)
    for item in target_patterns:
        answer_queue.insert(item)

    # Wait for user response using the grid interface
    grid_logic(win, mouse, push_button, helper_text, n_slots,
               submission_queue, grid_interface)

    ### Scoring for answer in EXACT ORDER
    # Score subject responses
    subj_response_correct = \
        sum(answer_queue.queue_items[i] == submission_queue.queue_items[i]
            for i in range(0, n_slots))
    # # Compare the answer and submission one by one to toggle feedback color
    # for i in range(0, n_slots):
    #     if answer_queue.queue_items[i] == submission_queue.queue_items[i]:
    #         submission_queue.set_border_color(i, (0, 255, 0))
    #     else:
    #         submission_queue.set_border_color(i, (255, 0, 0))
    #     submission_queue.toggle_border(i)

    # Display feedback and ready
    feedback_str = "{:d}/5 correct!\n\n\nPress 'NEXT' to continue".format(subj_response_correct)
    helper_text.set(text=feedback_str, pos=(0, 0))
    helper_text.draw()
    push_button.set(text="NEXT")
    push_button.enable()
    push_button.draw()
    answer_queue.draw()
    submission_queue.draw()
    win.flip()
    wait_for_push_button(win, mouse, push_button)

    return submission_queue.queue_items, subj_response_correct


@push_button_wait_logic
def grid_logic(win, mouse, push_button, helper_text, n_slots,
               submission_queue, grid_interface):
    # NOTE: push_button MUST be third variable due to the decorator definition
    grid_interface.draw()
    submission_queue.draw()
    instruction_str = "Click on the words to respond."
    helper_text.set(text=instruction_str, pos=(0, 0.85))
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
