from .termy.termy import colorize
from .utils import average
import time


def clock(tui):
    def clock_content():
        return colorize(time.strftime('%Y-%m-%d %H:%M:%S'), color='white', bg_color='blue', effects=['bold'])
    element = tui.create_status_element('Clock', clock_content)
    return element
    


def last_log(tui):
    def last_log_content():
        if len(tui.log_messages) > 0:
            log_str = colorize(f'{time.strftime("%H:%M:%S", time.localtime(tui.log_messages[-1][0]))}  {tui.log_messages[-1][1]}', color='cyan', effects=['bold'])
            return f'Last log: {log_str}'
        else:
            return f'Last log: {colorize("None logged!", color="cyan", effects=["bold"])}'
    element = tui.create_status_element('Last Log', last_log_content)
    return element


def panel_count(tui):
    def panel_count_content():
        return colorize(f'{len(tui.panels)} panel(s)', color='white', effects=['bold'])
    element = tui.create_status_element('Panel Count', panel_count_content)
    return element


def term_size(tui):
    def term_size_content():
        return 'Term Size: ' + colorize(f'{tui.terminal_dimensions[0]}x{tui.terminal_dimensions[1]}', color='cyan', effects=['bold'])
    element = tui.create_status_element('Terminal Size', term_size_content)
    return element


def framerate(tui):
    def framerate_content():
        if len(tui.frame_time_hist) > 0:
            return 'Avg FPS: ' + colorize(f'{(sum([1/x for x in tui.frame_time_hist]) / len(tui.frame_time_hist)):.0f}', color='cyan', effects=['bold'])
        else:
            return 'Avg FPS: Undefined!'
    element = tui.create_status_element('Framerate', framerate_content)
    return element


def last_frametime(tui):
    def last_frametime_content():
        if len(tui.frame_time_hist) > 0:
            return 'Last frame time: ' + colorize(f'{tui.frame_time_hist[-1]:.3f}s', color='cyan', effects=['bold'])
        else:
            return 'Last frame time: ' + colorize(f'No Data!', color='cyan', effects=['bold'])
    element = tui.create_status_element('Last Frame Time', last_frametime_content)
    return element


def cell_change_stats(tui):
    def cell_change_stats_content():
        if len(tui.display.cells_history) == 0:
            return 'Cell changes mn/mx/av: [no data]'   
        stats_str = colorize(f'{min(tui.display.cells_history)} / {max(tui.display.cells_history)} / {average(tui.display.cells_history):.0f}', color='cyan', effects=['bold'])
        return f'Cell changes mn/mx/av: {stats_str}'
    element = tui.create_status_element('Cell Change Stats', cell_change_stats_content)
    return element


def char_volume_stats(tui):
    def char_volume_stats_content():
        if len(tui.display.chars_history) == 0:
            return 'Chars/frame mn/mx/av: [no data]'   
        stats_str = colorize(f'{min(tui.display.chars_history)} / {max(tui.display.chars_history)} / {average(tui.display.chars_history):.0f}', color='cyan', effects=['bold'])
        return f'Chars/frame mn/mx/av: {stats_str}'
    element = tui.create_status_element('Cell Change Stats', char_volume_stats_content)
    return element


def last_key(tui):
    def last_key_content():
        return 'Last key: ' + colorize(f'{repr(tui.input_handler.last_key_pressed)}', color='cyan', effects=['bold'])
    element = tui.create_status_element('Last Key', last_key_content)
    return element