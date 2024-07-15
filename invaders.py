from termytui.tui import Tui
from termytui.utils import null_content_func
from termytui.termy.termy import colorize, control_chars
from termytui import status_widgets, panel_widgets
from copy import deepcopy
import threading
import time
import random

fgcolors = list(control_chars['fgcolor'].keys())
fgcolors.remove('black')

background = [
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '                                                                                                                                                     ',
            '      .                                                                                                                                              ',
            '      |                                  (_)                                                                                                         ',
            '   ___|___           +-------------\    % | %         ______________             |                                                                   ',
            '  / - - - |       @  | ]       ]    \   | | |    /\   \____//______/    ____  /--+--\    | | |                      (-                 ___________   ',
            ' | - - - -|       |  |  ]       ]    \  |/_\|   / o\   \==//=|     |   ||| ||    |        \|/           .          /           +      ( =  =  =  =)  ',
            '  \o - - /        +--|   ]       ]    \ /===\  / o o\   \//- | [   |   | || |    |     ____|____________|__________|           |\    (             ) ',
            '   \ -O /            |    ]       ]    | (|) |/ o  o \   | - | [   |___|| |||    |    /  ________________________  \  |^^^^^|  | \  ( =  =  =  =  = )',
            '    | ||        ____/______]_      ]   |  |  | o  o  o\__| - | [   |  / || ||\   |   /  |           )            |  \/| . . |--+  \(                 ',
            '    | ||       /  _|__|______|      ]  |  |  |  o   o    \ - | [   |_/|| || |#\  |  /   |           )            |   \| . . |  |   \ =  =  =  =  =  =',
            '___/__||\_____/__/_|__|__|__|]_______]_|__|__|____________\__|_____||||||||||##\_|_/____|___________)____________|____\_____|__|____\________________'
        ]


class EnemyGrid():
    def __init__(self, game, rows, columns):
        self.game = game
        self.panel = game.panel
        self.rows = rows
        self.columns = columns

        self.enemy_x_gap = 15
        self.enemy_y_gap = 5
        self.top_left_x = 15
        self.top_left_y = 5

        self.enemy_sprites = list()
        self.spriteflip = True
        self.time_last_moved = time.time()
        self.move_wait_time = 1
        self.move_wait_time_adjust_factor = 0.85
        self.move_dir = 1  # 1 = move right, -1 = move left
        self.x_stop_left = 10
        self.x_stop_right = 145
        self.y_stop = 39

        self.enemy_missiles = list()
        self.max_enemy_missiles = 2
        self.missile_fire_chance_per_frame = 0.05
        self.missile_move_frame_interval = 3
        
        self.reached_shields = False

        self.enemy_sprites.append([
            [
                '|-|-|',
                ' \\|/ ',
                '// \\\\'
            ],
            [
                '|-|-|',
                '-\\|/-',
                '|| ||'
            ]
        ])

        self.enemy_sprites.append([
            [
                '<-|->',
                '|## |',
                '+|||+'
            ],
            [
                '<--->',
                '| ##|',
                '-/|\\-'
            ]
        ])

        self.enemy_sprites.append([
            [
                ' ___ ',
                '(===)',
                ' /+\\ '
            ],
            [
                ' ___ ',
                '()=()',
                ' /+\\ '
            ]
        ])

        self.enemy_sprites.append([
            [
                '|ooo|',
                '\\ o /',
                ' |_/ '
            ],
            [
                '|***|',
                '\\ * /',
                ' \\_| '
            ]
        ])

        self.enemy_sprites.append([
            [
                '/@-@\\',
                '|-@-|',
                '/|||\\'
            ],
            [
                '/-@-\\',
                '|@-@|',
                '\\|||/'
            ]
        ])

        self.enemy_death_sprites = [
            [
                ' \\;/ ',
                '--*--',
                '`/\'\\\''
            ],
            [
                ' (#) ',
                '(&%*)',
                ' *&) '
            ],
            [
                '  |  ',
                '--*--',
                '  |  '
            ],
            [
                '     ',
                '  *  ',
                '     '
            ]
        ]

        self.grid = list()
        for i in range(0, self.rows):
            self.grid.append(list())
            for j in range(0, self.columns):
                self.grid[i].append(Enemy())

        self.init_finished = True

    def fire_missile(self):
        if len(self.enemy_missiles) >= self.max_enemy_missiles:
            return  # do nothing if there's already a bunch of missiles
        if random.random() < self.missile_fire_chance_per_frame:
            # pick which enemy to fire. the bottom-most enemy in each column is a candidate
            lowest_per_col = dict()
            for i in range(0, len(self.grid)):  
                for j in range(0, len(self.grid[0])):
                    if self.grid[i][j].alive:
                        lowest_per_col[j] = i
            col_to_fire = random.choice([x for x in lowest_per_col.keys()])
            new_missile_x_pos = self.top_left_x + (col_to_fire * self.enemy_x_gap) + 2   # +2 puts us at the mid point of the sprite
            new_missile_y_pos = self.top_left_y + (lowest_per_col[col_to_fire] * self.enemy_y_gap) + 3  # +3 puts us just below the sprite
            self.enemy_missiles.append([new_missile_x_pos, new_missile_y_pos])

    def update_missiles(self):
        if len(self.enemy_missiles) == 0:
            return  # bail fast if no missiles
        to_remove = list()
        for m in self.enemy_missiles:
            # move the missile down by 1
            m[1] += 1
            # check collision with shields
            if self.game.check_shield_collision(m[0], m[1]):
                to_remove.append(m)
            # check collision with the player
            elif self.game.check_player_collision(m[0], m[1]):
                to_remove.append(m)
            elif m[1] >= 49:  # hit the bottom without colliding with anything
                to_remove.append(m)
        for m in to_remove:
            self.enemy_missiles.remove(m)

    def count_alive(self):
        count = 0
        for i in range(0, len(self.grid)):
            for j in range(0, len(self.grid[i])):
                if self.grid[i][j].alive:
                    count += 1
        return count

    def move(self):
        if time.time() - self.time_last_moved > self.move_wait_time:
            if self.move_wait_time < self.game.tick_interval:
                if self.count_alive() > 1:
                    self.top_left_x += self.move_dir * 2
                else:
                    self.top_left_x += self.move_dir * 3
            else:
                self.top_left_x += self.move_dir
            if self.top_left_x <= self.x_stop_left:
                self.top_left_x = self.x_stop_left
                self.move_dir = self.move_dir * -1
                self.top_left_y += 1
            if self.top_left_x + (self.columns * self.enemy_x_gap) >= self.x_stop_right:
                self.move_dir = self.move_dir * -1
                self.top_left_y += 1
            self.spriteflip = not self.spriteflip
            self.time_last_moved = time.time()
            if not self.reached_shields and self.top_left_y + self.rows * self.enemy_y_gap >= self.game.shield_y_top_pos + 3:  # reached the top of the shields
                self.game.tui.log('Hit top of shields')
                self.game.remove_shields()
                self.reached_shields = True
            if self.top_left_y + self.rows * self.enemy_y_gap >= self.game.shield_y_top_pos + 8:  # reached the player
                self.game.tui.log('Hit player')
                self.game.end_game()
        if self.game.tick_count % self.missile_move_frame_interval == 0:
            self.update_missiles()
            self.fire_missile()
    
    def check_enemy_collision(self, x, y):
        # is it within the grid boundaries at all?
        if x < self.x_stop_left or x > self.x_stop_right or y > self.y_stop:
            return False
        bottom_right_x = self.top_left_x + (self.columns * self.enemy_x_gap) + 5
        bottom_right_y = self.top_left_y + (self.rows * self.enemy_y_gap) + 3
        if x < self.top_left_x or x > bottom_right_x or y < self.top_left_y or y > bottom_right_y:
            return False
        # iterate over the enemies to check collision
        for i in range(0, self.rows):
            for j in range(0, self.columns):
                if self.grid[i][j].alive:
                    enemy_top_left_x = self.top_left_x + (j * self.enemy_x_gap)
                    enemy_top_left_y = self.top_left_y + (i * self.enemy_y_gap)
                    if enemy_top_left_x <= x <= enemy_top_left_x + 5 and enemy_top_left_y <= y <= enemy_top_left_y + 3:
                        self.grid[i][j].die()
                        self.move_wait_time = self.move_wait_time_adjust_factor * self.move_wait_time
                        return True
    
    def render_missiles(self):
        for m in self.enemy_missiles:
            color = random.choice(fgcolors)
            self.panel.print_to_pos(m[0], m[1], colorize('|', color, effects=['bold']))

        
    def render_grid(self):
        self.consolidate()
        for i in range(0, self.rows):
            for j in range(0, self.columns):
                if self.grid[i][j].alive:
                    if j % 2 == 0:
                        effective_spriteflip = self.spriteflip
                    else:
                        effective_spriteflip = not self.spriteflip
                    if effective_spriteflip:
                        sprite = self.enemy_sprites[i % len(self.enemy_sprites)][0]
                    else:
                        sprite = self.enemy_sprites[i % len(self.enemy_sprites)][1]
                    color = fgcolors[i % len(fgcolors)]
                    for y in range(0, 3):
                        for x in range(0, 5):
                            x_pos = self.top_left_x + (j * self.enemy_x_gap) + x
                            y_pos = self.top_left_y + (i * self.enemy_y_gap) + y
                            self.panel.print_to_pos(x_pos, y_pos, colorize(sprite[y][x], color, effects=['bold']))
                elif not self.grid[i][j].alive and not self.grid[i][j].removed:
                    color = fgcolors[i % len(fgcolors)]
                    sprite = self.enemy_death_sprites[self.grid[i][j].destroy_anim_frame_count]
                    for y in range(0, 3):
                        for x in range(0, 5):
                            x_pos = self.top_left_x + (j * self.enemy_x_gap) + x
                            y_pos = self.top_left_y + (i * self.enemy_y_gap) + y
                            self.panel.print_to_pos(x_pos, y_pos, colorize(sprite[y][x], color, effects=['bold']))
                    self.grid[i][j].destroy_anim_frame_count += 1
                    if self.grid[i][j].destroy_anim_frame_count >= len(self.enemy_death_sprites):
                        self.grid[i][j].removed = True

    def consolidate(self):
        if not self.init_finished or len(self.grid) == 0:
            return
        
        # can the bottom row be removed?
        if len(self.grid[-1]) == len([x for x in self.grid[-1] if x.removed]):
            self.grid.pop(-1)
            self.rows -= 1
            self.game.tui.log('Removing bottom grid row')
        # can the leftmost or rightmost columns be removed?
        num_left_alive = 0
        num_right_alive = 0
        for i in range(0, self.rows):
            if i < len(self.grid) and len(self.grid[i]) > 0:
                if not self.grid[i][0].removed:
                    num_left_alive += 1
                if not self.grid[i][-1].removed:
                    num_right_alive += 1
        if num_left_alive == 0:  # we can trim the left column
            for i in range(0, self.rows):
                if len(self.grid[i]) > 0:
                    self.grid[i].pop(0)
            self.columns -= 1
            self.top_left_x += self.enemy_x_gap
            self.game.tui.log('Removing leftmost column')
        if num_right_alive == 0:  # we can trim the right column
            for i in range(0, self.rows):
                if len(self.grid[i]) > 0:
                    self.grid[i].pop(-1)
            self.columns -= 1
            self.game.tui.log('Removing rightmost column')
        if self.columns <= 0 and self.rows <= 0:  # everything has been removed, which probably means everything is dead
            self.game.win_round()
            return
        


class Enemy():
    def __init__(self):
        self.alive = True
        self.removed = False
        self.destroy_anim_frame_count = 0

    def die(self):
        self.alive = False
        


class GameController():
    def __init__(self):
        self.tui = Tui()

        self.game_mode = 'not_in_game'

        self.log_panel = panel_widgets.tui_log_panel(self.tui, width=int(self.tui.screen_width * 0.25), height=50)
        self.clock = status_widgets.clock(self.tui)
        self.fps = status_widgets.framerate(self.tui)
        self.game_status = self.tui.create_status_element('game status', self.game_status_line)
    
        self.panel = self.tui.create_panel(150, 50, 'Invaders Game', border=True)
        self.tui.selected_panel_index = 1
        self.panel.move(1, 1)
        self.panel.content_func = null_content_func
        self.panel.input_handler.input_fallback = null_content_func
        self.panel.input_handler.hotkeys['d'] = self.move_player_right
        self.panel.input_handler.hotkeys['D'] = self.move_player_right_2
        self.panel.input_handler.hotkeys['a'] = self.move_player_left
        self.panel.input_handler.hotkeys['A'] = self.move_player_left_2
        self.panel.input_handler.hotkeys[' '] = self.player_shoot
        self.panel.input_handler.hotkeys['\n'] = self.start_game

        self.tick_interval = 0.0166
        self.tui.frame_sleep_time = self.tick_interval
        self.tick_count = 0

        self.round_win_wait_time = 10
        self.round_win_wait_start_time = 0

        self.player_y_top_pos = 47

        self.player_x = 75

        self.game_running = True

        self.player_missile_active = False
        self.player_missile_x_pos = 0
        self.player_missile_y_pos = 0

        self.enemies_destroyed = 0
        self.game_level = 1

        self.shield_y_top_pos = 40
        self.shield_x_top_pos = 20
        self.shield_gap = 20
        self.shield_height = 3
        self.shield_width = 6
        self.num_shields = 6
        self.shields = list()

        self.game_reset()

        self.game_thread = threading.Thread(target=self.game_thread_runner, daemon=True)
        self.game_thread.start()

    def game_reset(self):
        self.player_x = 75
        self.player_missile_active = False
        self.enemies_destroyed = 0
        self.game_level = 1
        self.init_shields()
        self.grid = EnemyGrid(self, 5, 6)

    def new_round(self):
        self.game_level += 1
        self.player_x = 75
        self.player_missile_active = False
        self.init_shields()
        self.grid = EnemyGrid(self, 5, 6)

        # leveling difficulty goes here

        self.grid.move_wait_time = 1 - (0.01 * self.game_level)
        self.grid.move_wait_time_adjust_factor = 0.85 - (0.01 * self.game_level)
        self.grid.max_enemy_missiles = 2 + int(self.game_level / 3)

        self.game_mode = 'game_running'

    def win_round(self):  # to be called when all enemies are destroyed
        self.tui.log('All enemies destroyed! Player has won the round!')
        self.round_win_wait_start_time = time.time()
        self.game_mode = 'round_win_wait'

    def start_game(self):
        self.game_reset()
        self.game_mode = 'game_running'
        del(self.panel.input_handler.hotkeys['\n'])

    def end_game(self):
        self.tui.log('end_game called')
        self.game_mode = 'game_over'
        self.panel.input_handler.hotkeys['\n'] = self.start_game


    def game_status_line(self):
        return (f'Grid: {self.grid.columns} cols x {self.grid.rows} rows  Move: {self.grid.move_wait_time:.3f}s  Destroyed: {self.enemies_destroyed} Level: {self.game_level}')

    def init_shields(self):
        self.shields = list()
        shield = [
            [False, False, True, True, False, False],
            [False, True, True, True, True, False],
            [True, True, True, True, True, True]
        ]
        for i in range(0, self.num_shields):
            self.shields.append(deepcopy(shield))

    def remove_shields(self):
        for s in range(0, self.num_shields):
            for x in range(0, self.shield_width):
                for y in range(0, self.shield_height):
                    self.shields[s][y][x] = False


    def check_player_collision(self, x_pos, y_pos):
        if y_pos < self.player_y_top_pos:
            return False  # Cannot intersect if we're not on the rows where the player exists
        player_bottom_right_x = self.player_x + 4
        player_bottom_right_y = self.player_y_top_pos + 2
        if self.player_x <= x_pos <= player_bottom_right_x and self.player_y_top_pos <= y_pos <= player_bottom_right_y:  # this should be a collision
            self.end_game()
            return True

    def check_shield_collision(self, x_pos, y_pos):
        if y_pos < self.shield_y_top_pos or y_pos > self.shield_y_top_pos + 2:
            return False  # Cannot intersect if we're not on the rows where the shields exist
        for s in range(0, self.num_shields):
            shield_top_left_x = s * self.shield_gap + self.shield_x_top_pos
            for y in range(0, self.shield_height):
                for x in range(0, self.shield_width):
                    this_x = shield_top_left_x + x
                    this_y = self.shield_y_top_pos + y
                    if self.shields[s][y][x] and this_x == x_pos and this_y == y_pos:  # this should be a collision
                        self.shields[s][y][x] = False
                        return True

    def player_shoot(self):
        if self.player_missile_active:
            return  # we don't want to do anything if a missle is already in flight
        self.player_missile_active = True
        self.player_missile_x_pos = self.player_x + 2  # + 2 to get to the middle of the 5-wide player sprite
        self.player_missile_y_pos = self.player_y_top_pos

    def update_player_missile(self):
        if not self.player_missile_active:
            return  # do nothing if we were called while the missile is not active
        self.player_missile_y_pos -= 1
        if self.player_missile_y_pos < 2:  # we've gone off the top of the screen
            self.player_missile_active = False
        if self.check_shield_collision(self.player_missile_x_pos, self.player_missile_y_pos):
            self.player_missile_active = False
        if self.grid.check_enemy_collision(self.player_missile_x_pos, self.player_missile_y_pos):
            self.player_missile_active = False
            self.enemies_destroyed += 1

    def move_player_left_2(self):
        self.move_player_left(spaces=2)

    def move_player_left(self, spaces=1):
        self.player_x -= spaces
        if self.player_x < 1:
            self.player_x = 1

    def move_player_right_2(self):
        self.move_player_right(spaces=2)
    
    def move_player_right(self, spaces=1):
        self.player_x += spaces
        if self.player_x > 145:
            self.player_x = 145

    def game_thread_runner(self):
        while self.game_running:
            self.tick()
            time.sleep(self.tick_interval)

    def tick(self):
        if self.game_mode == 'game_running':
            self.grid.move()
            if self.player_missile_active:
                self.update_player_missile()
        elif self.game_mode == 'round_win_wait':
            if time.time() - self.round_win_wait_start_time > self.round_win_wait_time:
                self.new_round()
        self.render_game()
        self.tick_count += 1

    def clear_panel(self):
        self.panel.blank(char=' ')

    def render_game_over_screen(self):
        self.clear_panel()
        self.draw_background()
        self.panel.create_border()
        title_line_1 = [
            ' ####    ###    #   #   #####',
            '#       #   #   ## ##   #    ',
            '#  ##   #####   # # #   ###  ',
            '#   #   #   #   #   #   #    ',
            ' ###    #   #   #   #   #####'
        ]
        title_line_2 = [
            ' ###    #   #   #####   #### ',
            '#   #   #   #   #       #   #',
            '#   #   #   #   ###     #### ',
            '#   #    # #    #       #   #',
            ' ###      #     #####   #   #'
        ]
        message = [
            f'Final level: {self.game_level}',
            f'Total kills: {self.enemies_destroyed}',
            f'',
            f'Press Enter to start a new game',
            f'Thanks for playing!'
        ]

        line_1_top_x = int((150 - len(title_line_1[0])) / 2)
        line_2_top_x = int((150 - len(title_line_2[0])) / 2)
        line_1_top_y = 10
        line_2_top_y = 20
        for i in range(0, len(title_line_1)):
            self.panel.print_to_pos(line_1_top_x, line_1_top_y + i, colorize(title_line_1[i], 'red', effects=['bold']))
            self.panel.print_to_pos(line_2_top_x, line_2_top_y + i, colorize(title_line_2[i], 'red', effects=['bold']))
            self.panel.print_to_pos(int((150 - len(message[i])) / 2), 30 + i, colorize(message[i], 'magenta', effects=['bold']))

    def render_round_win_screen(self):
        self.clear_panel()
        self.draw_background()
        self.panel.create_border()
        title_line = [
            ' ####    ###    #   #    ####   ####     ###    #####   #   #   #        ###    #####   #####    ###    #   #    ####   ##',
            '#       #   #   ##  #   #       #   #   #   #     #     #   #   #       #   #     #       #     #   #   ##  #   #       ##',
            '#       #   #   # # #   #  ##   ####    #####     #     #   #   #       #####     #       #     #   #   # # #    ###    ##',
            '#       #   #   #  ##   #   #   #   #   #   #     #     #   #   #       #   #     #       #     #   #   #  ##       #      ',
            ' ####    ###    #   #    ###    #   #   #   #     #      ###    #####   #   #     #     #####    ###    #   #   ####    ##'
        ]
        message = [
            'You have won the round!',
            '',
            f'Total kills: {self.enemies_destroyed}',
            '',
            f'The next round will start in {10 - (time.time() - self.round_win_wait_start_time):.0f} seconds'
        ]
        title_top = 15
        message_top = 25
        title_top_x = int((150 - len(title_line[0])) / 2)

        for i in range(0, len(title_line)):
            self.panel.print_to_pos(title_top_x, title_top + i, colorize(title_line[i], 'cyan', effects=['bold']))
            self.panel.print_to_pos(int((150 - len(message[i])) / 2), message_top + i, colorize(message[i], 'magenta', effects=['bold']))

    def render_start_screen(self):
        self.clear_panel()
        self.draw_background()
        self.panel.create_border()
        title_line_1 = [
            ' ####  ####     ###     ####   #####',
            '#      #   #   #   #   #       #    ',
            ' ###   ####    #####   #       ###  ',
            '    #  #       #   #   #       #    ',
            '####   #       #   #    ####   #####'
        ]
        title_line_2 = [
            '#####   #   #   #   #    ###    ####    #####   ####     ####',
            '  #     ##  #   #   #   #   #   #   #   #       #   #   #    ',
            '  #     # # #   #   #   #####   #   #   ###     ####     ### ',
            '  #     #  ##    # #    #   #   #   #   #       #   #       #',
            '#####   #   #     #     #   #   ####    #####   #   #   ####'
        ]
        instructions = [
            'Press Enter to start the game',
            'Controls -',
            'a (A): Move left (2x)',
            'd (D): Move right (2x)',
            'space: Fire missile'
        ]

        
        line_1_top_x = int((150 - len(title_line_1[0])) / 2)
        line_2_top_x = int((150 - len(title_line_2[0])) / 2)
        line_1_top_y = 10
        line_2_top_y = 20
        for i in range(0, len(title_line_1)):
            self.panel.print_to_pos(line_1_top_x, line_1_top_y + i, colorize(title_line_1[i], 'green', effects=['bold']))
            self.panel.print_to_pos(line_2_top_x, line_2_top_y + i, colorize(title_line_2[i], 'blue', effects=['bold']))
            self.panel.print_to_pos(int((150 - len(instructions[i])) / 2), 30 + i, colorize(instructions[i], 'magenta', effects=['bold']))
        

    def render_game(self):
        if self.game_mode == 'not_in_game':
            self.render_start_screen()
        elif self.game_mode == 'round_win_wait':
            self.render_round_win_screen()
        elif self.game_mode == 'game_over':
            self.render_game_over_screen()
        elif self.game_mode == 'game_running':
            self.clear_panel()
            self.draw_background()
            self.panel.create_border()
            self.render_player(self.player_x)
            self.render_shields()
            self.grid.render_grid()
            self.grid.render_missiles()
            if self.player_missile_active:
                self.render_player_missile(self.player_missile_x_pos, self.player_missile_y_pos)

    def render_player(self, x_location):
        player_chars = [
            ' <^> ',
            ' /|\ ',
            '/_|_\\'
        ]
        player_color = 'magenta'
        for i in range(0, len(player_chars)):
            for j in range(0, len(player_chars[0])):
                self.panel.print_to_pos(x_location + j, self.player_y_top_pos + i, colorize(player_chars[i][j], player_color, effects=['bold']))
    
    def render_player_missile(self, x_location, y_location):
        missile_char = '|'
        color = fgcolors[int(time.time() * 1000) % len(fgcolors)]
        self.panel.print_to_pos(x_location, y_location, colorize(missile_char, color, effects=['bold']))

    def render_shields(self):
        shield_char = '#'
        shield_color = 'blue'
        for s in range(0, self.num_shields):
            shield_top_left_x = s * self.shield_gap + self.shield_x_top_pos
            for y in range(0, self.shield_height):
                for x in range(0, self.shield_width):
                    this_x = shield_top_left_x + x
                    this_y = self.shield_y_top_pos + y
                    if self.shields[s][y][x]:
                        self.panel.print_to_pos(this_x, this_y, colorize(shield_char, shield_color, effects=['bold']))

    def draw_background(self):
        for i in range(len(background)):
            if background[i] != '                                                                                                                                                     ':
                self.panel.print_to_pos(1, i, background[i])
            

if __name__ == '__main__':
    game = GameController()