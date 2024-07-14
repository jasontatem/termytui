from .termy.termy import get_terminal_size, show_cursor, enable_echo, clear_screen, hide_cursor, disable_echo, colorize, Layer, coded_str_to_chars, control_chars
from .fb import BufferedDisplay
from .utils import allowed_inputs
import threading
import readchar
import time
import atexit


terminal_dimensions = get_terminal_size()
screen_width = terminal_dimensions[0]
screen_height = terminal_dimensions[1]


def final_exit():
    show_cursor()
    enable_echo()
    clear_screen()
    print('TUI Exiting!')

atexit.register(final_exit)


class Tui():
    def __init__(self):
        self.terminal_dimensions = get_terminal_size()
        self.screen_width = self.terminal_dimensions[0]
        self.screen_height = self.terminal_dimensions[1]

        self.render_enabled = True

        self.frame_sleep_time = 0.033

        self.frame_time_hist = list()
        self.frame_time_hist_max = 120

        self.log_messages = list()
        self.max_log_messages = 100

        self.panels = list()
        self.selected_panel_index = 0

        self.background_layer = Layer(0, 0)
        self.draw_background_layer = True

        self.colors = {
            'border_active': 'magenta',
            'border_inactive': 'white'
        }

        self.display = BufferedDisplay(screen_width, screen_height)

        self.status_line = StatusLine()
        self.input_handler = InputHandler(self)
        self.system_modal = SystemModal()

        clear_screen()
        hide_cursor()
        disable_echo()
        self.render_thread = threading.Thread(target=self.fb_render)
        self.render_thread.start()

        self.log('TUI initialized!')

    def exit(self):
        self.render_enabled = False
        while len(threading.enumerate()) > 0:
            print('Waiting for threads to exit!')
            print(f'Running threads: {threading.enumerate()}')
            time.sleep(0.1)
        
        
    def create_panel(self, x_size, y_size, name, border=True):
        panel = UIPanel(self, x_size, y_size, name=name, border=border)
        self.panels.append(panel)
        return panel
    
    def create_element(self, panel, name, top_left_x=1, top_left_y=1, input_enabled=True):
        element = UIElement(panel, name, top_left_x=top_left_x, top_left_y=top_left_y, input_enabled=input_enabled)
        return element
    
    def create_status_element(self, name, content_func):
        element = StatusElement(name, content_func)
        self.status_line.elements.append(element)
        return element
    
    def select_next_panel(self):
        self.selected_panel_index += 1
        if self.selected_panel_index >= len(self.panels):
            self.selected_panel_index = 0

        for i in range(0, len(self.panels)):
            if i == self.selected_panel_index and self.panels[i].border:
                self.panels[i].border_color = self.colors['border_active']
                self.panels[i].create_border(bold=True)
                self.panels[i].set_z_pos(0)
            elif self.panels[i].border:
                self.panels[i].border_color = self.colors['border_inactive']
                self.panels[i].create_border()
                self.panels[i].set_z_pos(10)

    def log(self, msg):
        log_time = time.time()
        self.log_messages.append((log_time, msg))
        if len(self.log_messages) > self.max_log_messages:
            self.log_messages = self.log_messages[-1 * self.max_log_messages:]

    def fb_render(self):
        while self.render_enabled:
            start_time = time.time()
            for p in [x for x in self.panels if x.redraw_every_frame or x.redraw_requested]:
                p.update_interior_content()
                p.redraw_requested = False
            if self.system_modal.visible:
                layers_to_draw = [p.layer for p in sorted(self.panels, key=lambda x: x.z_pos, reverse=True)] + [self.system_modal.layer]
            else:
                layers_to_draw = [p.layer for p in sorted(self.panels, key=lambda x: x.z_pos, reverse=True)]
            if self.draw_background_layer:
                layers_to_draw = [self.background_layer] + layers_to_draw
            self.status_line.render_content()
            layers_to_draw.append(self.status_line.layer)
            self.draw_layers_to_fb(1, 1, self.display.width + 1, self.display.height + 1, layers_to_draw)
            self.display.update_display()
            current_res = get_terminal_size()
            if current_res != self.terminal_dimensions:
                self.terminal_dimensions = current_res
                self.screen_width = terminal_dimensions[0]
                self.screen_height = terminal_dimensions[1]
                self.display.width = self.screen_width
                self.display.height = self.screen_height
                self.display.full_redraw()
                self.log(f'Terminal size changed, now {self.screen_width}x{self.screen_height}')
            mid_time = time.time()
            if self.frame_sleep_time > 0 and mid_time - start_time < self.frame_sleep_time:
                sleep_delay = self.frame_sleep_time - (mid_time - start_time)
                if sleep_delay > 0:
                    time.sleep(sleep_delay)
                else:
                    time.sleep(0)
            end_time = time.time()
            frame_time = end_time - start_time
            self.frame_time_hist.append(frame_time)
            if len(self.frame_time_hist) > self.frame_time_hist_max:
                self.frame_time_hist = self.frame_time_hist[-1 * self.frame_time_hist_max:]
            

    def draw_layers_to_fb(self, startx, starty, width, height, layers):
        self.display.blank_buffer()
        myframe = dict()
        for layer in layers:
            for point in dict(layer.points):
                pointx = point[0] + layer.xoffset
                pointy = point[1] + layer.yoffset
                myframe[(pointx, pointy)] = layer.points[point]

        mypoints = list(myframe)
        mypoints.sort()
        for point in mypoints:
            if point[0] <= width and point[1] <= height:
                self.display.buffer_frame[(point[0] + startx, point[1] + starty)] = myframe[point]
            

class SystemModal():
    # This class should only be used by the Tui class, which only creates 1 instance of it
    # Intended for display of critical messages or info about actions happening at the TUI layer, not the app within the TUI
    def __init__(self, x_pos=5, y_pos=5, x_size=30, y_size=10):
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.x_size = x_size
        self.y_size = y_size

        self.name = 'System Modal'
        self.title = 'System Message'
        
        self.border = True
        self.border_color = 'white'
        self.border_corner_char = '+'
        self.border_vert_char = '|'
        self.border_horiz_char = '-'

        self.visible = False

        self.rebuild()

    def rebuild(self):
        # rebuilds the modal from the ground up, including making a new Layer
        self.layer = Layer(self.x_pos, self.y_pos)
        self.blank()
        if self.border:
            self.create_border()
        self.create_title()

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def blank(self):
        # fills the entire layer with spaces
        for i in range(0, self.x_size):
            for j in range(0, self.y_size):
                self.layer.points[(i, j)] = ' '

    def create_title(self):
        self.print_to_pos(2, 1, colorize(self.title, color='magenta', effects=['bold']))

    def create_border(self):
        # corners
        self.layer.points[(0, 0)] = colorize(self.border_corner_char, color=self.border_color, effects=['bold'])
        self.layer.points[(0, self.y_size)] = colorize(self.border_corner_char, color=self.border_color, effects=['bold'])
        self.layer.points[(self.x_size, 0)] = colorize(self.border_corner_char, color=self.border_color, effects=['bold'])
        self.layer.points[(self.x_size, self.y_size)] = colorize(self.border_corner_char, color=self.border_color, effects=['bold'])

        # sides
        for i in range(1, self.y_size):
            self.layer.points[(0, i)] = colorize(self.border_vert_char, color=self.border_color, effects=['bold'])
            self.layer.points[(self.x_size, i)] = colorize(self.border_vert_char, color=self.border_color, effects=['bold'])

        # top/bottom
        for i in range(1, self.x_size):
            self.layer.points[(i, 0)] = colorize(self.border_horiz_char, color=self.border_color, effects=['bold'])
            self.layer.points[(i, self.y_size)] = colorize(self.border_horiz_char, color=self.border_color, effects=['bold'])

    def print_to_pos(self, x_pos, y_pos, text):
        coded_chars = coded_str_to_chars(text)
        for i in range(0, len(coded_chars)):
            self.layer.points[(x_pos + i, y_pos)] = coded_chars[i]

    def display_simple_message(self, message):
        self.rebuild()
        display_area_width = self.x_size - 3
        message_chars = coded_str_to_chars(message)
        idx = 0
        char_num = 0
        line_num = 0
        while idx < len(message_chars):
            self.print_to_pos(char_num + 2, line_num + 3, message_chars[idx])
            idx += 1
            char_num += 1
            if char_num == display_area_width:
                char_num = 0
                line_num += 1
        self.visible = True

    def display_disappearing_message(self, message, timeout=3):
        self.display_simple_message(message)
        to = threading.Timer(timeout, self.hide)
        to.start()


        


class StatusLine():
    # This class should only be used by the Tui class, which only creates 1 instance of it
    def __init__(self, y_pos=None):
        if y_pos is None:
            self.y_pos = 0
        self.elements = list()

        self.layer = Layer(0, self.y_pos)

    def render_content(self):
        self.layer.points = dict()
        content = ''
        for i in range(0, len(self.elements)):
            content += str(self.elements[i].render_content())
            if i != len(self.elements) - 1:
                content += colorize(' | ', color='cyan')
        coded_chars = coded_str_to_chars(content)
        for i in range(0, len(coded_chars)):
            self.layer.points[(i, 0)] = coded_chars[i]



class StatusElement():
    def __init__(self, name, content_func):
        self.name = name
        self.content_func = content_func
    
    def render_content(self):
        return self.content_func()


class UIPanel():
    def __init__(self, tui, x_size, y_size, name='unnamed', z_pos=0, border=True, border_color='white'):
        self.tui = tui
        self.x_size = x_size
        self.y_size = y_size
        self.z_pos = z_pos
        self.name = name
        self.border = border
        self.border_color = border_color
        self.border_corner_char = ' '
        self.border_corner_effects = ['bold', 'inverse']
        self.border_vert_char = '|'
        self.border_vert_effects = ['bold']
        self.border_horiz_char = '-'
        self.border_horiz_effects = ['bold']

        self.elements = list()
        self.active_element_index = 0

        self.layer = Layer(0, 0)
        if self.border:
            self.create_border()
        self.fill_interior()
        #self.print_to_pos(2, 1, colorize(self.name, color='white', effects=['bold', 'inverse']))

        self.input_handler = PanelInputHandler(self)

        self.redraw_every_frame = True
        self.redraw_requested = False

        self.content_func = None

        self.tui.log(f'{self.name}::Panel created')

    def destroy(self):
        self.tui.log(f'{self.name}::destroy called, removing myself from panels list')
        self.tui.panels.remove(self)

    def rename(self, value):
        self.tui.log(f'{self.name}::rename called, name will now be {value}')
        self.name = value
        self.print_to_pos(2, 1, ' ' * (self.x_size - 2))
        self.print_to_pos(2, 1, colorize(self.name, color='white', effects=['bold', 'inverse']))

    def move(self, new_x_offset, new_y_offset):
        self.layer.xoffset = new_x_offset
        self.layer.yoffset = new_y_offset
        self.redraw_requested = True

    def set_z_pos(self, z_pos):
        self.z_pos = z_pos
        self.redraw_requested = True

    def create_border(self, bold=False):
        # corners
        self.layer.points[(0, 0)] = colorize(self.border_corner_char, color=self.border_color, effects=self.border_corner_effects)
        self.layer.points[(0, self.y_size)] = colorize(self.border_corner_char, color=self.border_color, effects=self.border_corner_effects)
        self.layer.points[(self.x_size, 0)] = colorize(self.border_corner_char, color=self.border_color, effects=self.border_corner_effects)
        self.layer.points[(self.x_size, self.y_size)] = colorize(self.border_corner_char, color=self.border_color, effects=self.border_corner_effects)

        # sides
        for i in range(1, self.y_size):
            self.layer.points[(0, i)] = colorize(self.border_vert_char, color=self.border_color, effects=self.border_vert_effects)
            self.layer.points[(self.x_size, i)] = colorize(self.border_vert_char, color=self.border_color, effects=self.border_vert_effects)

        # top/bottom
        for i in range(1, self.x_size):
            self.layer.points[(i, 0)] = colorize(self.border_horiz_char, color=self.border_color, effects=self.border_horiz_effects)
            self.layer.points[(i, self.y_size)] = colorize(self.border_horiz_char, color=self.border_color, effects=self.border_horiz_effects)

    def fill_interior(self):
        for i in range(1, self.x_size):
            for j in range(1, self.y_size):
                self.layer.points[(i, j)] = ' '

    def blank(self):
        # fills the layer with spaces
        for x in range(0, self.x_size):
            for y in range(0, self.y_size):
                self.layer.points[(x, y)] = ' '

    def clear_panel(self, blank=False):
        self.layer.points = dict()
        if blank:
            self.blank()
        if self.border:
            self.create_border()
        self.redraw_requested = True

    def update_interior_content(self):
        if self.content_func is None:
            self.print_to_pos(2, 3, f'Size: {self.x_size} x {self.y_size}')
            self.print_to_pos(2, 4, f'Pos: {self.layer.xoffset} x {self.layer.yoffset}')
            self.print_to_pos(2, 5, f'ZDepth: {self.z_pos}')
            
            self.print_to_pos(2, 6, f'Always Redraw: {self.redraw_every_frame}')
            self.print_to_pos(2, 7, f'Last Redraw: {time.time():.3f}')
        else:
            self.content_func(self)
        for element in [e for e in self.elements if e.redraw_requested or e.redraw_every_frame]:
            element.update_interior_content()
            element.redraw_requested = False

    def print_to_pos(self, x_pos, y_pos, text):
        coded_chars = coded_str_to_chars(text)
        for i in range(0, len(coded_chars)):
            self.layer.points[(x_pos + i, y_pos)] = coded_chars[i]

    def select_element(self, index):
        if len(self.elements) > 0 and index >= 0 and index < len(self.elements):
            self.active_element_index = index
            self.elements[index].select()

    def select_next_element(self):
        next_index = self.active_element_index + 1
        old_index = self.active_element_index
        if next_index >= 0 and next_index < len(self.elements):
            self.tui.log(f'{self.name}::Selecting next element index {next_index}')
            self.select_element(next_index)
            if old_index >= 0 and old_index < len(self.elements):
                self.elements[old_index].redraw_requested = True
    
    def select_prev_element(self):
        prev_index = self.active_element_index - 1
        old_index = self.active_element_index
        if prev_index >= 0 and prev_index < len(self.elements):
            self.tui.log(f'{self.name}::Selecting prev element index {prev_index}')
            self.select_element(prev_index)
            if old_index >= 0 and old_index < len(self.elements):
                self.elements[old_index].redraw_requested = True


class UIElement():
    def __init__(self, panel, name, top_left_x=1, top_left_y=1, input_enabled=True):
        self.panel = panel
        self.name = name
        self.top_left_x = top_left_x
        self.top_left_y = top_left_y
        self.redraw_requested = True
        self.redraw_every_frame = False
        self.state = dict()
        self.input_enabled = input_enabled
        self.input_handler = ElementInputHandler(self)

        # various event-based funcs
        self.on_select = None
        self.on_input = None
        self.content_func = None

        self.panel.elements.append(self)
        self.panel.tui.log(f'{self.panel.name}::{self.name}::Element created')

    def select(self):
        self.redraw_requested = True
        if self.on_select is not None:
            self.on_select(self)

    def update_interior_content(self):
        if self.content_func is not None:
            self.content_func(self)

    def print_to_pos(self, x, y, text):
        self.panel.print_to_pos(self.top_left_x + x, self.top_left_y + y, text)

    def destroy(self):
        self.panel.elements.remove(self)
    
    def set_pos(self, x, y):
        self.top_left_x = x
        self.top_left_y = y
        self.redraw_requested = True

    
class ElementInputHandler():
    def __init__(self, element):
        self.element = element
        self.last_key_received = None

        # these dicts will contain input_key: handler_func pairs similar to the larger InputHandler
        self.hotkeys = dict()

        self.multichar_input_active = False
        self.multichar_input_buffer = ''
        self.multichar_imput_allowed_chars = allowed_inputs['alphapunct'] + allowed_inputs['space']
        self.multichar_input_end_key = '\n'
        self.multichar_input_update_callback_func = None
        self.multichar_input_end_callback_func = None
        self.multichar_input_max_size = None

    def input_router(self, c):
        self.last_key_received = c

        # if there's an on_input func on the element, we'll call that first before we do our own processing
        if self.element.on_input is not None:
            self.element.on_input(self, c)

        if c in self.hotkeys:
            self.element.panel.tui.log(f'{self.element.panel.name}::{self.element.name}::Hotkey {repr(c)} matched')
            fallthrough = self.hotkeys[c](self)
            if not fallthrough:
                return
            self.element.panel.tui.log(f'{self.element.panel.name}::{self.element.name}::Hotkey func returned a truthy value, falling through')
        
        if self.multichar_input_active:
            self.element.panel.tui.log(f'{self.element.panel.name}::{self.element.name}::Multichar input receiving a char')
            if c == self.multichar_input_end_key:
                self.element.panel.tui.log(f'{self.element.panel.name}::{self.element.name}::Multichar input end char received')
                if self.multichar_input_end_callback_func is not None:
                    self.multichar_input_end_callback_func(self, self.multichar_input_buffer)
                self.multichar_input_active = False
                return
            elif c in self.multichar_imput_allowed_chars and (self.multichar_input_max_size is None or len(self.multichar_input_buffer) < self.multichar_input_max_size):
                self.element.panel.tui.log(f'{self.element.panel.name}::{self.element.name}::Multichar input received allowed input char')
                self.multichar_input_buffer += c
                if self.multichar_input_update_callback_func is not None:
                    self.multichar_input_update_callback_func(self, self.multichar_input_buffer, c)
                return
            elif c in self.multichar_imput_allowed_chars and self.multichar_input_max_size is not None and len(self.multichar_input_buffer) >= self.multichar_input_max_size:
                self.element.panel.tui.log(f'{self.element.panel.name}::{self.element.name}::Multichar input at max chars, rejecting input')
                return
        
        self.element.panel.tui.log(f'{self.element.panel.name}::{self.element.name}::Char {repr(c)} received but not handled')


class PanelInputHandler():
    def __init__(self, panel):
        self.panel = panel

        # these dicts will contain input_key: handler_func pairs similar to the larger InputHandler
        self.hotkeys = dict()

        self.last_key_received = None

        self.hotkeys['\x1bx'] = self.panel.destroy  #  alt-x = close panel

        self.hotkeys['\x1b[5~'] = self.panel.select_prev_element  # pgup = select previous element
        self.hotkeys['\x1b[6~'] = self.panel.select_next_element  # pgdn = select next element
        
    def input_router(self, c):
        self.last_key_received = c
        self.panel.tui.log(f'{self.panel.name}::Char {repr(c)} received')

        if c in self.hotkeys:
            self.panel.tui.log(f'{self.panel.name}::Char {repr(c)} is a panel hotkey')
            fallthrough = self.hotkeys[c]()
            if not fallthrough:
                return
            self.panel.tui.log(f'{self.panel.name}::Hotkey func returned a truthy value, falling through')
        
        if len(self.panel.elements) > 0 and self.panel.active_element_index >= 0 and self.panel.active_element_index < len(self.panel.elements) and self.panel.elements[self.panel.active_element_index].input_enabled:
            self.panel.elements[self.panel.active_element_index].input_handler.input_router(c)
            return
        
        self.input_fallback(c)
        
    def input_fallback(self, c):
        # will be called if it doesn't match anything else at the bottom of input_router
        self.panel.print_to_pos(2, self.panel.y_size - 1, f'Last key received: {repr(c)}')



class InputHandler():
    def __init__(self, tui):
        # these dicts will contain input_key: handler_func pairs
        self.tui = tui
        self.reserved_keys = dict()
        self.global_keys = dict()
        self.last_key_pressed = None
        self.state = dict()

        self.global_keys['\x1bn'] = tui.select_next_panel    # alt-n: select next panel
        self.global_keys['\x1bz'] = self.tui.display.full_redraw  # alt-z: force full screen redraw
        self.global_keys['\x1bq'] = tui.exit                  # alt-q: quit
        self.global_keys['\x1bm'] = self.panel_move_start     # alt-m: move current panel

        self.input_thread = threading.Thread(target=self.input_thread_runner, daemon=True)
        self.input_thread.start()

    def input_thread_runner(self):
        while self.tui.render_enabled:
            c = readchar.readkey()
            self.input_router(c)
            
    def input_router(self, c):
        self.tui.log(f'input_handler::Char {repr(c)} received')
        self.last_key_pressed = c

        if 'panel_move_active' in self.state.keys() and self.state['panel_move_active']:
            # Override other behaviors while in panel move mode
            self.panel_move_handler(c)
            return

        if c in self.global_keys:
            self.global_keys[c]()
            return
        
        if c in self.reserved_keys:
            self.reserved_keys[c]()
            return
        
        if len(self.tui.panels) > 0 and self.tui.selected_panel_index >= 0 and self.tui.selected_panel_index < len(self.tui.panels):
            self.tui.panels[self.tui.selected_panel_index].input_handler.input_router(c)
            return
        
        self.tui.log(f'input_handler::Char received but not processed')

    def panel_move_start(self):
        # to be called when we receive the "move current panel" hotkey
        if 'panel_move_active' in self.state.keys() and self.state['panel_move_active']:
            # do nothing, we're already in the mode, don't need to do anything now
            return
        self.tui.system_modal.display_simple_message('Panel move active: Use arrow keys to move the selected panel, press Enter to end')
        self.state['panel_move_active'] = True

    def panel_move_handler(self, c):
        if c == '\x1b[A':  # up arrow
            self.tui.panels[self.tui.selected_panel_index].move(self.tui.panels[self.tui.selected_panel_index].layer.xoffset, self.tui.panels[self.tui.selected_panel_index].layer.yoffset - 1)
        elif c == '\x1b[B':  # down arrow
            self.tui.panels[self.tui.selected_panel_index].move(self.tui.panels[self.tui.selected_panel_index].layer.xoffset, self.tui.panels[self.tui.selected_panel_index].layer.yoffset + 1)
        elif c == '\x1b[C':  # right arrow
            self.tui.panels[self.tui.selected_panel_index].move(self.tui.panels[self.tui.selected_panel_index].layer.xoffset + 1, self.tui.panels[self.tui.selected_panel_index].layer.yoffset)
        elif c == '\x1b[D':  # left arrow
            self.tui.panels[self.tui.selected_panel_index].move(self.tui.panels[self.tui.selected_panel_index].layer.xoffset - 1, self.tui.panels[self.tui.selected_panel_index].layer.yoffset)
        elif c == '\n':  # enter
            self.panel_move_end()

    def panel_move_end(self):
        # to be called when we receive Enter during panel move, signifying no more moving
        self.state['panel_move_active'] = False
        self.tui.system_modal.hide()