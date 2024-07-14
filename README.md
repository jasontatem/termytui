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
2. At a minimum, import the Tui object from termytui.tui
3. Create UIPanels and fill them with UIElements. Use StatusElements to add items to the status line

### Hello World

from termytui.tui import Tui

tt = Tui()

panel = tt.create_panel(20, 5, 'Hello')
def content_func(panel):
    panel.print_to_pos(1, 1, 'Hello World!')
panel.content_func = content_func