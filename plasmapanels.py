from termytui.tui import Tui
from termytui.utils import average
from termytui.termy.termy import colorize, colortext
from termytui import status_widgets, element_widgets
import time
import math
import random
import threading


def plasma(w, h, xf, yf, sleep, character, modestring, layer):
  mycolors = ['cyan', 'blue', 'green', 'yellow', 'red', 'magenta', 'white']
  styles = []
  for color in mycolors:
        styles.append((color, True))
        styles.append((color, False))
  for color in list(reversed(mycolors)):
        styles.append((color, False))
        styles.append((color, True))

  while tt.render_enabled:
    timebit = time.time()
    for x in range(1, w + 1):
      for y in range(1, h + 1):
        v = 0
        scalex = float(x) / float(w) * xf
        scaley = float(y) / float(h) * yf
        if 'a' in modestring:
          v += math.sin(scalex * 10 + timebit)
        if 'b' in modestring:
          v += math.sin(10 * (scalex * math.sin(timebit / 2) + scaley * math.cos(timebit / 3)) + timebit)
        if 'c' in modestring:
          cx = scalex + 0.5 * math.sin(timebit)
          cy = scaley + 0.5 * math.cos(timebit)
          v += math.sin(math.sqrt(100*(cx ** 2  + cy ** 2) + 1) + timebit)
        if 'd' in modestring:
          cx = scalex + 0.9 * math.cos(timebit)
          cy = scaley + 0.8 * math.sin(timebit)
          v += math.sin(math.sqrt(abs(100 * (cx ** 3  + cy ** 3) + 1)) + timebit)
        if 'e' in modestring:
          v += math.sqrt(abs(math.sin(scalex + scaley * timebit)))
        if 'f' in modestring:
          v += math.sin(math.tan((scalex * scaley)) + timebit)
        v = int(v * 7) % 28
        layer.points[(x, y)] = colortext(character, styles[v][0], False, styles[v][1])
    time.sleep(sleep)


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


def null_content_func(panel):
    pass


def mode_picker():
    num_modes = random.randrange(1, 6)
    modes = ['a', 'b', 'c', 'd', 'e', 'f']
    mode = ''
    for i in range(0, num_modes):
        mode += random.choice(modes)
    return mode

if __name__ == '__main__':
    tt = Tui()
    tt.log('Plasma Panels demo starting!')

    term_size_indicator = status_widgets.term_size(tt)
    frametime_indicator = status_widgets.last_frametime(tt)
    framerate_avg_indicator = status_widgets.framerate(tt)
    cell_change_stats_indicator = status_widgets.cell_change_stats(tt)
    char_volume_stats_indicator = status_widgets.char_volume_stats(tt)

    for x in range(0, tt.screen_width):
       for y in range(0, tt.screen_height):
          tt.background_layer.points[(x, y)] = colorize(' ', 'white', bg_color='blue')

    num_panels = 10

    chars = ['.', '-', '#', 'o', 'O', '*', '_', '@', '`', '+', '|', '~', ':', '^', '%', '&']

    # panel = tt.create_panel(tt.screen_width - 3, tt.screen_height - 3, name='plasma', border=False)
    # panel.move(1,1)
    # panel.content_func = null_content_func
    # t = threading.Thread(target=plasma, args=(tt.screen_width - 2, tt.screen_height - 2, 0.5, 0.5, 0.033, '#', 'acf', panel.layer))
    # t.start()

    graphpanel = tt.create_panel(int(tt.screen_width / 4), int(tt.screen_height / 2) + 2, name='graph', border=True)
    graphpanel.move(int(tt.screen_width / 4) * 3 - 1, 1)
    graphpanel.content_func = null_content_func

    cells_avg_hist = list()
    cells_avg_max = 120
    def el5_data_func():
        global cells_avg_hist
        cells_avg_hist.append(average(tt.display.cells_history))
        if len(cells_avg_hist) > cells_avg_max:
           cells_avg_hist = cells_avg_hist[-1 * cells_avg_max:]
        return cells_avg_hist
    
    el5 = element_widgets.basic_line_chart_element(graphpanel, 'graph', graphpanel.x_size - 2, int(graphpanel.y_size / 3), el5_data_func, x_axis_title='Time', y_axis_title='Avg Cells', top_left_y=1)
   

    chars_avg_hist = list()
    chars_avg_max = 120
    def el6_data_func():
       global chars_avg_hist
       chars_avg_hist.append(average(tt.display.chars_history))
       if len(chars_avg_hist) > chars_avg_max:
          chars_avg_hist = chars_avg_hist[-1 * chars_avg_max:]
       return chars_avg_hist
    
    el6 = element_widgets.basic_line_chart_element(graphpanel, 'graph', graphpanel.x_size - 2, int(graphpanel.y_size / 3), el6_data_func, x_axis_title='Time', y_axis_title='Avg Chars', line_color='blue', top_left_y=int(graphpanel.y_size / 3) + 1)
    

    fps_avg_hist = list()
    fps_avg_max = 120
    def el7_data_func():
       global fps_avg_hist
       fps_avg_hist.append(1 / average(tt.frame_time_hist))
       if len(fps_avg_hist) > fps_avg_max:
          fps_avg_hist = fps_avg_hist[-1 * fps_avg_max:]
       return fps_avg_hist
    
    el7 = element_widgets.basic_line_chart_element(graphpanel, 'graph', graphpanel.x_size - 2, int(graphpanel.y_size / 3), el7_data_func, x_axis_title='Time', y_axis_title='Avg FPS', line_color='magenta', top_left_y=int(graphpanel.y_size / 3) * 2 + 1)
    
    for i in range(1, num_panels + 1):
        w = int(random.random() * 70 + 5)
        h = int(random.random() * 20 + 5)
        x_loc = random.randrange(0, tt.screen_width - w)
        y_loc = random.randrange(0, tt.screen_height - h)
        panel = tt.create_panel(w, h, name=f'Plasma Panel {i}', border=False)
        panel.content_func = null_content_func
        panel.move(x_loc, y_loc)
        panel.set_z_pos(i)
        t = threading.Thread(target=plasma, args=(w, h, random.random(), random.random(), 0.05, random.choice(chars), mode_picker(), panel.layer))
        t.start()
        if i % 1 == 0:
            pt = threading.Thread(target=pb_thread_func, args=(panel,))
            pt.start()
