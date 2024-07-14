# TITWSTE: TITWSTE Is The World's Shittiest Text Editor
# A terrible text editor intended to be a minimal TermyTUI app demo
# Invoke as: python3 titwste.py

from termytui.tui import Tui
from termytui.utils import null_content_func
from termytui import status_widgets, element_widgets


def save_text_to_file():
    filename = filename_entry.state['value']
    with open(filename, 'w') as f:
        f.write(text_entry.state['value'])
    tt.log(f'Saved {len(text_entry.state["value"])} chars to {filename}')


def load_text_from_file():
    filename = filename_entry.state['value']
    with open(filename, 'r') as f:
        text = f.read()
    text_entry.state['value'] = text
    text_entry.redraw_requested = True
    tt.log(f'Loaded {len(text)} chars from {filename}')


if __name__ == '__main__':
    tt = Tui()

    tt.log('TUI started')

    term_size_indicator = status_widgets.term_size(tt)
    panel_counter = status_widgets.panel_count(tt)
    frametime_indicator = status_widgets.last_frametime(tt)
    framerate_avg_indicator = status_widgets.framerate(tt)
    cell_change_stats_indicator = status_widgets.cell_change_stats(tt)
    last_key_indicator = status_widgets.last_key(tt)
    last_err_indicator = status_widgets.last_log(tt)
    
    main_panel = tt.create_panel(tt.screen_width - 2, tt.screen_height - 2, name='Main Panel')
    main_panel.redraw_every_frame = True
    main_panel.content_func = null_content_func
    main_panel.move(1, 2)

    main_panel.input_handler.hotkeys['\x1bs'] = save_text_to_file
    main_panel.input_handler.hotkeys['\x1bl'] = load_text_from_file

    filename_entry = element_widgets.multiline_input_field_builder(main_panel,
                                                   'Filename',
                                                   initial_value='out.txt',
                                                   max_size=1000,
                                                   width=200,
                                                   height=1,
                                                   top_left_x=3,
                                                   top_left_y=2,
                                                   show_field_name=True
                                                   )

    text_entry = element_widgets.multiline_input_field_builder(main_panel, 
                                               'Text Entry', 
                                               max_size=10000000, 
                                               width=tt.display.width - 10, 
                                               height=tt.display.height - 10,
                                               top_left_x=4, 
                                               top_left_y=6, 
                                               show_field_name=False
                                               )
    

