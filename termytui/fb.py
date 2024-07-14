from .termy.termy import colorize, move_and_print, clear_screen, coloropt
import random
import time
import sys


fps_history_max = 120
cells_history_max = 120


class BufferedDisplay():
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.display_frame = dict()
        self.buffer_frame = dict()
        self.frame_delay = 0.0065
        self.render_enabled = True
        self.debug_enabled = False
        self.frame_count = 0
        self.last_frame_time = self.frame_delay
        self.fps_history = list()
        self.cells_history = list()
        self.chars_history = list()
        
        for i in range(0, width + 10):
            for j in range(0, height + 10):
                self.display_frame[(i, j)] = ' '
                self.buffer_frame[(i, j)] = ' '
                move_and_print(i + 1, j + 1, ' ')

        #self.render_thread = threading.Thread(target=self.render_thread_runner)
        #self.render_thread.start()

    def render_thread_runner(self):
        while self.render_enabled:
            frame_start = time.time()
            self.update_display()
            time.sleep(self.frame_delay)
            frame_end = time.time()
            self.fps_history.append(1 / self.last_frame_time)
            self.last_frame_time = frame_end - frame_start
            if len(self.fps_history) > fps_history_max:
                self.fps_history = self.fps_history[-1 * fps_history_max:]


    def blank_buffer(self):
        for i in range(0, self.width):
            for j in range(0, self.height):
                self.buffer_frame[(i, j)] = ' '
        
    def update_display(self, full_redraw=False):
        chars_this_frame = 0
        self.frame_count += 1
        # build dict of cells that need to change
        to_change = list()
        if not full_redraw:
            for j in range(0, self.height):
                for i in range(0, self.width):
                    if self.display_frame[(i, j)] != self.buffer_frame[(i, j)]:
                        to_change.append((i, j))
        else:
            for i in range(0, self.width):
                for j in range(0, self.height):
                    to_change.append((i, j))
        # iterate over that and make updates
        for c in to_change:
            try:
                self.display_frame[c] = self.buffer_frame[c]
                out_str = f'\033[{c[1]};{c[0]}H{self.display_frame[c]}'
                sys.stdout.write(out_str)
                chars_this_frame += len(out_str)
            except:
                pass
        sys.stdout.flush()
        
        self.cells_history.append(len(to_change))
        if len(self.cells_history) > cells_history_max:
            self.cells_history = self.cells_history[-1 * cells_history_max:]

        self.chars_history.append(chars_this_frame)
        if len(self.chars_history) > cells_history_max:
            self.chars_history = self.chars_history[-1 * cells_history_max:]

        
        # report for debug
        if self.debug_enabled:
            move_and_print(1, self.height + 3, f'                                      ')
            move_and_print(1, self.height + 3, f'Changed {len(to_change)} cells')
            move_and_print(1, self.height + 4, f'Frame count: {self.frame_count}')
        

    def full_redraw(self):
        clear_screen()
        self.update_display(full_redraw=True)

    def randbox(self):
        top_left_x = random.randrange(0, self.width - 3)
        top_left_y = random.randrange(0, self.height - 3)
        box_width = random.randrange(2, self.width - top_left_x)
        box_height = random.randrange(2, self.height - top_left_y)
        char = random.choice(['!', '@', '#', '$', '%', '^', '&', '*', '?', '<', '>', '.', ',', ':', ';', '-', '+', '='])
        color = random.choice(coloropt)
        if random.random() < 0.999:
            filled = False
        else:
            filled = True
        for i in range(0, box_width):
            for j in range(0, box_height):
                if filled or i == 0 or j == 0 or i == box_width - 1 or j == box_height - 1:
                    self.buffer_frame[(top_left_x + i, top_left_y + j)] = colorize(char, color=color, effects=['bold'])





if __name__ == '__main__':
    clear_screen()
    d = BufferedDisplay(200, 60)

    bouncer_x = 0
    bouncer_y = 0
    bouncer_xdir = 1
    bouncer_ydir = 1
    bouncer_char = colorize('*', color='magenta', effects=['bold'])

    while True:
        #d.randbox()
        d.buffer_frame[(bouncer_x, bouncer_y)] = bouncer_char
        bouncer_x += bouncer_xdir
        bouncer_y += bouncer_ydir
        if bouncer_x >= d.width - 1 or bouncer_x <= 0:
            bouncer_xdir = bouncer_xdir * -1
            bouncer_char = colorize('*', color=random.choice(coloropt), effects=['bold'])
        if bouncer_y >= d.height - 1 or bouncer_y <= 0:
            bouncer_ydir = bouncer_ydir * -1
            bouncer_char = colorize('*', color=random.choice(coloropt), effects=['bold'])


        time.sleep(0.02)