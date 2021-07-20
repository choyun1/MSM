from psychopy import core, event


def exit_program(win):
    win.close()
    core.quit()


def make_tutorial_strs():
    intro_str = \
        "Thank you for participating in this experiment.\n\nWe will ask you " \
        "to either identify the moving sound or report back the words spoken " \
        "by the moving talker. We will begin by presenting some examples."
    ex1_str = \
        "Here is an example of a single NOISE source moving back and forth " \
        "around the CENTER. Please listen carefully.\n\n" \
        "Press 'PLAY' when ready."
    ex2_str = \
        "And this is an example of a single TALKER moving back and forth " \
        "around the CENTER. Please listen carefully.\n\n" \
        "Press 'PLAY' when ready."
    ex3_str = \
        "In the actual experiment, you will be presented with three " \
        "sound sources located LEFT, CENTER, and RIGHT. You must " \
        "identify the one sound that is moving back and forth.\n\n" \
        "Here is an example with three TALKERS.\n\nPress 'PLAY' when ready."
    ex4_str = \
        "Here is an example with three NOISE sources. Please identify the " \
        "MOVING sound.\n\nPress 'PLAY' when ready."
    ex5_str = \
        "In some tasks, we will ask you to report back the words spoken by " \
        "the moving talker. Here is an example.\n\nPress 'PLAY' when ready."
    ex6_str = \
        "Here is a final example with three talkers. Please report back the " \
        "words spoken by the MOVING talker.\n\nPress 'PLAY' when ready."
    final_str = \
        "It may be difficult to identify the moving talker in some trials. " \
        "Please make your best guess when that happens. Next, we will do " \
        "some practice before moving on to the experimental blocks.\n\n" \
        "Press 'NEXT' to continue."
    return intro_str, ex1_str, ex2_str, ex3_str, \
        ex4_str, ex5_str, ex6_str, final_str


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
    trial_str = helper_text.text_stim.text + \
        "\n\nWhich talker moved in this trial?"
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
    subj_response_correct = int(user_response == target_idx)

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

    # Score subject responses in EXACT ORDER
    subj_response_correct = \
        sum(answer_queue.queue_items[i] == submission_queue.queue_items[i]
            for i in range(0, n_slots))

    # Display feedback and ready
    feedback_str = "{:d}/5 correct!\n\n\nPress 'NEXT' to continue".format(
        subj_response_correct)
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
