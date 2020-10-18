from psychopy import core, event


def exit_program(win):
    win.close()
    core.quit()


def make_task_instruction_str():
    task_str = """
This is a speech intelligibility task. You will hear two male talkers moving
between your ears. One of the talkers will begin their sentence with the name
'Sue'. Attend to this talker and respond with the spoken sentence.

Press 'NEXT' when ready.
    """
    return task_str


def push_button_wait_logic(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        win = args[0]
        push_button = args[1]
        mouse = args[2]
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
def wait_for_push_button(win, push_button, mouse):
    if mouse.left_click_released():
        curr_mouse_pos = mouse.getPos()
        # Check if the mouse cursor is contained in push button
        if push_button.contains(curr_mouse_pos):
            push_button.set_pressed()


@push_button_wait_logic
def grid_logic(win, push_button, mouse, n_slots, helper_text,
               word_grid_interface, word_submission_queue):
    # Flip frame
    word_grid_interface.draw()
    word_submission_queue.draw()
    helper_text.set_pos((0, 11))
    helper_text.set_text("Select the words in the order they were spoken.")
    helper_text.draw()
    push_button.draw()
    win.flip()

    # Check for number of selected tone patterns in the submission box
    if len(word_submission_queue) == n_slots:
        push_button.enable()
    else:
        push_button.disable()

    # Get mouse clicks
    if mouse.left_click_released():
        curr_mouse_pos = mouse.getPos()
        # Check if the mouse cursor is contained in one of the grid choices
        for idx, box in enumerate(word_grid_interface.word_boxes):
            if box.contains(curr_mouse_pos):
                word_submission_queue.insert(
                    word_grid_interface.word_labels[idx].text)
        # Check if the mouse cursor is contained in push button
        if push_button.contains(curr_mouse_pos) and push_button.is_enabled():
            push_button.set_pressed()


def do_word_recall_task(win, push_button, mouse, helper_text,
                        word_submission_queue, word_answer_queue,
                        word_grid_interface,
                        target_sentence_items):
    # Reset GUI elements
    word_answer_queue.reset()
    word_submission_queue.reset()
    word_submission_queue.reset_borders()
    helper_text.set_text("")
    helper_text.set_color((0, 0, 0))
    push_button.reset_pressed()
    push_button.set_text("SUBMIT")
    win.flip()

    # Build the correct answer queue
    for item in target_sentence_items:
        word_answer_queue.insert(item.upper())
    # Always insert constant pattern into the submission queue
    word_submission_queue.insert("SUE")

    # Get user response
    n_slots = len(target_sentence_items)
    grid_logic(win, push_button, mouse, n_slots, helper_text,
               word_grid_interface, word_submission_queue)

    # Score responses EXCLUDING the first constant pattern
    subj_response = word_submission_queue.texts
    subj_response_correct = \
        sum( word_answer_queue.texts[i] == subj_response[i]
             for i in range(1, len(subj_response)) )

    # Toggle color indicating correct/incorrect
    for i in range(1, len(word_submission_queue)):
        if word_answer_queue.texts[i] == word_submission_queue.texts[i]:
            word_submission_queue.set_border_color(i, (0, 255, 0))
        else:
            word_submission_queue.set_border_color(i, (255, 0, 0))
        word_submission_queue.toggle_border(i)

    # Display answer and feedback
    word_answer_queue.draw()
    word_submission_queue.draw()
    win.flip()
    core.wait(0.5)

    # Re-draw elements for waiting
    helper_text.set_text("Press 'NEXT' to continue")
    helper_text.draw()
    push_button.set_text("NEXT")
    push_button.enable()
    push_button.draw()
    word_answer_queue.draw()
    word_submission_queue.draw()
    win.flip()
    wait_for_push_button(win, push_button, mouse)

    return subj_response, subj_response_correct




#####
#####
#####
#####
#####


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
#
#
# def do_word_recall_task(win, mouse,
#                         word_submission_queue, word_answer_queue,
#                         word_grid_interface, helper_text, push_button,
#                         N_PATTERNS, target_sentence):
#     # Reset GUI elements
#     word_answer_queue.reset()
#     word_submission_queue.reset()
#     word_submission_queue.reset_borders()
#     helper_text.set_text("")
#     helper_text.set_color((0, 0, 0))
#     push_button.reset_pressed()
#     push_button.set_text("SUBMIT")
#     win.flip()
#
#     # Always insert constant pattern into the submission queue
#     word_submission_queue.insert("SUE")
#
#     # Check for user input
#     while not push_button.is_pressed():
#         mouse.clickReset()
#
#         # Set helper text
#         helper_text.set_pos((0, 11))
#         helper_text.set_text("Select the words in the order they were played.")
#
#         # Check for number of selected tone patterns in the submission box
#         if len(word_submission_queue) == N_PATTERNS:
#             push_button.enable()
#         else:
#             push_button.disable()
#
#         # Flip frame
#         word_grid_interface.draw()
#         word_submission_queue.draw()
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
#             # Check if the mouse cursor is contained in one of the grid choices
#             for idx, box in enumerate(word_grid_interface.word_boxes):
#                 if box.contains(curr_mouse_pos):
#                     word_submission_queue.insert(word_grid_interface.word_labels[idx].text)
#
#             # Check if the mouse cursor is contained in push button
#             if push_button.contains(curr_mouse_pos) and push_button.is_enabled():
#                 push_button.set_pressed()
#
#     # Build the correct answer queue
#     target_name, target_verb, target_adj, target_noun = target_sentence
#     word_answer_queue.insert(target_name.upper())
#     word_answer_queue.insert(target_verb.upper())
#     word_answer_queue.insert(target_adj.upper())
#     word_answer_queue.insert(target_noun.upper())
#
#     # Compare the answer and submission one by one to see which is correct
#     for i in range(1, len(word_submission_queue)):
#         if word_answer_queue.texts[i] == word_submission_queue.texts[i]:
#             word_submission_queue.set_border_color(i, (0, 255, 0))
#         else:
#             word_submission_queue.set_border_color(i, (255, 0, 0))
#         word_submission_queue.toggle_border(i)
#
#     # Score subject responses, EXCLUDING the first constant pattern
#     subj_response = word_submission_queue.texts
#     subj_response_correct = \
#         sum(word_answer_queue.texts[i] == subj_response[i]
#             for i in range(1, len(subj_response)))
#
#     # Display answer and feedback
#     helper_text.set_text("CORRECT ANSWER")
#     helper_text.set_pos((-18, 5))
#     word_answer_queue.draw()
#     word_submission_queue.draw()
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
#         word_answer_queue.draw()
#         word_submission_queue.draw()
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
#     word_answer_queue.reset()
#     word_submission_queue.reset()
#     word_submission_queue.reset_borders()
#     helper_text.set_text("")
#     helper_text.set_color((0, 0, 0))
#     push_button.reset_pressed()
#     push_button.set_text("SUBMIT")
#
#     return subj_response, subj_response_correct
