# Library of terminal control functions

import sys
import os
import termios
import time


t_fd = sys.stdin.fileno()
orig_term_settings = termios.tcgetattr(t_fd)


control_chars = {
    'fgcolor': {
        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'magenta': '35',
        'cyan': '36',
        'white': '37',
    },
    'bgcolor': {
        'black': '40',
        'red': '41',
        'green': '42',
        'yellow': '43',
        'blue': '44',
        'magenta': '45',
        'cyan': '46',
        'white': '47',
    },
    'effect': {
        'normal': '0',
        'bold': '1',
        'underline': '4',
        'blink': '5',
        'inverse': '7'
    }
}


class Layer(object):
    def __init__(self,xoffset,yoffset):
        self.xoffset = xoffset
        self.yoffset = yoffset
        self.points = {}

    def setpoint(self, point, char):
        self.points[point] = char

    def delpoint(self, point):
        self.points.pop(point)

    def replacechar(self, char):
        for point in self.points:
            self.points[point] = char


def colorize(text, color=None, bg_color=None, effects=None):
    if color is None and bg_color is None and effects is None:
        return text
    
    codes = list()
    if color is not None and color in control_chars['fgcolor'].keys():
        codes.append(control_chars['fgcolor'][color])
    if bg_color is not None and bg_color in control_chars['bgcolor'].keys():
        codes.append(control_chars['bgcolor'][bg_color])
    if effects is not None:
        for e in effects:
            if e in control_chars['effect'].keys():
                codes.append(control_chars['effect'][e])
    return f'\033[{";".join(codes)}m{text}\033[0m'
    

def colortext(text, color, underline=False, bold=False, inverse=False, bgcolor=None):
    effects = list()
    if bold:
        effects.append('bold')
    if underline:
        effects.append('underline')
    if inverse:
        effects.append('inverse')
    return colorize(text, color=color, bg_color=bgcolor, effects=effects)


coloropt = ['red', 'green', 'yellow', 'blue', 'magenta', 'cyan', 'white']


def clear_screen():
    sys.stdout.write("\033[2J\033[;H\033[0m")


def show_cursor():
    sys.stdout.write("\x1b[?25h")


def hide_cursor():
    sys.stdout.write("\x1b[?25l")


def disable_echo():
    new_settings = termios.tcgetattr(t_fd)
    new_settings[3] = new_settings[3] & ~termios.ECHO
    termios.tcsetattr(t_fd, termios.TCSADRAIN, new_settings)


def enable_echo():
    termios.tcsetattr(t_fd, termios.TCSADRAIN, orig_term_settings)


def move_cursor(x, y):
    sys.stdout.write('\033[' + str(y) + ';' + str(x) + 'H')


def move_cursor_left(n=1):
    sys.stdout.write(f'\033[{n}D')


def move_cursor_right(n=1):
    sys.stdout.write(f'\033[{n}C')


def move_cursor_up(n=1):
    sys.stdout.write(f'\033[{n}A')


def move_cursor_down(n=1):
    sys.stdout.write(f'\033[{n}B')


def flush():
    sys.stdout.flush()


def move_and_print(x, y, string, clear=False, cleardelay=0.1, flush=True):
    move_cursor(x, y)
    sys.stdout.write(string)
    sys.stdout.write('\033[0m')
    if flush:
        sys.stdout.flush()
    if clear:
        time.sleep(cleardelay)
        move_cursor(x, y)
        sys.stdout.write(' \033[0m')
        if flush:
            sys.stdout.flush()


def get_terminal_size():
    s = os.get_terminal_size()
    return (s[0], s[1])


def get_cursor_pos():
    # Save stdin configuration
    fd = sys.stdin.fileno()
    oldsettings = termios.tcgetattr(fd)

    # put terminal into raw mode
    settings = termios.tcgetattr(fd)
    settings[3] = settings[3] & ~(termios.ECHO | termios.ICANON)
    termios.tcsetattr(sys.stdin, termios.TCSAFLUSH, settings)


    # Request cursor position
    sys.stdout.write("\033[6n")
    sys.stdout.flush()

    resp = ''
    char = ''
    while char != 'R':
        char = sys.stdin.read(1)
        resp += char

    # Restore previous stdin configuration
    termios.tcsetattr(fd, termios.TCSADRAIN, oldsettings)

    # Split answer in two and return COL and ROW as tuple
    x =  tuple([int(i) for i in resp[2:-1].split(';')])
    return x


def draw_sprite(pixels, xtopleft, ytopleft, fillchar='', clear=False): # clear replaces the "pixel" characters with spaces. Does not change behavior of fillchar.
    xmin = min([y[0] for x,y in sorted((tup[1], tup) for tup in pixels)]) + xtopleft
    xmax = max([y[0] for x,y in sorted((tup[1], tup) for tup in pixels)]) + xtopleft
    ymin = min([y[1] for x,y in sorted((tup[1], tup) for tup in pixels)]) + ytopleft
    ymax = max([y[1] for x,y in sorted((tup[1], tup) for tup in pixels)]) + ytopleft

    for i in range(xmin, xmax + 1):
        for j in range(ymin, ymax + 1):
            move_and_print(i, j, fillchar)
    for pixel in pixels:
        if clear:
            move_and_print(pixel[0] + xtopleft, pixel[1] + ytopleft, ' ')
        else:
            move_and_print(pixel[0] + xtopleft, pixel[1] + ytopleft, pixel[2])
  

def load_sprite_file(spritefile, transparent=False):
    f = open(spritefile, 'r')
    spritepoints = {}
    linecount = 1
    for line in f:
        line = line.rstrip('\n')
        for i in range(0, len(line)):
            if line[i] == ' ':
                if not transparent:
                    spritepoints[(i + 1, linecount)] = line[i]
            else:
                spritepoints[(i + 1, linecount)] = line[i]
            linecount += 1
    return spritepoints

def draw_layers(startx, starty, width, height, layers):
    myframe = {}
    for layer in layers:
        for point in layer.points:
            pointx = point[0] + layer.xoffset
            pointy = point[1] + layer.yoffset
            myframe[(pointx, pointy)] = layer.points[point]

    mypoints = list(myframe)
    mypoints.sort()
    for point in mypoints:
        if point[0] <= width and point[1] <= height:
            move_and_print(point[0] + startx, point[1] + starty, myframe[point])


def coded_str_to_chars(text, remove_codes=False):
    if len(text) == 0:
        return text
    fg_codes = ['30', '31', '32', '33', '34', '35', '36', '37']
    bg_codes = ['40', '41', '42', '43', '44', '45', '46', '47']
    result = list()
    current_effective_codes = list()
    index = 0
    finished = False
    while not finished:
        char = text[index]
        if char == '\033' and index < len(text) - 1 and text[index + 1] == '[':  # we are entering an excape sequence
            #print(f'Found esc+[ at index {index}')
            # grab chars til we hit ; or m
            found_terminator = False
            offset = 2
            current_code_buffer = ''
            while not found_terminator:
               next_char = text[index + offset]
               if next_char != ';' and next_char != 'm':
                    current_code_buffer += next_char
                    offset += 1
               else:
                   if current_code_buffer != '' and current_code_buffer not in current_effective_codes:
                        if current_code_buffer != '0':
                            if current_code_buffer in fg_codes and len([x for x in current_effective_codes if x in fg_codes]) > 0:
                                # remove existing foreground codes
                                while len([x for x in current_effective_codes if x in fg_codes]) > 0:
                                    to_remove = [x for x in current_effective_codes if x in fg_codes][0]
                                    current_effective_codes.remove(to_remove)
                                    #print(f'Removing redundant foreground color code: {to_remove}')
                            if current_code_buffer in bg_codes and len([x for x in current_effective_codes if x in bg_codes]) > 0:
                                # remove existing background codes
                                while len([x for x in current_effective_codes if x in bg_codes]) > 0:
                                    to_remove = [x for x in current_effective_codes if x in bg_codes][0]
                                    current_effective_codes.remove(to_remove)
                                    #print(f'Removing redundant background color code: {to_remove}')
                            current_effective_codes.append(current_code_buffer)
                            #print(f'Adding code to current_effective_codes: {current_code_buffer}')
                            offset += 1
                            current_code_buffer = ''
                        else:
                            #print(f'Found clear code at index {index} offset {offset}')
                            current_effective_codes = list()
                            offset += 1
                            current_code_buffer = ''
                   if next_char == 'm':
                        found_terminator = True
                        #print(f'Found terminator at index {index} offset {offset}')
                        index += offset
        else:
            if len(current_effective_codes) > 0 and not remove_codes:
              char_str = f'\033[{";".join(list(current_effective_codes))}m{text[index]}\033[0m'
            else:
              char_str = text[index]
            #print(f'Adding to result: {char_str} using {len(current_effective_codes)} codes: {current_effective_codes}')
            result.append(char_str)
            index += 1
        if index == len(text):
            finished = True
    return result

                 
                    

                  


