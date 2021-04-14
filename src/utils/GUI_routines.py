from psychopy import core, event


def make_intro():
    intro_str =\
        "Thank you for participating in this experiment.\n\n"\
        "You will be asked to pay attention to a male speaker who sounds as "\
        "though he is MOVING and report back the sentence he says.\n\n\n"\
        "Click 'NEXT' to continue."
    return intro_str


def ex1():
    ex1_str = "Here is an example of a moving talker. Please listen carefully."
    return ex1_str


def ex2():
    ex2_str = "Here is another example of a moving talker."
    return ex2_str


def ex3():
    ex3_str = \
        "In the actual experiment, you will have to listen for the moving "\
        "talker among one or more other stationary talkers in the audio.\n\n"\
        "This is an example with 2 talkers. Press 'PLAY' when ready.\n\n\n"
    return ex3_str


def ex4():
    ex4_str = \
        "Notice that the talkers should sound as though they are coming from "\
        "different locations.\n\n"\
        "Here is another example. Press 'PLAY' when ready.\n\n\n"
    return ex4_str


def ex5():
    ex5_str = \
        "Here is another example, this time with more talkers.\n\n\n"
    return ex5_str


def ex6():
    ex6_str = \
        "The degree of motion may change from trial to trial. Here is an "\
        "example of a talker with small amount of movement.\n\n\n"
    return ex6_str


def ex7():
    ex7_str = \
        "Here is a final example with more talkers.\n\n\n"
    return ex7_str


def warning():
    warn_str = \
        "In some cases, the motion of the moving talker may be so slight "\
        "as to be unnoticeable. When that happens, you will have to guess "\
        "the identity of the moving talker and report back his words.\n\n"\
        "It may take some time and practice throughout the experiment to "\
        "become proficient at this task.\n\n\n"\
        "Click 'NEXT' to continue."
    return warn_str


def make_task_instruction():
    task_instr_str =\
        "Now we will begin the experiment. Before each block, you will be "\
        "informed about the number of talkers in the audio. The amount of "\
        "motion in the moving talker will vary from trial to trial.\n\n\n"\
        "Click 'START' when you are ready to begin."
    return task_instr_str


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
    trial_str = "Report back the words spoken by the target talker in the EXACT "\
                "ORDER by clicking on the words in the grid."
    # trial_str = "Report back the words spoken by the target talker in ANY ORDER "\
    #             "by clicking on the words in the grid."
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


def do_recall_task(win, mouse, helper_text, push_button,
                   submission_queue, answer_queue,
                   grid_interface, target_patterns):
    # Reset GUI elements
    answer_queue.reset()
    answer_queue.reset_borders()
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

    # Wait for user response using the grid interface
    grid_logic(win, mouse, push_button, helper_text, n_slots, submission_queue,
               grid_interface)

    ### Scoring for answer in EXACT ORDER
    # Score subject responses
    subj_response_correct = \
        sum(answer_queue.queue_items[i] == submission_queue.queue_items[i]
            for i in range(0, n_slots))
    # Compare the answer and submission one by one to toggle feedback color
    # for i in range(0, n_slots):
    #     if answer_queue.queue_items[i] == submission_queue.queue_items[i]:
    #         submission_queue.set_border_color(i, (0, 0, 255))
    #     else:
    #         submission_queue.set_border_color(i, (255, 0, 0))
    #     submission_queue.toggle_border(i)

    # Display feedback and ready
    helper_text.set(text="CORRECT ANSWERS\n\n\nPress 'NEXT' to continue", pos=(0, -2))
    helper_text.draw()
    push_button.set_text("NEXT")
    push_button.enable()
    push_button.draw()
    answer_queue.draw()
    submission_queue.draw()
    win.flip()
    wait_for_push_button(win, mouse, push_button)

    return submission_queue.queue_items, subj_response_correct
