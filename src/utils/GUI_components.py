from abc import ABC, abstractmethod

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


class SupportText:
    def __init__(self, win, text="", color=(0, 0, 0), pos=(0, 0)):
        text_stim = \
            visual.TextStim(
                win,
                text=text,
                color=color,
                colorSpace="rgb255",
                pos=pos
            )
        self.text_stim = text_stim

    def set(self, text=None, color=None, pos=None):
        if text:
            self.text_stim.text = text
        if color:
            self.text_stim.color = color
        if pos:
            self.text_stim.pos = pos

    def draw(self):
        self.text_stim.draw()


class PushButton:
    def __init__(self, win, text="", color=(0, 0, 0), pos=(0, 0), size=(0.4, 0.2)):
        button_box = visual.Rect(
            win, width=size[0], height=size[1], pos=pos,
            lineColor=(150, 150, 150), lineColorSpace="rgb255",
            fillColor=(200, 200, 200), fillColorSpace="rgb255")
        button_txt = visual.TextStim(win, text=text,
                                     color=color, colorSpace="rgb255", pos=pos)
        self.win = win
        self.button_box = button_box
        self.button_txt = button_txt
        self.enabled = True
        self.pressed = False

    def set(self, text=None, color=None, pos=None, size=None):
        if text:
            self.button_txt.text = text
        if color:
            self.button_txt.color = color
        if pos:
            self.button_box.pos = pos
            self.button_txt.pos = pos
        if size:
            self.button_box.width, self.button_box.height = size

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

    def enable(self):
        """Enable push button"""
        self.enabled = True
        self.button_txt.color = (0, 0, 0)

    def disable(self):
        """Disable push button"""
        self.enabled = False
        self.button_txt.color = (150, 150, 150)

    def toggle_enable(self):
        """Toggle enable for push button"""
        if self.is_enabled():
            self.disable()
        else:
            self.enable()

    def is_enabled(self):
        """Check if the push button is enabled"""
        return self.enabled

    def reset_enable(self):
        """Reset enable for push button; same as enabling"""
        self.enable()


class Queue(ABC):
    def __init__(self, win, n_slots, gap, width, height, y_pos):
        borders = [visual.Rect( \
                     win,
                     width=width, height=height,
                     pos=(-0.25 + (i - 1)*(gap + width), y_pos),
                     lineColor=(127, 127, 127),
                     fillColor=(127, 127, 127),
                     lineColorSpace="rgb255",
                     fillColorSpace="rgb255",
                     opacity=0.)
                   for i in range(n_slots)]
        self.win = win
        self.borders = borders
        self.visual_elems = list(range(n_slots))
        self.queue_items = list(range(n_slots))
        self.curr_queue_pos = 0

    @abstractmethod
    def __len__(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def insert(self, x):
        pass

    def draw(self):
        for border in self.borders:
            border.draw()
        for elem in self.visual_elems:
            elem.draw()

    def toggle_border(self, i):
        if self.borders[i].opacity == 0:
            self.borders[i].opacity = 1
        else:
            self.borders[i].opacity = 0

    def set_border_color(self, i, color):
        self.borders[i].lineColor = color

    def reset_borders(self):
        for border in self.borders:
            border.opacity = 0
            border.lineColor = (0, 0, 0)


class WordQueue(Queue):
    def __init__(self, win, n_slots, gap, width, height, y_pos):
        super().__init__(win, n_slots, gap, width, height, y_pos)
        self.visual_elems = [
            visual.TextStim( \
                win, height=0.8*height, text="",
                pos=(-0.25 + (i - 1)*(gap + width), y_pos),
                color=(0, 0, 0), colorSpace="rgb255")
            for i in range(n_slots)]

    def __len__(self):
        return sum(elem.text is not "" for elem in self.visual_elems)

    def reset(self):
        self.curr_queue_pos = 0
        self.queue_items = []
        for elem in self.visual_elems:
            elem.text = ""

    def insert(self, text_str):
        if len(self) < len(self.visual_elems):
            curr_queue_pos = self.curr_queue_pos
            self.visual_elems[curr_queue_pos].text = text_str
            self.queue_items.append(text_str)
            self.curr_queue_pos += 1


class TonePatternQueue(Queue):
    def __init__(self, win, n_slots, gap, width, height, y_pos):
        super().__init__(win, n_slots, gap, width, height, y_pos)
        self.visual_elems = [
            visual.ImageStim( \
                win, image=None,
                pos=(-n_slots*width/2 + (i - 1)*(gap + width),   y_pos) )
            for i in range(n_slots)]

    def __len__(self):
        return sum(elem.image is not None for elem in self.visual_elems)

    def reset(self):
        self.curr_queue_pos = 0
        self.queue_items = []
        for elem in self.visual_elems:
            elem.image = None

    def insert(self, pattern_num):
        if len(self) < len(self.visual_elems):
            curr_queue_pos = self.curr_queue_pos
            self.visual_elems[curr_queue_pos].image = \
                PATTERN_SMALL_IMG_PATHS[pattern_num]
            self.queue_items.append(PATTERN_TYPES[pattern_num])
            self.curr_queue_pos += 1


class AFCInterface:
    def __init__(self, win):
        choice_buttons = [PushButton(win, text="LEFT",   pos=(-0.5, -0.7)),
                          PushButton(win, text="CENTER", pos=(   0, -0.7)),
                          PushButton(win, text="RIGHT",  pos=( 0.5, -0.7))]
        self.win = win
        self.choice_buttons = choice_buttons

    def draw(self):
        for button in self.choice_buttons:
            button.draw()


class WordGridInterface:
    def __init__(self, win, column_len, words_in_grid,
                 x_offset, y_offset,
                 word_box_width, word_box_height):
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
                height=0.08,
                pos=( (i//column_len)*word_box_width  + x_offset,
                     -(i %column_len)*word_box_height + y_offset) )
            for i, word in enumerate(words_in_grid)
        ]
        self.win = win
        self.word_boxes = word_boxes
        self.word_labels = word_labels

    def draw(self):
        for box in self.word_boxes:
            box.draw()
        for word in self.word_labels:
            word.draw()
