from .termy.termy import colorize
import time
from .utils import *
from .element_widgets import *

def tui_log_panel(tui, width=100, height=40, z_depth=20):
    panel = tui.create_panel(width, height, name='TUI Log Viewer')
    panel.move(tui.screen_width - width - 1, 2)
    panel.set_z_pos(z_depth)
    
    def tui_log_panel_content(panel):
        panel.clear_panel(blank=True)
        num_logs = panel.y_size - 2
        index = 0
        for l in panel.tui.log_messages[-1 * num_logs:]:
            log_str = colorize(f'{time.strftime("%H:%M:%S", time.localtime(l[0]))}  {l[1]}', color='cyan', effects=['bold'])
            panel.print_to_pos(2, index + 1, log_str)
            index += 1
    
    panel.content_func = tui_log_panel_content
    return panel


def display_perf_metrics_panel(tui, width=100, height=30, z_depth=0):
    panel = tui.create_panel(width, height, name='Display Perf Metrics')
    panel.move(tui.screen_width - width - 2, 1)
    panel.set_z_pos(z_depth)
    panel.content_func = null_content_func

    def chars_data_func():
        return panel.tui.display.chars_history
    
    chars_graph_element = basic_line_chart_element(panel, 
                                                   'Chars Printed Graph', 
                                                   panel.x_size - 2, 
                                                   int(panel.y_size / 3) - 2,
                                                   chars_data_func,
                                                   x_axis_title='Time',
                                                   y_axis_title='Chars',
                                                   line_color='blue',
                                                   top_left_y=1
                                                   )

    def cells_data_func():
        return panel.tui.display.cells_history
    
    cells_graph_element = basic_line_chart_element(panel, 
                                                   'Cells Changed Graph', 
                                                   panel.x_size - 2, 
                                                   int(panel.y_size / 3) - 2,
                                                   cells_data_func,
                                                   x_axis_title='Time',
                                                   y_axis_title='Cells',
                                                   line_color='green',
                                                   top_left_y=int(panel.y_size / 3) + 1
                                                   )
    
    def fps_data_func():
        return [int(1 / x) for x in panel.tui.frame_time_hist]
    
    cells_graph_element = basic_line_chart_element(panel, 
                                                   'FPS Graph', 
                                                   panel.x_size - 2, 
                                                   int(panel.y_size / 3) - 2,
                                                   fps_data_func,
                                                   x_axis_title='Time',
                                                   y_axis_title='FPS',
                                                   line_color='red',
                                                   top_left_y=int(panel.y_size / 3) * 2 + 1
                                                   )