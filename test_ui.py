from termytui.tui import Tui, UIElement
from termytui.termy.termy import colorize, control_chars
from termytui.utils import null_content_func
from termytui import panel_widgets, status_widgets, element_widgets
import time
import math
import random
import threading


def sin_content_func(panel):
    colors = ['white', 'red', 'green', 'blue', 'yellow', 'magenta', 'cyan']
    panel.print_to_pos(2, 3, colorize('Sine Bars!', color=random.choice(colors), effects=['bold']))
    panel.print_to_pos(2, 5, ' ' * (panel.x_size - 2))
    panel.print_to_pos(2, 7, ' ' * (panel.x_size - 2))
    panel.print_to_pos(2, 9, ' ' * (panel.x_size - 2))
    panel.print_to_pos(2, 5, colorize('#' * int(abs(math.sin(time.time())) * (panel.x_size - 2)), color='blue', effects=['bold']))
    panel.print_to_pos(2, 7, colorize('#' * int(abs(math.sin(time.time() / 2)) * (panel.x_size - 2)), color='green', effects=['bold']))
    panel.print_to_pos(2, 9, colorize('#' * int(abs(math.sin(time.time() * 2)) * (panel.x_size - 2)), color='red', effects=['bold']))

    panel.print_to_pos(2, 18, f'Last Redraw: {time.time():.3f}')


def pb_thread_func(panel):
    x_max = tt.display.width - panel.x_size
    y_max = tt.display.height - panel.y_size

    x = random.randrange(1, x_max)
    y = random.randrange(3, y_max)

    if random.random() > 0.5:
        x_dir = -1 * random.choice([1,2])
    else:
       x_dir = random.choice([1,2])

    if random.random() > 0.5:
        y_dir = -1 * random.choice([1,2])
    else:
       y_dir = random.choice([1,2])
    

    while tt.render_enabled:
        panel.move(x, y)
        x = x + x_dir
        if x >= x_max:
            x_dir = -1 * x_dir
        if x <= 1:
            x_dir = -1 * x_dir
        y = y + y_dir
        if y >= y_max:
            y_dir = -1 * y_dir
        if y <= 3:
            y_dir = -1 * y_dir
        
        time.sleep(0.1)


test_background = [
    '.........................',
    '.----..-...-.-----.-----.',
    '. ... . ... ... ..... ...',
    '.====..=...=...=.....=...',
    '. ... . ... ... ..... ...',
    '.----...---....-.....-...',
    '.........................',
]


if __name__ == '__main__':
    tt = Tui()

    tt.log('Test TUI starting!')

    clock = status_widgets.clock(tt)
    term_size_indicator = status_widgets.term_size(tt)
    panel_counter = status_widgets.panel_count(tt)
    frametime_indicator = status_widgets.last_frametime(tt)
    framerate_avg_indicator = status_widgets.framerate(tt)
    cell_change_stats_indicator = status_widgets.cell_change_stats(tt)
    last_key_indicator = status_widgets.last_key(tt)
    last_err_indicator = status_widgets.last_log(tt)

    def bgcycle():
      colors = list(control_chars['fgcolor'].keys())
      idx = 1
      while tt.render_enabled:
        for x in range(0, tt.screen_width):
            for y in range(0, tt.screen_height):
                if test_background[y % len(test_background)][x % len(test_background[0])] != '.':
                    tt.background_layer.points[(x, y)] = colorize(test_background[y % len(test_background)][x % len(test_background[0])], colors[int(x + idx) % len(colors)], effects=['bold'], bg_color=colors[int(y + idx) % len(colors)])
                else:
                    tt.background_layer.points[(x, y)] = colorize(test_background[y % len(test_background)][x % len(test_background[0])], colors[int(y + idx) % len(colors)])
        time.sleep(0.05)
        idx += 1

    
    bgc_thread = threading.Thread(target=bgcycle)
    bgc_thread.start()

    p1 = tt.create_panel(30, 20, name='Panel 1')
    p1.content_func = sin_content_func
    p2 = tt.create_panel(80, 30, name='Panel 2')
    p2.content_func = null_content_func
    p1.redraw_every_frame = True
    p2.redraw_every_frame = True
    p1.move(80, 8)
    p2.move(15, 25)

    p1.set_z_pos(10)
    p2.set_z_pos(5)

    p1.border_horiz_char = '-'
    p1.border_corner_char = '+'
    p1.border_vert_char = '|'
    p1.border_corner_effects = ['bold']
    p1.border_vert_effects = []
    p1.border_horiz_effects = []
    p1.create_border()
    #pt = threading.Thread(target=pb_thread_func, args=(p1,))
    #pt.start()

    #pt2 = threading.Thread(target=pb_thread_func, args=(p2,))
    #pt2.start()

    p3 = panel_widgets.tui_log_panel(tt, width=tt.screen_width - 2, height=8)
    p3.move(0, tt.screen_height - 10)

    el1 = UIElement(p2, 'Fart', 2, 3)
    el1.redraw_every_frame = True

    def el1_content_func(element):
        if element.panel.active_element_index == element.panel.elements.index(element):
            out_str = f'My name is {element.name} and the time is {time.time():.1f} and I am SELECTED!    '
        else:
           out_str = f'My name is {element.name} and the time is {time.time():.1f} and I am NOT selected'
        element.panel.print_to_pos(element.top_left_x, element.top_left_y, out_str)
    
    el1.content_func = el1_content_func

    
    el2 = element_widgets.input_field_element(p2, 'Input 1', size=15, top_left_x=2, top_left_y=5, initial_value='fart')
    el3 = element_widgets.input_field_element(p2, 'Input 2', size=30, top_left_x=2, top_left_y=7, initial_value='your mother')

    def update_panel_name(ih, value):
       tt.log(f'update_panel_name called with value {value}')
       ih.element.panel.rename(value)

    el2.state['on_save'] = update_panel_name

    el4 = element_widgets.multiline_input_field_builder(p2, 'Multiline Input 1', width=60, height=5, top_left_x=2, top_left_y=9, initial_value='multiline field, bitch!')

    p4 = panel_widgets.display_perf_metrics_panel(tt, width=125)

    tt.system_modal.display_disappearing_message('This is a disappearing message!')

