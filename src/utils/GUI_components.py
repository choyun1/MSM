from psychopy import event, visual


class CustomMouse(event.Mouse):
    """Class that extends PsychoPy Mouse class to detect left click releases."""
    def __init__(self, *arg, **kwarg):
        super(CustomMouse, self).__init__(*arg, **kwarg)
        self.prev_left_click_status = 0

    def left_click_released(self):
        curr_left_click_status = self.getPressed()[0]
        if self.prev_left_click_status == 1 and curr_left_click_status == 0:
            self.prev_left_click_status = curr_left_click_status
            return True
        else:
            self.prev_left_click_status = curr_left_click_status
            return False


class WordQueue:
    def __init__(self, win, n_slots, y_pos, width):
        gap = 1
        boxes = [
            visual.Rect(
                win,
                width=width,
                height=1,
                lineColor=(0, 255, 0),
                lineColorSpace="rgb255",
                fillColor=(0, 255, 0),
                fillColorSpace="rgb255",
                opacity=0.,
                pos=( -n_slots*width/2 + i*(gap + width), y_pos )
            )
            for i in range(n_slots)
        ]
        text_labels = [
            visual.TextStim(
                win,
                text="",
                color=(0, 0, 0),
                colorSpace="rgb255",
                height=0.8,
                pos=( -n_slots*width/2 + i*(gap + width), y_pos )
            )
            for i in range(n_slots)
        ]
        self.win = win
        self.boxes = boxes
        self.text_labels = text_labels
        self.texts = []
        self.curr_queue_pos = 0


    def insert(self, text_str):
        """queue a word at the end"""
        if len(self) < len(self.text_labels):
            curr_queue_pos = self.curr_queue_pos
            self.text_labels[curr_queue_pos].text = text_str
            self.texts.append(text_str)
            self.curr_queue_pos += 1

    def pop(self, position):
        raise NotImplementedError

    def reset(self):
        self.curr_queue_pos = 0
        self.texts = []
        for text_label in self.text_labels:
            text_label.text = ""

    def toggle_border(self, i):
        if self.boxes[i].opacity == 0:
            self.boxes[i].opacity = 1
        elif self.boxes[i].opacity == 1:
            self.boxes[i].opacity = 0

    def set_border_color(self, i, color):
        self.boxes[i].color = color

    def reset_borders(self):
        for box in self.boxes:
            box.opacity = 0
            box.color = (0, 0, 0)

    def draw(self):
        for box in self.boxes:
            box.draw()
        for text_label in self.text_labels:
            text_label.draw()

    def __len__(self):
        return sum(text_elem.text is not "" for text_elem in self.text_labels)


class WordGridInterface:
    def __init__(self, win, column_len, words_in_grid,
                 x_offset=-5, y_offset=4,
                 word_box_width=4, word_box_height=1.5):
        word_boxes = [
            visual.Rect(
                win,
                width=word_box_width,
                height=word_box_height,
                lineColor=(0, 0, 0),
                lineColorSpace="rgb255",
                fillColor=(0, 0, 0),
                fillColorSpace="rgb255",
                opacity=0.,
                pos=( (i//column_len)*word_box_width  + x_offset,
                     -(i %column_len)*word_box_height + y_offset) )
            for i in range(len(words_in_grid))
            ]
        word_labels = [
            visual.TextStim(
                win,
                text=word.upper(),
                color=(0, 0, 0),
                colorSpace="rgb255",
                height=0.8,
                pos=( (i//column_len)*word_box_width  + x_offset,
                     -(i %column_len)*word_box_height + y_offset) )
            for i, word in enumerate(words_in_grid)
        ]
        self.win = win
        self.word_boxes = word_boxes
        self.word_labels = word_labels

    def toggle_position(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def draw(self):
        for box in self.word_boxes:
            box.draw()
        for word in self.word_labels:
            word.draw()


class PushButton:
    def __init__(self, win, pos=(0, -10)):
        button_box = visual.Rect(
            win,
            width=5,
            height=2,
            lineColor=(180, 180, 180),
            lineColorSpace="rgb255",
            fillColor=(200, 200, 200),
            fillColorSpace="rgb255",
            pos=pos)
        button_txt = visual.TextStim(
            win,
            text="",
            color=(0, 0, 0),
            colorSpace="rgb255",
            pos=pos)
        self.win = win
        self.button_box = button_box
        self.button_txt = button_txt
        self.enabled = True
        self.pressed = False

    def contains(self, pos):
        """Wrapper for contains method"""
        return self.button_box.contains(pos)

    def draw(self):
        """Wrapper for draw method"""
        self.button_box.draw()
        self.button_txt.draw()

    def set_pressed(self):
        """Press button"""
        self.pressed = True

    def is_pressed(self):
        """Returns current button toggle status"""
        return self.pressed

    def reset_pressed(self):
        """Resets button press status to unpressed"""
        self.pressed = False

    def is_enabled(self):
        """Check if the push button is enabled"""
        return self.enabled

    def enable(self):
        """Enable push button"""
        self.enabled = True
        curr_text = self.button_txt.text
        self.button_txt.color = (0, 0, 0)

    def disable(self):
        """Disable push button"""
        self.enabled = False
        curr_text = self.button_txt.text
        self.button_txt.color = (150, 150, 150)

    def toggle_enable(self):
        """Toggle enable for push button"""
        if self.is_enabled():
            self.disable()
        else:
            self.enable()

    def reset_enable(self):
        """Reset enable for push button; same as enabling"""
        self.enable()

    def set_text(self, text_str):
        """Set the text string for the box"""
        self.button_txt.text = text_str

    def reset_text(self):
        """Reset the text string for the box"""
        self.button_txt.text = ""


class SupportingText:
    def __init__(self, win):
        text_stim = \
            visual.TextStim(
                win,
                text="",
                color=(0, 0, 0),
                colorSpace="rgb255",
                pos=(0, 0)
            )
        self.text_stim = text_stim

    def set_text(self, text):
        self.text_stim.text = text

    def set_pos(self, pos):
        self.text_stim.pos = pos

    def set_color(self, color):
        self.text_stim.color = color

    def draw(self):
        self.text_stim.draw()
