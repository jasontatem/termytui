# Element widget library for TermyTUI
# tui.py imports this, so these can be used as tui.element_widgets.[whatever]
# Required arguments for all:
# - panel: the owning UIPanel object
# - name: the name of the element
# - top_left_x/y: top left corner coordinates
# Specific elements may have their own additional parameters

from .termy.termy import colorize
from .utils import *
from copy import deepcopy


def basic_line_chart_element(panel, name, width, height, data_series_func, top_left_x=1, top_left_y=1, x_axis_title='', y_axis_title='', line_color='green', line_char='*'):
    element = panel.tui.create_element(panel, name, top_left_x=top_left_x, top_left_y=top_left_y)
    element.state['width'] = width
    element.state['height'] = height
    element.state['data_func'] = data_series_func
    element.state['x_axis_title'] = x_axis_title
    element.state['y_axis_title'] = y_axis_title
    element.state['line_color'] = line_color

    def basic_line_chart_content_func(element):
        element.state['data'] = element.state['data_func']()
        if element.state['x_axis_title'] == '':
            graph_height = element.state['height']
        else:
            graph_height = element.state['height'] - 2
        if element.state['y_axis_title'] == '':
            graph_width = element.state['width']
        else:
            graph_width = element.state['width'] - 2

        data_max = 0

        for i in range(0, len(element.state['data'])):
            if element.state['data'][i] > data_max:
                data_max = element.state['data'][i]


        for x in range(0, element.state['width']):
            for y in range(0, element.state['height']):
                element.print_to_pos(x, y, ' ')

        #element.panel.tui.log(f'Max: {data_max}')

        if data_max > 0:
            data_scale_factor = graph_height / data_max
        else:
            data_scale_factor = 0
        if len(element.state['data']) > 0:
            series_scale_factor = graph_width / len(element.state['data'])
        else:
            series_scale_factor = 0

        #element.panel.tui.log(f'len {len(element.state["data"])} series scale {series_scale_factor}')

        # draw the graph

        colored_line_char = colorize(line_char, line_color, effects=['bold'])
        for i in range(0, len(element.state['data'])):
            y_pos = element.state['height'] - int(element.state['data'][i] * data_scale_factor)
            
            x_pos = int(i * series_scale_factor)
            element.print_to_pos(x_pos + 2, y_pos - 1, colored_line_char)
            #element.panel.tui.log(f'Graph x {x_pos} y {y_pos} data {element.state["data"][i]}')

        # draw axes

        if element.state['x_axis_title'] != '':
            start_point = int((element.state['width'] - len(element.state['x_axis_title'])) / 2)
            element.print_to_pos(start_point, element.state['height'], element.state['x_axis_title'])

        if element.state['y_axis_title'] != '':
            start_point = int((element.state['height'] - len(element.state['y_axis_title'])) / 2)
            for i in range(0, len(element.state['y_axis_title'])):
                element.print_to_pos(0, start_point + i, element.state['y_axis_title'][i])
            element.print_to_pos(2, 0, f'Max: {data_max:.1f}')

    
    element.content_func = basic_line_chart_content_func
    element.redraw_every_frame = True

    return element


def input_field_element(panel, name, size=10, initial_value='', top_left_x=1, top_left_y=1, on_save=pass_func, allowed_chars=None):
    element = panel.tui.create_element(panel, name, top_left_x=top_left_x, top_left_y=top_left_y)
    element.state['value'] = initial_value
    element.state['input_max_size'] = size
    element.state['on_save'] = on_save
    if allowed_chars is None:
        element.state['allowed_chars'] = allowed_inputs['alphapunct'] + allowed_inputs['space']
    else:
        element.state['allowed_chars'] = allowed_chars

    def input_field_content_func(element):
        if element.panel.active_element_index == element.panel.elements.index(element):
            field_name_str = colorize(f'{element.name}:', color='white', effects=['bold', 'inverse'])
        else:
            field_name_str = colorize(f'{element.name}:', color='white', effects=['bold'])
        if element.input_handler.multichar_input_active:
            value_str = colorize(element.state['value'] + (' ' * (element.state['input_max_size'] - len(element.state['value']))), color='cyan', effects=['inverse', 'underline'])
        else:
            value_str = colorize(element.state['value'] + (' ' * (element.state['input_max_size'] - len(element.state['value']))), color='white', effects=['underline'])
        
        element.panel.print_to_pos(element.top_left_x, element.top_left_y, f'{field_name_str} {value_str}')

    def input_edit_hotkey_func(input_handler):
        panel.tui.log(f'{input_handler.element.panel.name}::{input_handler.element.name}::Edit hotkey pressed')
        if not input_handler.multichar_input_active:
            input_handler.multichar_input_active = True
            input_handler.multichar_input_buffer = input_handler.element.state['value']
            input_handler.multichar_input_max_size = input_handler.element.state['input_max_size']
            input_handler.multichar_input_allowed_chars = element.state['allowed_chars']
            input_handler.element.redraw_requested = True
        else:
            return True

    def input_multichar_update_func(input_handler, value, c):
        panel.tui.log(f'{input_handler.element.panel.name}::{input_handler.element.name}::Value updated, now {value}')
        input_handler.element.state['value'] = value
        input_handler.element.redraw_requested = True

    def input_multichar_save_func(input_handler, value):
        panel.tui.log(f'{input_handler.element.panel.name}::{input_handler.element.name}::Saved value {value}')
        input_handler.element.state['value'] = value
        input_handler.multichar_input_active = False
        input_handler.element.redraw_requested = True
        input_handler.element.state['on_save'](input_handler, value)

    def backspace_handler(input_handler):
        panel.tui.log(f'{input_handler.element.panel.name}::{input_handler.element.name}::Backspace pressed')
        input_handler.element.state['value'] = input_handler.element.state['value'][:-1]
        input_handler.multichar_input_buffer = input_handler.element.state['value']
        input_handler.element.redraw_requested = True


    element.content_func = input_field_content_func
    element.input_handler.hotkeys['\n'] = input_edit_hotkey_func
    element.input_handler.hotkeys['\x7f'] = backspace_handler
    element.input_handler.multichar_input_update_callback_func = input_multichar_update_func
    element.input_handler.multichar_input_end_callback_func = input_multichar_save_func

    return element


def multiline_input_field_builder(panel, name, max_size=500, width=10, height=5, initial_value='', top_left_x=1, top_left_y=1, on_save=pass_func, allowed_chars=None, show_field_name=True):
    element = panel.tui.create_element(panel, name, top_left_x=top_left_x, top_left_y=top_left_y)

    element.state['value'] = initial_value
    element.state['input_max_size'] = max_size
    element.state['input_width'] = width
    element.state['input_height'] = height
    element.state['on_save'] = on_save
    element.state['input_show_field_name'] = show_field_name
    element.state['cursor_pos'] = len(element.state['value'])

    if allowed_chars is None:
        element.state['allowed_chars'] = allowed_inputs['alphapunct'] + allowed_inputs['space']
    else:
        element.state['allowed_chars'] = allowed_chars

    def multiline_input_field_content_func(element):
        if element.state['input_show_field_name']:
            if element.panel.active_element_index == element.panel.elements.index(element):
                if element.input_handler.multichar_input_active:
                    field_name_str = colorize(f'{element.name}:', color='cyan', effects=['bold', 'inverse'])
                else:
                    field_name_str = colorize(f'{element.name}:', color='white', effects=['bold', 'inverse'])
            else:
                field_name_str = colorize(f'{element.name}:', color='white', effects=['bold'])
        else:
            field_name_str = ''
        
        lines = list()
        current_line = list()
        line_index = 0
        for i in range(0, len(element.state['value'])):
            # figure out the color and effects to apply to this specific char
            if element.panel.active_element_index == element.panel.elements.index(element):
                if element.input_handler.multichar_input_active:  # we are actively editing, so use cyan and bold
                    if i == element.state['cursor_pos']:
                        color_char = colorize(element.state['value'][i], color='cyan', effects=['bold', 'underline', 'inverse'])
                    else:
                        color_char = colorize(element.state['value'][i], color='cyan', effects=['bold', 'underline'])
                else:  # not actively editing, so stay white, and don't show the cursor char
                    color_char = colorize(element.state['value'][i], color='white', effects=['underline'])
            else:
                color_char = colorize(element.state['value'][i], color='white', effects=['underline'])
            if line_index < element.state['input_width']:
                # we have room on this line, so add it
                if element.panel.active_element_index == element.panel.elements.index(element):
                    if i == element.state['cursor_pos']:
                        current_line.append(color_char)
                    else:
                        current_line.append(color_char)
                else:
                    current_line.append(color_char)
                line_index += 1
            else:
                # append current_line to lines, make a new current_line, add the current char to it
                lines.append(deepcopy(current_line))
                current_line = list()
                current_line.append(color_char)
                line_index = 1
        lines.append(deepcopy(current_line))
               
        num_lines = int(len(element.state['value']) / element.state['input_width']) + 1
        if num_lines >= element.state['input_height']:
            # we need to figure out what line to start the display on
            cursor_line = int(element.state['cursor_pos'] / element.state['input_width'])
            if cursor_line == 0:
                start_line = 0
            elif cursor_line == 1:
                start_line = 0
            else:
                start_line = 2
        else:
            start_line = 0

        y_index = 0
        if element.state['input_show_field_name']:
            element.panel.print_to_pos(element.top_left_x, element.top_left_y, field_name_str)
            y_index += 2

        # fill the whole area with underlined spaces
        for i in range(element.top_left_x, element.top_left_x + element.state['input_width']):
            for j in range(element.top_left_y, element.top_left_y + element.state['input_height']):
                if element.panel.active_element_index == element.panel.elements.index(element) and element.input_handler.multichar_input_active:
                    element.panel.print_to_pos(i, j + y_index, colorize(' ', color='cyan', effects=['bold', 'underline']))
                else:
                    element.panel.print_to_pos(i, j + y_index, colorize(' ', color='white', effects=['underline']))
        
        # draw the chars over the underlines spaces by walking the lines
        x_index = 0
        panel.tui.log(f'Will draw {len(lines)} lines')
        if element.state['input_height'] >= 2:
            end_line = start_line + element.state['input_height'] - 2
        else:
            end_line = start_line + 1
        for line in lines[start_line:end_line]:
            for char in line:
                element.panel.print_to_pos(x_index + element.top_left_x, y_index + element.top_left_y, char)
                x_index += 1
            y_index += 1
            x_index = 0

        # if we're editing and the cursor is at the end of the text, draw the cursor separately because life's a shit
        if element.input_handler.multichar_input_active and element.state['cursor_pos'] == len(element.state['value']):
            cursor_y = int(element.state['cursor_pos'] / element.state['input_width'])
            cursor_x = element.state['cursor_pos'] - cursor_y * element.state['input_width']
            if element.state['input_show_field_name']:
                offset = 2
            else:
                offset = 0
            element.panel.print_to_pos(cursor_x + element.top_left_x, cursor_y + element.top_left_y + offset, colorize(' ', color='cyan', effects=['inverse', 'underline', 'bold']))

    def input_edit_hotkey_func(input_handler):
        panel.tui.log(f'{input_handler.element.panel.name}::{input_handler.element.name}::Edit hotkey pressed')
        if not input_handler.multichar_input_active:
            input_handler.multichar_input_active = True
            input_handler.multichar_input_buffer = input_handler.element.state['value']
            input_handler.multichar_input_max_size = input_handler.element.state['input_max_size']
            input_handler.multichar_input_allowed_chars = element.state['allowed_chars']
            input_handler.element.redraw_requested = True
        else:
            return True

    def input_multichar_update_func(input_handler, value, c):
        panel.tui.log(f'{input_handler.element.panel.name}::{input_handler.element.name}::Input char received to multiline input: {c} with cursor pos {input_handler.element.state["cursor_pos"]}')
        if input_handler.element.state['cursor_pos'] == len(input_handler.element.state['value']):  # we're at the end so append to the end
            input_handler.element.state['value'] += c
        else:
            input_handler.element.state['value'] = input_handler.element.state['value'][0:input_handler.element.state['cursor_pos']] + c + input_handler.element.state['value'][input_handler.element.state['cursor_pos']:]
        input_handler.element.state['cursor_pos'] += 1
        if input_handler.element.state['cursor_pos'] >= input_handler.element.state['input_max_size']:
            input_handler.element.state['cursor_pos'] = input_handler.element.state['input_max_size'] - 1
        input_handler.element.redraw_requested = True


    def input_multichar_save_func(input_handler, value):
        panel.tui.log(f'{input_handler.element.panel.name}::{input_handler.element.name}::Saved value {value}')
        input_handler.element.state['value'] = value
        input_handler.multichar_input_active = False
        input_handler.element.redraw_requested = True
        input_handler.element.state['on_save'](input_handler, value)

    def up_arrow_handler(input_handler):
        panel.tui.log(f'{input_handler.element.panel.name}::{input_handler.element.name}::Up arrow pressed')
        current_pos = input_handler.element.state['cursor_pos']
        if current_pos < input_handler.element.state['input_width']:  # we're on the top line, do nothing
            return
        new_pos = current_pos - input_handler.element.state['input_width'] + 1
        input_handler.element.state['cursor_pos'] = new_pos
        input_handler.element.redraw_requested = True

    def down_arrow_handler(input_handler):
        panel.tui.log(f'{input_handler.element.panel.name}::{input_handler.element.name}::Down arrow pressed')
        current_pos = input_handler.element.state['cursor_pos']
        current_line_pos = int(current_pos / input_handler.element.state['input_width']) + 1
        num_lines = int(len(input_handler.element.state['value']) / input_handler.element.state['input_width']) + 1
        if current_line_pos == num_lines:  # we're already at the bottom, do nothing
            return
        new_pos = current_pos + input_handler.element.state['input_width'] - 1
        input_handler.element.state['cursor_pos'] = new_pos
        input_handler.element.redraw_requested = True

    def right_arrow_handler(input_handler):
        panel.tui.log(f'{input_handler.element.panel.name}::{input_handler.element.name}::Right arrow pressed')
        current_pos = input_handler.element.state['cursor_pos']
        new_pos = current_pos + 1
        if new_pos > len(input_handler.element.state['value']):
            new_pos = len(input_handler.element.state['value']) 
        input_handler.element.state['cursor_pos'] = new_pos
        input_handler.element.redraw_requested = True

    def left_arrow_handler(input_handler):
        panel.tui.log(f'{input_handler.element.panel.name}::{input_handler.element.name}::Left arrow pressed')
        current_pos = input_handler.element.state['cursor_pos']
        new_pos = current_pos - 1
        if new_pos < 0:
            new_pos = 0
        input_handler.element.state['cursor_pos'] = new_pos
        input_handler.element.redraw_requested = True

    def backspace_handler(input_handler):
        panel.tui.log(f'{input_handler.element.panel.name}::{input_handler.element.name}::Backspace pressed')
        current_pos = input_handler.element.state['cursor_pos']
        if current_pos == len(input_handler.element.state['value']):  # we are at the end of the input, so delete from the end
            input_handler.element.state['value'] = input_handler.element.state['value'][:-1]
        else:  # we need to remove the item at the current cursor pos
            input_handler.element.state['value'] = input_handler.element.state['value'][0:current_pos] + input_handler.element.state['value'][current_pos + 1:]
        new_pos = current_pos - 1
        if new_pos < 0:
            new_pos = 0
        input_handler.element.state['cursor_pos'] = new_pos
        input_handler.element.redraw_requested = True

    def delete_handler(input_handler):
        panel.tui.log(f'{input_handler.element.panel.name}::{input_handler.element.name}::Delete pressed')
        current_pos = input_handler.element.state['cursor_pos']
        if current_pos == len(input_handler.element.state['value']):  # we are at the end of the input, so delete from the end
            input_handler.element.state['value'] = input_handler.element.state['value'][:-1]
            new_pos = current_pos - 1
        else:  # we need to remove the item at the current cursor pos
            input_handler.element.state['value'] = input_handler.element.state['value'][0:current_pos] + input_handler.element.state['value'][current_pos + 1:]
            new_pos = current_pos
        input_handler.element.state['cursor_pos'] = new_pos
        input_handler.element.redraw_requested = True

    element.content_func = multiline_input_field_content_func
    element.input_handler.hotkeys['\n'] = input_edit_hotkey_func
    element.input_handler.hotkeys['\x1b[A'] = up_arrow_handler
    element.input_handler.hotkeys['\x1b[B'] = down_arrow_handler
    element.input_handler.hotkeys['\x1b[C'] = right_arrow_handler
    element.input_handler.hotkeys['\x1b[D'] = left_arrow_handler
    element.input_handler.hotkeys['\x7f'] = backspace_handler
    element.input_handler.hotkeys['\x1b[3~'] = delete_handler
    element.input_handler.multichar_input_update_callback_func = input_multichar_update_func
    element.input_handler.multichar_input_end_callback_func = input_multichar_save_func

    return element