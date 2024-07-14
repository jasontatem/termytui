# TermyTUI
## A pile of wrong decisions in the form of a terminal UI framework

### What?

A rather basic framework for putting characters on a terminal, with some simple constructs to make building terminal UIs easier.

### Why?

There's a lot of much better ones out there. I wrote this for 2 reasons, mostly:

1. To learn a lot more about interfacing with terminals
2. I don't want to learn someone else's giant pile of UI abstractions so I can use their TUI framework

If you're in the market for an actual usable TUI framework, you have better options, and I encourage you to use them instead of this garbage.

### Usage

1. Copy the contents of the "termytui" folder into your project. Or do something better with package management or something I don't care just make it resolvable by python
2. Install readchar: pip3 install readchar
3. At a minimum, import the Tui object from termytui.tui
4. Create UIPanels and fill them with UIElements. Use StatusElements to add items to the status line

### Hello World

    from termytui.tui import Tui

    tt = Tui()

    panel = tt.create_panel(20, 5, 'Hello')
    def content_func(panel):
        panel.print_to_pos(1, 1, 'Hello World!')
    panel.content_func = content_func

### Features

- Framebuffer-esque rendering (if you want you can completely ignore the UI stuff and just scribble on the buffer)
- UIPanel objects that can have their content defined directly, or can contain one or more UIElement objects
- UIPanels can be moved without affecting their contents
- UIPanels have Z depth and will be correctly rendered above/below other panels based
- Status line populated by StatusElement objects for displaying small bits of always-visible info
- Predefined widgets for input fields, simple graphs, status line elements
- Input handling with globally-defined handlers, then UIPanel and UIElement specific handlers
- Terminal resize detection
- Very little crap getting in your way
- Not caring much (at all) about tons of colors or sixel graphics or any of that mess

### Requirements

The only non-stdlib requirement is the [readchar](https://pypi.org/project/readchar/) module

### Standard Global Hotkeys

- Alt-Q: Quit
- Alt-Z: Full redraw, useful for resolving render errors
- Alt-N: Select the next UIPanel
- Alt-M: Move the currently selected UIPanel

### Standard Panel Hotkeys

- Alt-X: Close panel
- PgUp: Select prior UIElement
- PgDn: Select next UIElement

### Demos

All demos can be run from the root of the cloned repo. Just run python3 [demo].py

#### test_ui.py

This is my general playgorund for testing out features. Its contents can be tame or wild depending on what I was doing at the last commit

#### plasmapanels.py

Oldschool plasma effects applied to bouncing UIPanels

#### invaders.py

Space Invaders clone

#### titwste.py

TITWSTE Is The World's Shittiest Text Editor. Extremely minimal text editor