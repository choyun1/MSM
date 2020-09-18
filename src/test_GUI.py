import os

from psychopy import core, visual, event

# Project imports
from utils.init_constants import *
from utils.stim_tools import *
from utils.GUI_components import *
from utils.GUI_routines import *

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

# Set ready screen
helper_text.set_text("Speech on speech staircase.\n\nPress NEXT when ready.")
helper_text.draw()
push_button.set_text("NEXT")
push_button.draw()
win.flip()

wait_for_push_button(win, push_button, mouse)

talkers, \
target_sentence, masker_sentence, \
target_sentence_items, masker_sentence_items = make_sentence()

do_word_recall_task(win, push_button, mouse, helper_text,
                    word_submission_queue, word_answer_queue,
                    word_grid_interface,
                    target_sentence_items)

exit_program(win)
