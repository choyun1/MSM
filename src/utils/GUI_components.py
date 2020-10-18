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


class TonePatternQueue:
    def __init__(self, win, n_slots, y_pos):
        gap = 2
        width = 5
        borders = [
            visual.Rect(
                win,
                width=5.5,
                height=2,
                lineColor=(0, 255, 0),
                lineColorSpace="rgb255",
                fillColor=(0, 255, 0),
                fillColorSpace="rgb255",
                opacity=0.,
                pos=( -n_slots*width/2 + i*(gap + width), y_pos )
            )
            for i in range(n_slots)
        ]
        imgs = [
            visual.ImageStim(
                win,
                image=None,
                pos=( -n_slots*width/2 + i*(gap + width), y_pos )
            )
            for i in range(n_slots)
        ]

        self.win = win
        self.borders = borders
        self.imgs = imgs
        self.patterns = []
        self.curr_queue_pos = 0

    def insert(self, pattern_num):
        """inserts a tone pattern always at the end"""
        if len(self) < len(self.imgs):
            curr_queue_pos = self.curr_queue_pos
            self.imgs[curr_queue_pos].image = PATTERN_SMALL_IMG_PATHS[pattern_num]
            self.patterns.append(PATTERN_TYPES[pattern_num])
            self.curr_queue_pos += 1

    def pop(self, position):
        ### TODO: There's a bug in the popping capability!
        """pops a tone pattern from any position"""
        for idx in range(position, len(self.imgs) - 1):
            self.imgs[idx].image = self.imgs[idx + 1].image
        self.imgs[-1].image = None
        self.patterns.pop(position)
        self.curr_queue_pos = max(self.curr_queue_pos - 1, 0)

    def reset(self):
        self.curr_queue_pos = 0
        self.patterns = []
        for img in self.imgs:
            img.image = None

    def toggle_border(self, i):
        if self.borders[i].opacity == 0:
            self.borders[i].opacity = 1
        elif self.tone_pattern_borders[i].opacity == 1:
            self.tone_pattern_borders[i].opacity = 0

    def set_border_color(self, i, color):
        self.borders[i].color = color

    def reset_borders(self):
        for border in self.borders:
            border.opacity = 0
            border.color = (0, 0, 0)

    def draw(self):
        for border in self.borders:
            border.draw()
        for img in self.imgs:
            img.draw()

    def __len__(self):
        return sum(img.image is not None for img in self.imgs)


# class TonePatternInterface:
#     def __init__(self, win, y_offset=1):
#         tone_pattern_borders = [
#             visual.Rect(
#                 win,
#                 width=11.1,
#                 height=4.1,
#                 lineColor=(0, 0, 0),
#                 lineColorSpace="rgb255",
#                 fillColor=(0, 0, 0),
#                 fillColorSpace="rgb255",
#                 opacity=0.,
#                 pos=(-12 + 12*(i%3), -6*(i//3) + y_offset))
#             for i in range(len(PATTERN_TYPES))
#         ]
#         tone_pattern_grid = [
#             visual.ImageStim(
#                 win,
#                 image=PATTERN_IMG_PATHS[i],
#                 pos=(-12 + 12*(i%3), -6*(i//3) + y_offset))
#             for i in range(len(PATTERN_TYPES))
#         ]
#         tone_pattern_labels = [
#             visual.TextStim(
#                 win,
#                 text=pattern_name,
#                 color=(0, 0, 0),
#                 colorSpace="rgb255",
#                 height=0.8,
#                 pos=(-12 + 12*(i%3), -2.5 - 6*(i//3) + y_offset))
#             for i, pattern_name in enumerate(PATTERN_TYPES)
#         ]
#         self.win = win
#         self.tone_pattern_borders = tone_pattern_borders
#         self.tone_pattern_grid = tone_pattern_grid
#         self.tone_pattern_labels = tone_pattern_labels
#         self.highlighted_patterns = 0
#         self.highlighted_pattern_idxs = set()
#
#     def toggle_border(self, i):
#         if self.tone_pattern_borders[i].opacity == 0:
#             self.tone_pattern_borders[i].opacity = 1
#             self.highlighted_patterns += 1
#             self.highlighted_pattern_idxs.add(i)
#         elif self.tone_pattern_borders[i].opacity == 1:
#             self.tone_pattern_borders[i].opacity = 0
#             self.highlighted_patterns -= 1
#             self.highlighted_pattern_idxs.remove(i)
#
#     def set_border_color(self, i, color):
#         self.tone_pattern_borders[i].color = color
#
#     def count_highlighted(self):
#         return self.highlighted_patterns
#
#     def highlighted_idxs(self):
#         return sorted(list(self.highlighted_pattern_idxs))
#
#     def reset_borders(self):
#         for border in self.tone_pattern_borders:
#             border.opacity = 0
#             border.color = (0, 0, 0)
#         self.highlighted_patterns = 0
#         self.highlighted_pattern_idxs = set()
#
#     def draw(self):
#         for tone_pattern_border in self.tone_pattern_borders:
#             tone_pattern_border.draw()
#         for tone_pattern_img in self.tone_pattern_grid:
#             tone_pattern_img.draw()
#         for tone_pattern_label in self.tone_pattern_labels:
#             tone_pattern_label.draw()


class WordQueue:
    def __init__(self, win, n_slots, y_pos, gap, width, height):
        boxes = [
            visual.Rect(
                win,
                width=width,
                height=height,
                lineColor=(0, 255, 0),
                lineColorSpace="rgb255",
                fillColor=(0, 255, 0),
                fillColorSpace="rgb255",
                opacity=0.,
                pos=( -n_slots*width/2 + (i - 1)*(gap + width), y_pos )
            )
            for i in range(n_slots)
        ]
        text_labels = [
            visual.TextStim(
                win,
                text="",
                color=(0, 0, 0),
                colorSpace="rgb255",
                height=0.8*height,
                pos=( -n_slots*width/2 + (i - 1)*(gap + width), y_pos )
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


# class TonePatternInterface:
#     def __init__(self, win, y_offset=1):
#         tone_pattern_borders = [
#             visual.Rect(
#                 win,
#                 width=11.1,
#                 height=4.1,
#                 lineColor=(0, 0, 0),
#                 lineColorSpace="rgb255",
#                 fillColor=(0, 0, 0),
#                 fillColorSpace="rgb255",
#                 opacity=0.,
#                 pos=(-12 + 12*(i%3), -6*(i//3) + y_offset))
#             for i in range(len(PATTERN_TYPES))
#         ]
#         tone_pattern_grid = [
#             visual.ImageStim(
#                 win,
#                 image=PATTERN_IMG_PATHS[i],
#                 pos=(-12 + 12*(i%3), -6*(i//3) + y_offset))
#             for i in range(len(PATTERN_TYPES))
#         ]
#         tone_pattern_labels = [
#             visual.TextStim(
#                 win,
#                 text=pattern_name,
#                 color=(0, 0, 0),
#                 colorSpace="rgb255",
#                 height=0.8,
#                 pos=(-12 + 12*(i%3), -2.5 - 6*(i//3) + y_offset))
#             for i, pattern_name in enumerate(PATTERN_TYPES)
#         ]
#         self.win = win
#         self.tone_pattern_borders = tone_pattern_borders
#         self.tone_pattern_grid = tone_pattern_grid
#         self.tone_pattern_labels = tone_pattern_labels
#         self.highlighted_patterns = 0
#         self.highlighted_pattern_idxs = set()
#
#     def toggle_border(self, i):
#         if self.tone_pattern_borders[i].opacity == 0:
#             self.tone_pattern_borders[i].opacity = 1
#             self.highlighted_patterns += 1
#             self.highlighted_pattern_idxs.add(i)
#         elif self.tone_pattern_borders[i].opacity == 1:
#             self.tone_pattern_borders[i].opacity = 0
#             self.highlighted_patterns -= 1
#             self.highlighted_pattern_idxs.remove(i)
#
#     def set_border_color(self, i, color):
#         self.tone_pattern_borders[i].color = color
#
#     def count_highlighted(self):
#         return self.highlighted_patterns
#
#     def highlighted_idxs(self):
#         return sorted(list(self.highlighted_pattern_idxs))
#
#     def reset_borders(self):
#         for border in self.tone_pattern_borders:
#             border.opacity = 0
#             border.color = (0, 0, 0)
#         self.highlighted_patterns = 0
#         self.highlighted_pattern_idxs = set()
#
#     def draw(self):
#         for tone_pattern_border in self.tone_pattern_borders:
#             tone_pattern_border.draw()
#         for tone_pattern_img in self.tone_pattern_grid:
#             tone_pattern_img.draw()
#         for tone_pattern_label in self.tone_pattern_labels:
#             tone_pattern_label.draw()


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
