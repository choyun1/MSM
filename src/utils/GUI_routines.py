from psychopy import core, event



def exit_program(win):
    win.close()
    core.quit()


def make_task_instruction_str():
    task_str = """
This is the {:s} task. Please attend to the tone patterns in your {:s} ear, and
identify the last {:d} patterns embedded in the masker tones. The first pattern
is always the CONSTANT pattern.

Press 'NEXT' when ready.
    """.format(" ".join(task_type.split("_")).upper(), tone_pattern_ear, n_patterns - 1)
    return task_str


def do_word_recall_task(win, mouse,
                        word_submission_queue, word_answer_queue,
                        word_grid_interface, helper_text, push_button,
                        N_PATTERNS, target_sentence):
    # Reset GUI elements
    word_answer_queue.reset()
    word_submission_queue.reset()
    word_submission_queue.reset_borders()
    helper_text.set_text("")
    helper_text.set_color((0, 0, 0))
    push_button.reset_pressed()
    push_button.set_text("SUBMIT")
    win.flip()

    # Always insert constant pattern into the submission queue
    word_submission_queue.insert("SUE")

    # Check for user input
    while not push_button.is_pressed():
        mouse.clickReset()

        # Set helper text
        helper_text.set_pos((0, 11))
        helper_text.set_text("Select the words in the order they were played.")

        # Check for number of selected tone patterns in the submission box
        if len(word_submission_queue) == N_PATTERNS:
            push_button.enable()
        else:
            push_button.disable()

        # Flip frame
        word_grid_interface.draw()
        word_submission_queue.draw()
        helper_text.draw()
        push_button.draw()
        win.flip()

        # Check for exit keyboard input
        quit_program = event.getKeys(keyList=EXIT_KEYS)
        if quit_program:
            win.close()
            core.quit()

        # Get mouse clicks
        if mouse.left_click_released():
            curr_mouse_pos = mouse.getPos()
            # Check if the mouse cursor is contained in one of the grid choices
            for idx, box in enumerate(word_grid_interface.word_boxes):
                if box.contains(curr_mouse_pos):
                    word_submission_queue.insert(word_grid_interface.word_labels[idx].text)

            # Check if the mouse cursor is contained in push button
            if push_button.contains(curr_mouse_pos) and push_button.is_enabled():
                push_button.set_pressed()

    # Build the correct answer queue
    target_name, target_verb, target_adj, target_noun = target_sentence
    word_answer_queue.insert(target_name.upper())
    word_answer_queue.insert(target_verb.upper())
    word_answer_queue.insert(target_adj.upper())
    word_answer_queue.insert(target_noun.upper())

    # Compare the answer and submission one by one to see which is correct
    for i in range(1, len(word_submission_queue)):
        if word_answer_queue.texts[i] == word_submission_queue.texts[i]:
            word_submission_queue.set_border_color(i, (0, 255, 0))
        else:
            word_submission_queue.set_border_color(i, (255, 0, 0))
        word_submission_queue.toggle_border(i)

    # Score subject responses, EXCLUDING the first constant pattern
    subj_response = word_submission_queue.texts
    subj_response_correct = \
        sum(word_answer_queue.texts[i] == subj_response[i]
            for i in range(1, len(subj_response)))

    # Display answer and feedback
    helper_text.set_text("CORRECT ANSWER")
    helper_text.set_pos((-18, 5))
    word_answer_queue.draw()
    word_submission_queue.draw()
    helper_text.draw()
    win.flip()

    core.wait(0.5)

    push_button.reset_pressed()
    push_button.set_text("NEXT")
    push_button.enable()

    # Wait for subject to press "NEXT"
    while not push_button.is_pressed():
        mouse.clickReset()

        # Flip frame
        word_answer_queue.draw()
        word_submission_queue.draw()
        helper_text.draw()
        push_button.draw()
        win.flip()

        # Check for exit keyboard input
        quit_program = event.getKeys(keyList=EXIT_KEYS)
        if quit_program:
            win.close()
            core.quit()

        # Get mouse clicks
        if mouse.left_click_released():
            curr_mouse_pos = mouse.getPos()

            # Check if the mouse cursor is contained in push button
            if push_button.contains(curr_mouse_pos) and push_button.is_enabled():
                push_button.set_pressed()

    # Reset GUI elements
    word_answer_queue.reset()
    word_submission_queue.reset()
    word_submission_queue.reset_borders()
    helper_text.set_text("")
    helper_text.set_color((0, 0, 0))
    push_button.reset_pressed()
    push_button.set_text("SUBMIT")

    return subj_response, subj_response_correct
