from tui import *
from utils import *

def null_content_func(panel):
    pass


chars = allowed_inputs['alphapunct']
char_index = 0


def fill_func(panel):
    global char_index
    for i in range(0, panel.x_size):
        for j in range(0, panel.y_size):
            char = chars[char_index]
            if i % 6 == 0 or j % 6 == 0 or i % j == 0:
                #panel.layer.points[(i, j)] = colorize(char, color='blue', effects=['bold', 'underline'])

                panel.layer.points[(i,j)] = char
    char_index += 1
    if char_index >= len(chars):
        char_index = 0


if __name__ == '__main__':
    tt = Tui()

    term_size_indicator = status_widgets.term_size(tt)
    frametime_indicator = status_widgets.last_frametime(tt)
    framerate_avg_indicator = status_widgets.framerate(tt)
    cell_change_stats_indicator = status_widgets.cell_change_stats(tt)
    char_volume_stats_indicator = status_widgets.char_volume_stats(tt)

    main_panel = tt.create_panel(tt.screen_width - 2, tt.screen_height - 3, name='Main Panel', border=False)
    main_panel.redraw_every_frame = True
    main_panel.content_func = fill_func
    main_panel.move(1, 2)